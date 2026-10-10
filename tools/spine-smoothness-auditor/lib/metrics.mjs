export const DEFAULT_THRESHOLDS = { step: 0.03, speed: 3, acceleration: 60, jerk: 3000, madMultiplier: 8, loopPosition: 0.002, loopVelocity: 0.1, triangleAreaRatio: 0.02 };
const length = p => Math.hypot(p[0], p[1]);
export function quantile(values, q) {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y), n = (a.length - 1) * q, lo = Math.floor(n), hi = Math.ceil(n);
  return a[lo] + (a[hi] - a[lo]) * (n - lo);
}
export function derivative(series) {
  const result = [];
  for (let i = 1; i < series.length; i++) {
    const p = series[i - 1], q = series[i];
    const dt = q.time - p.time;
    if (!(dt > 0)) throw new Error('Derivative times must increase strictly.');
    const value = [(q.value[0] - p.value[0]) / dt, (q.value[1] - p.value[1]) / dt];
    result.push({ time: (p.time + q.time) / 2, value, magnitude: length(value), start: p.start ?? p.time, end: q.end ?? q.time, frame: q.frame });
  }
  return result;
}
function stats(values) {
  if (!values.length) return { count: 0, median: null, p95: null, p99: null, max: null, rms: null };
  return { count: values.length, median: quantile(values, 0.5), p95: quantile(values, 0.95), p99: quantile(values, 0.99), max: values.reduce((m, x) => Math.max(m, x), 0), rms: Math.sqrt(values.reduce((s, x) => s + x * x, 0) / values.length) };
}
function sameSlots(a, b) {
  const events = [];
  for (const name of new Set([...Object.keys(a.slots), ...Object.keys(b.slots)])) {
    const p = a.slots[name], q = b.slots[name];
    if (p?.attachment !== q?.attachment) events.push({ type: 'attachment-change', slot: name, from: p?.name ?? null, to: q?.name ?? null });
    if (p?.visible !== q?.visible) events.push({ type: 'visibility-change', slot: name, from: p?.visible ?? false, to: q?.visible ?? false });
    if (p?.sequence !== q?.sequence) events.push({ type: 'sequence-change', slot: name, from: p?.sequence, to: q?.sequence });
    if (p && q && Math.abs(p.alpha - q.alpha) >= 0.25) events.push({ type: 'alpha-step', slot: name, from: p.alpha, to: q.alpha });
  }
  if (JSON.stringify(a.drawOrder) !== JSON.stringify(b.drawOrder)) events.push({ type: 'draw-order-change', from: a.drawOrder, to: b.drawOrder });
  return events;
}
export function comparePoses(first, last, landmarks, threshold) {
  const distances = [];
  for (const [id, a] of Object.entries(first.points)) if (last.points[id]) {
    const b = last.points[id], magnitude = Math.hypot(a[0] - b[0], a[1] - b[1]);
    distances.push({ id, ...landmarks[id], magnitude });
  }
  const missing = [...new Set([...Object.keys(first.points), ...Object.keys(last.points)])].filter(id => !(first.points[id] && last.points[id]));
  return { matchedLandmarks: distances.length, unmatchedLandmarks: missing.length, maxPositionGap: distances.length ? Math.max(...distances.map(x => x.magnitude)) : null, positionRisk: distances.some(x => x.magnitude > threshold), worst: distances.sort((a, b) => b.magnitude - a.magnitude).slice(0, 10), discreteEvents: sameSlots(first, last), note: 'Only identical landmark identities are compared; changed/hidden attachments are separate events.' };
}
function loopSeam(sample, thresholds) {
  const { frames, landmarks } = sample;
  const result = comparePoses(frames[0], frames.at(-1), landmarks, thresholds.loopPosition);
  const velocity = [];
  if (frames.length >= 5) {
    const first = frames.slice(0, 5), last = frames.slice(-5).reverse();
    const estimate = (points, h, weights) => [0, 1].map(k => weights.reduce((sum, w, i) => sum + w * points[i][k], 0) / h);
    const d5 = [-25 / 12, 4, -3, 4 / 3, -1 / 4], d3 = [-1.5, 2, -0.5];
    for (const id of Object.keys(first[0].points)) if ([...first, ...last].every(f => f.points[id])) {
      const start = first.map(f => f.points[id]), end = last.map(f => f.points[id]);
      const h0 = first[1].time - first[0].time, h1 = last[1].time - last[0].time;
      const v0 = estimate(start, h0, d5), v1 = estimate(end, h1, d5), low0 = estimate(start, h0, d3), low1 = estimate(end, h1, d3);
      const magnitude = Math.hypot(v0[0] - v1[0], v0[1] - v1[1]);
      const uncertainty = Math.hypot(v0[0] - low0[0], v0[1] - low0[1]) + Math.hypot(v1[0] - low1[0], v1[1] - low1[1]);
      velocity.push({ id, ...landmarks[id], magnitude, uncertainty, risk: magnitude > thresholds.loopVelocity + uncertainty });
    }
  }
  result.maxVelocityGap = velocity.length ? Math.max(...velocity.map(x => x.magnitude)) : null;
  result.maxVelocityUncertainty = velocity.length ? Math.max(...velocity.map(x => x.uncertainty)) : null;
  result.velocityRisk = velocity.length ? velocity.some(x => x.risk) : null;
  result.worstVelocity = velocity.sort((a, b) => b.magnitude - a.magnitude).slice(0, 10);
  result.velocityMethod = '5-point fourth-order one-sided endpoint derivatives. Heuristic uncertainty is summed difference from 3-point estimates; risk requires gap > threshold + uncertainty. Not a rigorous error bound; increase FPS to verify. Fewer than 5 matched samples: unavailable. No acceleration seam claim.';
  result.physicsInterpretation = 'Endpoint diagnostic on first sequential cycle from reset, not a settled-loop physics simulation.';
  return result;
}
function suppressReason(event, sample, options) {
  for (const rule of options.suppressions ?? []) {
    if (rule.animation && rule.animation !== sample.name) continue;
    if (rule.metrics && !rule.metrics.includes(event.metric)) continue;
    if (rule.boneRegex && !new RegExp(rule.boneRegex).test(event.bone ?? '')) continue;
    if (rule.slotRegex && !new RegExp(rule.slotRegex).test(event.slot ?? '')) continue;
    if (event.supportEnd < (rule.start ?? -Infinity) || event.supportStart > (rule.end ?? Infinity)) continue;
    return rule.reason || 'configured intentional motion';
  }
  if (options.suppressStepped) {
    for (const key of sample.steppedKeys) {
      if (key.time < event.supportStart - 1e-8 || key.time > event.supportEnd + 1e-8) continue;
      // Direct bone/slot only: inheritance/constraints can propagate further; explicit windows handle those cases.
      if (key.bone && key.bone === event.bone || key.slot && key.slot === event.slot) return `intentional stepped key (${key.timeline})`;
    }
  }
  return null;
}
function geometryEvents(frames, thresholds) {
  const history = new Map(), events = [];
  for (let fi = 0; fi < frames.length; fi++) {
    const frame = frames[fi];
    for (const [id, mesh] of Object.entries(frame.triangles)) {
      let state = history.get(id);
      if (!state) { state = mesh.areas.map(a => ({ reference: Math.abs(a), sign: Math.sign(a), collapsed: Math.abs(a) < 1e-12 })); history.set(id, state); }
      const collapsed = [], flips = [];
      mesh.areas.forEach((area, index) => {
        const p = state[index], magnitude = Math.abs(area);
        const small = magnitude < 1e-12 || (p.reference > 1e-12 && magnitude / p.reference < thresholds.triangleAreaRatio);
        if (small && (!p.collapsed || fi === 0)) collapsed.push(index);
        const sign = magnitude > 1e-12 ? Math.sign(area) : 0;
        if (sign && p.sign && sign !== p.sign) flips.push(index);
        if (sign) p.sign = sign;
        p.collapsed = small;
      });
      if (collapsed.length) events.push({ time: frame.time, type: 'triangle-collapse', slot: mesh.slot, attachment: mesh.attachment, triangleCount: collapsed.length, triangleIndices: collapsed, note: 'Area small relative to first visible pose, or numerically zero; may be deliberate perspective flattening.' });
      if (flips.length) events.push({ time: frame.time, type: 'triangle-orientation-flip', slot: mesh.slot, attachment: mesh.attachment, triangleCount: flips.length, triangleIndices: flips, note: 'Signed triangle area changed; intentional mirroring/perspective can do this too.' });
    }
  }
  return events;
}
export function analyzeSample(sample, options = {}) {
  const thresholds = { ...DEFAULT_THRESHOLDS, ...options.thresholds };
  const all = { step: [], speed: [], acceleration: [], jerk: [] }, byKind = { bone: {}, 'visible-geometry': {} }, events = [], summaries = [];
  const perFrame = sample.frames.map((f, i) => ({ frame: i, time: f.time, step: 0, speed: 0, acceleration: 0, jerk: 0, worst: {} }));
  for (const [id, metadata] of Object.entries(sample.landmarks)) {
    const segments = []; let current = [];
    sample.frames.forEach((f, i) => { if (f.points[id]) current.push({ time: f.time, value: f.points[id], frame: i }); else if (current.length) { segments.push(current); current = []; } });
    if (current.length) segments.push(current);
    const measures = { step: [], speed: [], acceleration: [], jerk: [] };
    for (const segment of segments) {
      const speed = derivative(segment), acceleration = derivative(speed), jerk = derivative(acceleration);
      for (const x of speed) measures.speed.push(x);
      for (const x of acceleration) measures.acceleration.push(x);
      for (const x of jerk) measures.jerk.push(x);
      for (let i = 1; i < segment.length; i++) { const a = segment[i - 1], b = segment[i]; measures.step.push({ time: (a.time + b.time) / 2, frame: b.frame, start: a.time, end: b.time, magnitude: Math.hypot(b.value[0] - a.value[0], b.value[1] - a.value[1]) }); }
    }
    const item = { id, ...metadata, stats: {} };
    for (const [metric, series] of Object.entries(measures)) {
      const values = series.map(x => x.magnitude), stat = stats(values); item.stats[metric] = stat;
      const median = stat.median ?? 0, mad = quantile(values.map(x => Math.abs(x - median)), 0.5) ?? 0;
      const threshold = Math.max(thresholds[metric], median + thresholds.madMultiplier * Math.max(1.4826 * mad, median * 0.05, 1e-9));
      item.stats[metric].signalThreshold = threshold;
      const group = (byKind[metadata.kind][metric] ??= []);
      for (const value of values) { all[metric].push(value); group.push(value); }
      for (const x of series) {
        const frame = perFrame[x.frame];
        if (x.magnitude > frame[metric]) { frame[metric] = x.magnitude; frame.worst[metric] = id; }
        if (x.magnitude <= threshold) continue;
        const event = { metric, time: x.time, frame: x.frame, supportStart: x.start, supportEnd: x.end, magnitude: x.magnitude, threshold, ratio: x.magnitude / threshold, id, ...metadata };
        event.suppressed = !!(event.suppressionReason = suppressReason(event, sample, options)); events.push(event);
      }
    }
    summaries.push(item);
  }
  const discreteEvents = [];
  for (let i = 1; i < sample.frames.length; i++) for (const e of sameSlots(sample.frames[i - 1], sample.frames[i])) discreteEvents.push({ time: sample.frames[i].time, intervalStart: sample.frames[i - 1].time, ...e });
  const result = { name: sample.name, type: sample.type, duration: sample.duration, sampleCount: sample.frames.length, effectiveFps: sample.effectiveFps, settings: sample.settings, summary: Object.fromEntries(Object.entries(all).map(([k, v]) => [k, stats(v)])), byKind: Object.fromEntries(Object.entries(byKind).map(([kind, data]) => [kind, Object.fromEntries(Object.entries(data).map(([k, v]) => [k, stats(v)]))])), continuitySignals: events.sort((a, b) => b.ratio - a.ratio), signalCount: events.filter(e => !e.suppressed).length, suppressedCount: events.filter(e => e.suppressed).length, discreteEvents, geometryEvents: geometryEvents(sample.frames, thresholds), steppedKeys: sample.steppedKeys, perFrame, landmarks: summaries };
  result.angularAliasingRisks = sample.angularAliasingRisks ?? [];
  result.signalCountByKind = { bone: events.filter(e => !e.suppressed && e.kind === 'bone').length, 'visible-geometry': events.filter(e => !e.suppressed && e.kind === 'visible-geometry').length };
  if (options.loop) result.loopSeam = loopSeam(sample, thresholds);
  if (sample.type === 'transition') result.switchInstant = comparePoses(sample.beforeSwitch, sample.afterSwitch, sample.landmarks, thresholds.loopPosition);
  return result;
}
