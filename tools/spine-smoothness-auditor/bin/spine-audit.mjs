#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs } from 'node:util';
import { auditFile, writeReport } from '../lib/audit.mjs';
import { loadSkeleton } from '../lib/runtime.mjs';

const help = `Spine 4.2 连续性风险检查器 (Node >=20)
Usage: node bin/spine-audit.mjs --input skeleton.json|skeleton.skel [options]

  --atlas FILE             Atlas 元数据；默认自动寻找同名 .atlas，不需纹理 PNG
  --list                   列出动画后退出
  --animations a,b         要检查的动画；默认全部 (不自动猜测循环)
  --loops idle,walk        检查这些动画的端点位置/速度 (会自动加入 animations)
  --transition from:to     可重复；通过 AnimationState 模拟真实单轨 mix
  --mix SECONDS            过渡时长，默认 0.2
  --from-time SECONDS      源动画开始切换的相位；默认源动画末尾
  --from-loop              源动画在 warm-up 和 mix 中循环
  --to-loop                目标动画循环
  --fps NUMBER             采样 FPS，默认60 (1..1000)
  --physics none|update    默认 none；update 为顺序物理模拟
  --skin NAME              选择 skin
  --scale NUMBER           固定归一化参考长度，覆盖自动 setup-visible bbox
  --bones REGEX            仅这些骨骼；--ignore-bones REGEX 排除
  --slots REGEX            仅这些槽位；--ignore-slots REGEX 排除
  --visible-bones-only     只取当前可见附件的骨依赖 (近似，不含约束逆依赖)
  --mesh-vertices N        每可见附件最多采样N点，默认16；三角形检查仍用全部点
  --suppress-stepped       标注意图明确的直接 bone/slot stepped 支持区间
  --config FILE            JSON高级配置：thresholds、suppressions、transitions等
  --out DIR                输出 report.json/report.md/signals.csv/frames.csv
  --help                   本帮助

Example:
  node bin/spine-audit.mjs --input hero.json --loops idle --transition attack:idle --mix 0.2 --out out

没有“通用丝滑总分”。输出是需要视觉复验的连续性风险信号。`;
try {
  const { values: v } = parseArgs({ strict: true, options: {
    input: { type: 'string' }, atlas: { type: 'string' }, animations: { type: 'string' }, loops: { type: 'string' }, transition: { type: 'string', multiple: true }, mix: { type: 'string' }, 'from-time': { type: 'string' }, 'from-loop': { type: 'boolean' }, 'to-loop': { type: 'boolean' }, fps: { type: 'string' }, physics: { type: 'string' }, skin: { type: 'string' }, scale: { type: 'string' }, bones: { type: 'string' }, 'ignore-bones': { type: 'string' }, slots: { type: 'string' }, 'ignore-slots': { type: 'string' }, 'visible-bones-only': { type: 'boolean' }, 'mesh-vertices': { type: 'string' }, 'suppress-stepped': { type: 'boolean' }, config: { type: 'string' }, out: { type: 'string' }, list: { type: 'boolean' }, help: { type: 'boolean', short: 'h' },
  } });
  if (v.help) { console.log(help); process.exit(0); }
  if (!v.input) throw new Error('Missing --input. Use --help.');
  const o = v.config ? JSON.parse(fs.readFileSync(v.config, 'utf8')) : {};
  for (const key of ['atlas', 'physics', 'skin', 'bones', 'slots']) if (v[key] !== undefined) o[key] = v[key];
  for (const key of ['fps', 'mix', 'scale']) if (v[key] !== undefined) o[key] = Number(v[key]);
  for (const key of ['animations', 'loops']) if (v[key] !== undefined) o[key] = v[key].split(',').filter(Boolean);
  for (const [flag, key] of [['ignore-bones', 'ignoreBones'], ['ignore-slots', 'ignoreSlots'], ['visible-bones-only', 'visibleBonesOnly'], ['suppress-stepped', 'suppressStepped']]) if (v[flag] !== undefined) o[key] = v[flag];
  if (v['mesh-vertices'] !== undefined) o.meshVertices = Number(v['mesh-vertices']);
  if (v.transition) o.transitions = v.transition.map(value => { const [from, to, extra] = value.split(':'); if (!from || !to || extra) throw new Error('Use --transition from:to; for names containing colon use config.transitions.'); return { from, to, ...(v.mix !== undefined ? { mix: Number(v.mix) } : {}), ...(v['from-time'] !== undefined ? { fromTime: Number(v['from-time']) } : {}), fromLoop: !!v['from-loop'], toLoop: !!v['to-loop'] }; });
  if (v.list) { const { data } = loadSkeleton(v.input, o); for (const a of data.animations) console.log(`${a.name}\t${a.duration.toFixed(6)}s`); process.exit(0); }
  const report = auditFile(v.input, o), out = v.out ?? 'spine-audit-output';
  writeReport(report, out);
  for (const a of report.analyses) console.log(`${a.name}: signals=${a.signalCount}, intentional=${a.suppressedCount}, discrete=${a.discreteEvents.length}, geometry=${a.geometryEvents.length}${a.loopSeam ? `, loopPosition=${a.loopSeam.maxPositionGap}, loopVelocity=${a.loopSeam.maxVelocityGap}` : ''}`);
  console.log(`Reports written: ${path.resolve(out)}`);
} catch (error) { console.error(`spine-audit: ${error.message}`); process.exitCode = 1; }
