import fs from 'node:fs';
import path from 'node:path';
import { loadSkeleton, referenceScale, sampleAnimation, sampleTransition, finiteNumber } from './runtime.mjs';
import { analyzeSample, DEFAULT_THRESHOLDS } from './metrics.mjs';

export function validateOptions(options) {
  finiteNumber(options.fps, 'fps', { min: 1, max: 1000 });
  if (!['none', 'update'].includes(options.physics)) throw new Error('physics must be none or update.');
  for (const key of ['bones', 'ignoreBones', 'slots', 'ignoreSlots']) if (options[key]) new RegExp(options[key]);
  if (options.scale !== undefined) finiteNumber(options.scale, 'scale', { min: 1e-9 });
  finiteNumber(options.meshVertices, 'meshVertices', { min: 1, max: 100000 });
  if (!Number.isInteger(options.meshVertices)) throw new Error('meshVertices must be an integer.');
  finiteNumber(options.maxFrames, 'maxFrames', { min: 1, max: 1000000 });
  for (const [key, value] of Object.entries(options.thresholds)) {
    if (!(key in DEFAULT_THRESHOLDS)) throw new Error(`Unknown threshold: ${key}`);
    finiteNumber(value, `thresholds.${key}`, { min: 0 });
  }
  for (const rule of options.suppressions ?? []) {
    for (const key of ['boneRegex', 'slotRegex']) if (rule[key]) new RegExp(rule[key]);
    if (rule.start !== undefined) finiteNumber(rule.start, 'suppression start');
    if (rule.end !== undefined) finiteNumber(rule.end, 'suppression end');
    if ((rule.start ?? -Infinity) > (rule.end ?? Infinity)) throw new Error('Suppression start must not exceed end.');
  }
}
export function auditFile(input, userOptions = {}) {
  const options = { fps: 60, physics: 'none', meshVertices: 16, maxFrames: 20000, ...userOptions, thresholds: { ...DEFAULT_THRESHOLDS, ...userOptions.thresholds } };
  validateOptions(options);
  const { data, metadata } = loadSkeleton(input, options);
  options.regionGeometry = metadata.regionGeometry;
  options.referenceScale = referenceScale(data, options);
  const chosenNames = options.animations ?? data.animations.map(a => a.name);
  if (!Array.isArray(chosenNames) || chosenNames.some(n => typeof n !== 'string')) throw new Error('animations must be an array of names.');
  const loops = new Set(options.loops ?? []);
  const names = [...new Set([...chosenNames, ...loops])];
  for (const name of loops) if (!data.findAnimation(name)) throw new Error(`Loop animation not found: ${name}`);
  const warnings = [
    'Continuity risk signals are review candidates, not an aesthetic score or universal quality standard. Deliberate impacts/holds can produce strong signals.',
    'Geometry only: no pixels/textures, silhouette matching across attachment swaps, perceptual salience, occlusion, clipping, anti-aliasing, camera motion or real frame pacing.',
    'Single skeleton, skin and track 0 only. Match production tracks, timeScale, mix configuration, interruptions and engine behavior separately.',
    'Finite sampling can miss subframe jumps or alias fast rotations (especially >=180 degrees/sample). Verify suspect times at 2x/4x FPS.',
    'Derivative magnitudes depend on FPS around actual discontinuities; compare identical settings. Quantiles pool landmarks, so rig density can bias cross-character comparisons.',
    'Bone probes include helper bones by default; use visible-geometry summaries, --visible-bones-only or bone filters. Bone influence is a dependency approximation, not pixel visibility.',
    'Triangle collapse/flip is a geometric hint, not proof of a rendering defect. First visible pose is the reference and may already be distorted.',
  ];
  if (!metadata.atlas) warnings.push('No atlas: region corners skipped to avoid incorrect trim/rotation geometry. Mesh vertices and bones still sampled. Supply matching .atlas for complete region landmarks.');
  if (options.physics === 'none' && data.physicsConstraints.length) warnings.push(`${data.physicsConstraints.length} physics constraints disabled. Use --physics update to include sequential simulation.`);
  if (options.physics === 'update') warnings.push('Physics begins from reset without pre-settling; initial transient is included. Animation timestep is duration/ceil(duration*fps); transition warm-up reaches fromTime exactly, then uses 1/fps. External physicsTranslate/Rotate are not modeled.');
  const analyses = names.map(name => analyzeSample(sampleAnimation(data, name, options), { ...options, loop: loops.has(name) }));
  for (const transition of options.transitions ?? []) analyses.push(analyzeSample(sampleTransition(data, transition, options), options));
  return { schemaVersion: 1, title: 'Spine continuity risk audit / Spine 连续性风险检查', generatedAt: new Date().toISOString(), input: metadata, skeleton: { bones: data.bones.length, slots: data.slots.length, physicsConstraints: data.physicsConstraints.length, availableAnimations: data.animations.map(a => ({ name: a.name, duration: a.duration })), skin: options.skin ?? '(default)' }, referenceScale: options.referenceScale, configuration: { fps: options.fps, physics: options.physics, meshVertices: options.meshVertices, thresholds: options.thresholds, bones: options.bones ?? null, ignoreBones: options.ignoreBones ?? null, slots: options.slots ?? null, ignoreSlots: options.ignoreSlots ?? null, visibleBonesOnly: !!options.visibleBonesOnly, suppressStepped: !!options.suppressStepped, suppressions: options.suppressions ?? [] }, units: { step: 'reference-scale units', speed: 'reference-scale units / second', acceleration: 'reference-scale units / second^2', jerk: 'reference-scale units / second^3', time: 'seconds; transition time 0 is the requested switch' }, warnings, analyses };
}
const number = (n, digits = 5) => n === null || n === undefined ? 'n/a' : Number(n).toFixed(digits);
const quoteCsv = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
function csv(rows) { return rows.map(row => row.map(quoteCsv).join(',')).join('\n') + '\n'; }
export function reportMarkdown(report) {
  const lines = [`# Spine 连续性风险检查`, '', `输入：${report.input.filename} · Spine ${report.input.spineVersion} · runtime ${report.input.runtimeVersion}`, `参考长度：${number(report.referenceScale.value)} (${report.referenceScale.source})`, `采样：请求 ${report.configuration.fps} FPS；物理：${report.configuration.physics}；可见网格每附件最多 ${report.configuration.meshVertices} 个顶点。`, '', '速度、加速度和 jerk 均已按固定参考长度归一化。风险计数是“点×时间×指标”的诊断数量，不是缺陷数量，也不能当分数排名。', '', '## 汇总', '', '| 动画/过渡 | 时长 s | 风险信号 | 已标注意图 | 附件/层序等事件 | 网格提示 | loop位置差 | loop速度差 |', '|---|---:|---:|---:|---:|---:|---:|---:|'];
  for (const a of report.analyses) lines.push(`| ${a.name.replaceAll('|', '\\|')} | ${number(a.duration, 3)} | ${a.signalCount} | ${a.suppressedCount} | ${a.discreteEvents.length} | ${a.geometryEvents.length} | ${number(a.loopSeam?.maxPositionGap)} | ${number(a.loopSeam?.maxVelocityGap)} |`);
  for (const a of report.analyses) {
    lines.push('', `## ${a.name}`, '', `实际采样 ${a.sampleCount} 帧，有效 FPS ${number(a.effectiveFps, 3)}。${a.type === 'transition' ? `切换时间记作 0；从动画相位 ${number(a.settings.fromTime, 3)} s，mix=${number(a.settings.mix, 3)} s。` : ''}`);
    if (a.switchInstant) lines.push(`切换瞬间最大同身份点位置差：${number(a.switchInstant.maxPositionGap)}；附件/层序事件 ${a.switchInstant.discreteEvents.length}。`);
    if (a.loopSeam) lines.push(`仅在准备循环播放时解读：端点位置风险 ${a.loopSeam.positionRisk}，端点速度风险 ${a.loopSeam.velocityRisk}；附件/层序接缝事件 ${a.loopSeam.discreteEvents.length}。速度采用5点高阶单侧差分，对比3点结果估计误差：${number(a.loopSeam.maxVelocityUncertainty)}；误差估计不是严格界限，需提高FPS复验。`);
    const top = a.continuitySignals.filter(e => !e.suppressed).slice(0, 12);
    lines.push('', '最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：');
    if (!top.length) lines.push('- 当前阈值下无信号；不等于视觉完美。');
    for (const e of top) lines.push(`- ${number(e.time, 4)} s [${number(e.supportStart, 4)}, ${number(e.supportEnd, 4)}]：${e.metric}=${number(e.magnitude)}，阈值=${number(e.threshold)}；${e.id}${e.kind === 'bone' && !e.visibleInfluence ? '（未识别为可见附件依赖骨）' : ''}`);
    if (a.discreteEvents.length) { lines.push('', '离散事件（独立报告，不自动扣分）：'); for (const e of a.discreteEvents.slice(0, 12)) lines.push(`- ${number(e.time, 4)} s：${e.type} ${e.slot ?? ''} ${e.from ?? ''} → ${e.to ?? ''}`); }
    if (a.geometryEvents.length) { lines.push('', '网格风险提示（先确认是否为有意透视/镜像）：'); for (const e of a.geometryEvents.slice(0, 12)) lines.push(`- ${number(e.time, 4)} s：${e.type}，${e.slot}/${e.attachment}，三角面 ${e.triangleCount} 个`); }
    if (a.angularAliasingRisks.length) { lines.push('', '角度欠采样警告：'); for (const e of a.angularAliasingRisks.slice(0, 12)) lines.push(`- ${e.bone}，${number(e.start, 4)}–${number(e.end, 4)} s：平均每采样步约 ${number(e.degreesPerSample, 1)} 度，当前结果可能把快速转动误读成静止。`); }
  }
  lines.push('', '## 可信范围与限制', '', ...report.warnings.map(w => `- ${w}`), '', '## 下一步', '', '1. 先看 visible-geometry 与具体 slot/bone；再看被标记区间和附件事件。', '2. 用相同设置在 60/120/240 FPS 复验；真实阶跃的导数通常随 FPS 增长，有限差分噪声也会变大。', '3. 在原播放器逐帧检查命中/急停/换姿势是否有意；用 config.suppressions 标注意图，保留审计记录。', '4. loop 要同时检查位置与速度；实际切换必须用运行时 mix 配置模拟，端点相等并不能保证中段无褶皱或像素跳。', '');
  return lines.join('\n');
}
export function writeReport(report, outputDir) {
  fs.mkdirSync(outputDir, { recursive: true });
  const events = [['animation', 'type', 'time_s', 'support_start_s', 'support_end_s', 'metric', 'magnitude', 'threshold', 'ratio', 'bone', 'slot', 'landmark', 'suppressed', 'reason']];
  const frames = [['animation', 'frame', 'time_s', 'max_step', 'max_speed', 'max_acceleration', 'max_jerk', 'worst_step', 'worst_speed', 'worst_acceleration', 'worst_jerk']];
  for (const a of report.analyses) {
    for (const e of a.continuitySignals) events.push([a.name, 'continuity-signal', e.time, e.supportStart, e.supportEnd, e.metric, e.magnitude, e.threshold, e.ratio, e.bone, e.slot, e.id, e.suppressed, e.suppressionReason]);
    for (const e of [...a.discreteEvents, ...a.geometryEvents]) events.push([a.name, e.type, e.time, e.intervalStart, e.time, '', '', '', '', '', e.slot, e.attachment ?? '', false, JSON.stringify(e)]);
    for (const f of a.perFrame) frames.push([a.name, f.frame, f.time, f.step, f.speed, f.acceleration, f.jerk, f.worst.step, f.worst.speed, f.worst.acceleration, f.worst.jerk]);
  }
  fs.writeFileSync(path.join(outputDir, 'report.json'), JSON.stringify(report, null, 2));
  fs.writeFileSync(path.join(outputDir, 'report.md'), reportMarkdown(report));
  fs.writeFileSync(path.join(outputDir, 'signals.csv'), csv(events));
  fs.writeFileSync(path.join(outputDir, 'frames.csv'), csv(frames));
}
