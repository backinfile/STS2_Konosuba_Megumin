import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import * as S from '@esotericsoftware/spine-core';
import { BinaryInput } from '@esotericsoftware/spine-core/dist/SkeletonBinary.js';

export const RUNTIME_VERSION = '4.2.120';
export function finiteNumber(value, name, { min = -Infinity, max = Infinity } = {}) {
  if (!Number.isFinite(value) || value < min || value > max) throw new Error(`${name} must be a finite number in [${min}, ${max}].`);
  return value;
}
function checkVersion(version) {
  if (typeof version !== 'string' || !/^4\.2(?:\.|$)/.test(version)) throw new Error(`Spine ${version ?? '(missing version)'} is unsupported. Export Spine 4.2 data; this tool pins runtime ${RUNTIME_VERSION}.`);
}
function validateJson(value, location = 'root') {
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error(`Non-finite JSON number at ${location}.`);
  if (Array.isArray(value)) {
    if (value.length && value.every(v => v && typeof v === 'object' && !Array.isArray(v)) && location.startsWith('root.animations.')) {
      let previous = -Infinity;
      for (const frame of value) {
        const time = frame.time ?? 0;
        if (typeof time !== 'number' || !Number.isFinite(time) || time < 0 || time < previous) throw new Error(`Invalid or unsorted timeline times at ${location}.`);
        previous = time;
      }
    }
    value.forEach((v, i) => validateJson(v, `${location}[${i}]`));
  } else if (value && typeof value === 'object') for (const [key, item] of Object.entries(value)) validateJson(item, `${location}.${key}`);
}
export function loadSkeleton(input, options = {}) {
  const bytes = fs.readFileSync(input);
  if (bytes.length > 100 * 1024 * 1024) throw new Error('Input exceeds 100 MiB safety limit.');
  const binary = path.extname(input).toLowerCase() === '.skel';
  let json;
  if (binary) {
    if (bytes.length < 12) throw new Error('Truncated .skel header.');
    const header = new BinaryInput(new Uint8Array(bytes));
    header.readInt32(); header.readInt32(); checkVersion(header.readString());
  } else { json = JSON.parse(bytes.toString('utf8')); checkVersion(json.skeleton?.spine); validateJson(json); }
  const siblingAtlas = input.replace(/\.[^.]+$/, '.atlas');
  const atlasPath = options.atlas || (fs.existsSync(siblingAtlas) ? siblingAtlas : null);
  const dummyRegion = { u: 0, v: 0, u2: 1, v2: 1, width: 1, height: 1, originalWidth: 1, originalHeight: 1, offsetX: 0, offsetY: 0, degrees: 0 };
  const atlas = atlasPath ? new S.TextureAtlas(fs.readFileSync(atlasPath, 'utf8')) : { findRegion: () => dummyRegion };
  const loader = new S.AtlasAttachmentLoader(atlas);
  const data = binary ? new S.SkeletonBinary(loader).readSkeletonData(new Uint8Array(bytes)) : new S.SkeletonJson(loader).readSkeletonData(json);
  checkVersion(data.version);
  if (!data.bones.length) throw new Error('Skeleton contains no bones.');
  return { data, metadata: { filename: path.basename(input), sha256: crypto.createHash('sha256').update(bytes).digest('hex'), spineVersion: data.version, runtimeVersion: RUNTIME_VERSION, atlas: atlasPath ? path.basename(atlasPath) : null, regionGeometry: !!atlasPath } };
}
export function makeSkeleton(data, options = {}) {
  const skeleton = new S.Skeleton(data);
  if (options.skin) skeleton.setSkinByName(options.skin);
  skeleton.setToSetupPose();
  skeleton.updateWorldTransform(S.Physics.none);
  return skeleton;
}
function renderVertices(slot, regionGeometry) {
  const a = slot.getAttachment();
  if (a instanceof S.MeshAttachment) {
    const vertices = new Float32Array(a.worldVerticesLength);
    a.computeWorldVertices(slot, 0, vertices.length, vertices, 0, 2);
    return vertices;
  }
  if (regionGeometry && a instanceof S.RegionAttachment) {
    const vertices = new Float32Array(8); a.computeWorldVertices(slot, vertices, 0, 2); return vertices;
  }
  return null;
}
export function referenceScale(data, options = {}) {
  if (options.scale !== undefined) return { value: finiteNumber(options.scale, 'scale', { min: 1e-9 }), source: 'explicit override' };
  const skeleton = makeSkeleton(data, options); const xy = [];
  for (const slot of skeleton.slots) {
    const a = slot.getAttachment();
    if (!slot.bone.active || !a || slot.color.a * (a.color?.a ?? 1) < 0.01) continue;
    const v = renderVertices(slot, options.regionGeometry); if (v) xy.push(...v);
  }
  function diagonal(values) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (let i = 0; i < values.length; i += 2) { minX = Math.min(minX, values[i]); minY = Math.min(minY, values[i + 1]); maxX = Math.max(maxX, values[i]); maxY = Math.max(maxY, values[i + 1]); }
    return Math.hypot(maxX - minX, maxY - minY);
  }
  const visible = diagonal(xy);
  if (Number.isFinite(visible) && visible > 1e-6) return { value: visible, source: 'setup-visible geometry bounding-box diagonal (before clipping/occlusion)' };
  const exported = Math.hypot(data.width || 0, data.height || 0);
  if (exported > 1e-6) return { value: exported, source: 'exported skeleton bounds diagonal fallback' };
  const bones = [];
  for (const b of skeleton.bones) { bones.push(b.worldX, b.worldY, b.worldX + b.a * b.data.length, b.worldY + b.c * b.data.length); }
  const value = diagonal(bones);
  if (value > 1e-6) return { value, source: 'setup bone bounds diagonal fallback (helper bones included)' };
  return { value: 1, source: 'unit fallback; set --scale for meaningful normalized units' };
}
function selector(include, exclude) {
  const inc = include ? new RegExp(include) : null, exc = exclude ? new RegExp(exclude) : null;
  return name => (!inc || inc.test(name)) && (!exc || !exc.test(name));
}
export function createSampler(data, options) {
  const skeleton = makeSkeleton(data, options);
  const state = new S.AnimationState(new S.AnimationStateData(data));
  const takeBone = selector(options.bones, options.ignoreBones), takeSlot = selector(options.slots, options.ignoreSlots);
  const landmarks = new Map();
  const scale = options.referenceScale.value;
  const maxVertices = options.meshVertices ?? 16;
  const boneVisibility = new Set();
  const attachmentKeys = new WeakMap();
  for (const skin of data.skins) for (const entry of skin.getAttachments()) attachmentKeys.set(entry.attachment, `${skin.name}/${entry.name}`);
  function snapshot(time) {
    const points = {}, slots = {}, triangles = {};
    boneVisibility.clear();
    for (const slot of skeleton.slots) {
      const a = slot.getAttachment();
      const alpha = skeleton.color.a * slot.color.a * (a?.color?.a ?? 1);
      const visible = !!a && slot.bone.active && alpha > (options.visibilityThreshold ?? 0.01);
      if (visible) {
        let b = slot.bone;
        while (b) { boneVisibility.add(b.data.index); b = b.parent; }
        if (a instanceof S.MeshAttachment && a.bones) {
          for (let i = 0; i < a.bones.length;) {
            const n = a.bones[i++];
            for (let j = 0; j < n; j++) {
              let weightedBone = skeleton.bones[a.bones[i++]];
              while (weightedBone) { boneVisibility.add(weightedBone.data.index); weightedBone = weightedBone.parent; }
            }
          }
        }
      }
      if (!takeSlot(slot.data.name)) continue;
      const identity = a ? `${a.name}#${attachmentKeys.get(a) ?? a.name}` : null;
      slots[slot.data.name] = { attachment: identity, name: a?.name ?? null, alpha, visible, sequence: slot.sequenceIndex };
      if (!visible) continue;
      const v = renderVertices(slot, options.regionGeometry); if (!v) continue;
      const count = v.length / 2, chosen = new Set();
      for (let i = 0; i < Math.min(count, maxVertices); i++) chosen.add(Math.floor(i * (count - 1) / Math.max(1, Math.min(count, maxVertices) - 1)));
      for (const index of chosen) {
        const id = `slot:${slot.data.name}/${identity}/v${index}`;
        points[id] = [v[index * 2] / scale, v[index * 2 + 1] / scale];
        landmarks.set(id, { kind: 'visible-geometry', slot: slot.data.name, bone: slot.bone.data.name, attachment: a.name, vertex: index });
      }
      if (a instanceof S.MeshAttachment) {
        const areas = [];
        for (let i = 0; i < a.triangles.length; i += 3) {
          const [u, w, z] = a.triangles.slice(i, i + 3).map(n => n * 2);
          areas.push(((v[w] - v[u]) * (v[z + 1] - v[u + 1]) - (v[w + 1] - v[u + 1]) * (v[z] - v[u])) / (2 * scale * scale));
        }
        triangles[`${slot.data.name}/${identity}`] = { slot: slot.data.name, attachment: a.name, areas };
      }
    }
    for (const b of skeleton.bones) {
      if (!b.active || !takeBone(b.data.name) || (options.visibleBonesOnly && !boneVisibility.has(b.data.index))) continue;
      const length = Math.max(Math.abs(b.data.length), scale * 0.03), axisY = scale * 0.03;
      for (const [label, x, y] of [['origin', 0, 0], ['x-axis', length, 0], ['y-axis', 0, axisY]]) {
        const id = `bone:${b.data.name}/${label}`;
        points[id] = [(b.worldX + x * b.a + y * b.b) / scale, (b.worldY + x * b.c + y * b.d) / scale];
        landmarks.set(id, { kind: 'bone', bone: b.data.name, landmark: label, setupLength: b.data.length, visibleInfluence: boneVisibility.has(b.data.index) });
      }
    }
    for (const [id, p] of Object.entries(points)) if (!p.every(Number.isFinite)) throw new Error(`Non-finite world geometry at ${time}s: ${id}.`);
    return { time, points, slots, drawOrder: skeleton.drawOrder.filter(s => takeSlot(s.data.name)).map(s => s.data.name), triangles };
  }
  function advance(dt, exactTrackTime) {
    state.update(dt);
    if (exactTrackTime !== undefined && state.tracks[0]) state.tracks[0].trackTime = exactTrackTime;
    state.apply(skeleton); skeleton.update(dt); skeleton.updateWorldTransform(options.physics === 'update' ? S.Physics.update : S.Physics.none);
  }
  return { skeleton, state, snapshot, advance, landmarks };
}
export function stepMarkers(data, animation) {
  const result = [];
  for (const timeline of animation.timelines) {
    if (!timeline.curves || !timeline.getFrameEntries) continue;
    const n = timeline.getFrameEntries(), count = timeline.frames.length / n;
    for (let i = 0; i < count - 1; i++) if (timeline.curves[i] === 1) result.push({ time: timeline.frames[(i + 1) * n], timeline: timeline.constructor.name, bone: data.bones[timeline.boneIndex]?.name ?? null, slot: data.slots[timeline.slotIndex]?.name ?? null });
  }
  return result;
}
function angularAliasingRisks(data, animation, fps) {
  const risks = [];
  for (const timeline of animation.timelines) {
    if (!(timeline instanceof S.RotateTimeline)) continue;
    const entries = timeline.getFrameEntries();
    for (let i = entries; i < timeline.frames.length; i += entries) {
      const dt = timeline.frames[i] - timeline.frames[i - entries], delta = timeline.frames[i + 1] - timeline.frames[i - entries + 1];
      const degreesPerSample = dt > 0 ? Math.abs(delta / dt / fps) : Infinity;
      if (degreesPerSample >= 90) risks.push({ bone: data.bones[timeline.boneIndex]?.name, start: timeline.frames[i - entries], end: timeline.frames[i], degreesPerSample: Number.isFinite(degreesPerSample) ? degreesPerSample : null, note: 'Average key-to-key rotation exceeds 90 degrees per sample; increase FPS. Bezier peaks and parent composition can be faster.' });
    }
  }
  return risks;
}
function grid(duration, fps, maxFrames = 20000) {
  const intervals = duration > 0 ? Math.ceil(duration * fps) : 0;
  if (intervals + 1 > maxFrames) throw new Error(`Sampling needs ${intervals + 1} frames, above maxFrames=${maxFrames}.`);
  return { intervals, dt: intervals ? duration / intervals : 0 };
}
export function sampleAnimation(data, name, options) {
  const animation = data.findAnimation(name); if (!animation) throw new Error(`Animation not found: ${name}`);
  finiteNumber(animation.duration, `${name} duration`, { min: 0 });
  const { intervals, dt } = grid(animation.duration, options.fps, options.maxFrames);
  const sampler = createSampler(data, options); sampler.state.setAnimation(0, name, false); sampler.advance(0);
  const frames = [sampler.snapshot(0)];
  for (let i = 1; i <= intervals; i++) { sampler.advance(dt, i * dt); frames.push(sampler.snapshot(i * dt)); }
  return { name, type: 'animation', duration: animation.duration, dt, effectiveFps: dt ? 1 / dt : null, frames, landmarks: Object.fromEntries(sampler.landmarks), steppedKeys: stepMarkers(data, animation), angularAliasingRisks: angularAliasingRisks(data, animation, dt ? 1 / dt : options.fps) };
}
export function sampleTransition(data, transition, options) {
  const { from, to } = transition;
  const fromAnimation = data.findAnimation(from), toAnimation = data.findAnimation(to);
  if (!fromAnimation || !toAnimation) throw new Error(`Transition animation not found: ${from} -> ${to}`);
  const fromTime = transition.fromTime ?? fromAnimation.duration;
  const mix = transition.mix ?? options.mix ?? 0.2;
  finiteNumber(fromTime, 'fromTime', { min: 0 }); finiteNumber(mix, 'mix', { min: 0 });
  const dt = 1 / options.fps;
  const before = transition.preRoll ?? Math.max(0.1, 3 * dt);
  const after = transition.postRoll ?? Math.max(mix + 0.2, 4 * dt);
  finiteNumber(before, 'preRoll', { min: 0 }); finiteNumber(after, 'postRoll', { min: dt });
  if (transition.attachmentThreshold !== undefined) finiteNumber(transition.attachmentThreshold, 'attachmentThreshold', { min: 0, max: 1 });
  if (transition.drawOrderThreshold !== undefined) finiteNumber(transition.drawOrderThreshold, 'drawOrderThreshold', { min: 0, max: 1 });
  const warmFrames = Math.ceil(fromTime / dt), postFrames = Math.ceil(after / dt);
  if (warmFrames + postFrames + 3 > (options.maxFrames ?? 20000)) throw new Error('Transition exceeds maxFrames.');
  const sampler = createSampler(data, options);
  const entry = sampler.state.setAnimation(0, from, !!transition.fromLoop);
  sampler.advance(0);
  const frames = [];
  // Fixed warm-up dt chosen so the requested transition phase is reached exactly.
  const warmDt = warmFrames ? fromTime / warmFrames : dt;
  if (fromTime <= before) frames.push(sampler.snapshot(-fromTime));
  for (let i = 1; i <= warmFrames; i++) { sampler.advance(warmDt, i * warmDt); const t = i * warmDt - fromTime; if (t >= -before - 1e-10) frames.push(sampler.snapshot(t)); }
  if (!frames.length) frames.push(sampler.snapshot(0));
  const beforeSwitch = frames.at(-1);
  const target = sampler.state.setAnimation(0, to, !!transition.toLoop);
  target.mixDuration = mix;
  if (transition.attachmentThreshold !== undefined) entry.mixAttachmentThreshold = transition.attachmentThreshold;
  if (transition.drawOrderThreshold !== undefined) entry.mixDrawOrderThreshold = transition.drawOrderThreshold;
  sampler.advance(0);
  const afterSwitch = sampler.snapshot(0);
  // Do not invent a nonzero delta for an instantaneous switch: report the same-time jump separately.
  frames[frames.length - 1] = afterSwitch;
  for (let i = 1; i <= postFrames; i++) { sampler.advance(dt); frames.push(sampler.snapshot(i * dt)); }
  return { name: `${from} -> ${to}`, type: 'transition', duration: frames.at(-1).time - frames[0].time, dt, effectiveFps: options.fps, frames, landmarks: Object.fromEntries(sampler.landmarks), steppedKeys: [], beforeSwitch, afterSwitch, settings: { from, to, fromTime, mix, fromLoop: !!transition.fromLoop, toLoop: !!transition.toLoop, preRoll: before, postRoll: postFrames * dt, attachmentThreshold: entry.mixAttachmentThreshold, drawOrderThreshold: entry.mixDrawOrderThreshold, mixing: 'single track 0, default runtime mix curves, target starts at time 0' } };
}
