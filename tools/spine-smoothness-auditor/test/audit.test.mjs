import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { auditFile, writeReport } from '../lib/audit.mjs';
import { derivative } from '../lib/metrics.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const fixture = path.join(root, 'fixtures/synthetic.json');
const cli = path.join(root, 'bin/spine-audit.mjs');
const audit = options => auditFile(fixture, options);
test('derivatives use vector change rather than difference of scalar speeds', () => {
  const velocity = derivative([{ time: 0, value: [0, 0] }, { time: 1, value: [1, 0] }, { time: 2, value: [1, 1] }]);
  assert.equal(velocity[0].magnitude, 1); assert.equal(velocity[1].magnitude, 1);
  assert.equal(derivative(velocity)[0].magnitude, Math.sqrt(2));
});
test('finite sampling reports exact support intervals for jerk', () => {
  const r = audit({ animations: ['stepped_jump'] }).analyses[0];
  const e = r.continuitySignals.find(x => x.metric === 'jerk');
  assert.ok(e); assert.ok(Math.abs(e.supportEnd - e.supportStart - 3 / 60) < 1e-6);
});
test('explicit suppression retains signals with reason but lowers active count', () => {
  const base = audit({ animations: ['stepped_jump'] }).analyses[0];
  const reviewed = audit({ animations: ['stepped_jump'], suppressions: [{ animation: 'stepped_jump', start: 0, end: 1, reason: 'intentional impact' }] }).analyses[0];
  assert.ok(base.signalCount > 0); assert.equal(reviewed.signalCount, 0); assert.equal(reviewed.suppressedCount, base.signalCount);
  assert.ok(reviewed.continuitySignals.every(e => e.suppressionReason === 'intentional impact'));
});
test('step metadata supports direct-bone intentional stepped annotations', () => {
  const a = audit({ animations: ['stepped_jump'], suppressStepped: true }).analyses[0];
  assert.ok(a.steppedKeys.length); assert.ok(a.suppressedCount > 0);
});
test('explicit loops automatically included alongside selected animations', () => {
  const r = audit({ animations: ['stationary'], loops: ['smooth_loop'] });
  assert.equal(r.analyses.length, 2); assert.ok(r.analyses[1].loopSeam);
});
test('bone and slot selectors control independent categories', () => {
  const a = audit({ animations: ['constant_velocity'], bones: '^root$', slots: '^NO_MATCH$' }).analyses[0];
  assert.equal(a.landmarks.length, 3); assert.ok(a.landmarks.every(x => x.bone === 'root' && x.kind === 'bone'));
});
test('repeated loads produce stable landmark identities and numeric results', () => {
  const a = audit({ animations: ['constant_velocity'] }), b = audit({ animations: ['constant_velocity'] });
  assert.deepEqual(a.analyses, b.analyses);
});
test('CSV, Markdown and JSON export complete and parseable', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'spine-audit-'));
  try {
    const r = audit({ animations: ['stationary', 'attachment_swap'] }); writeReport(r, temp);
    assert.deepEqual(fs.readdirSync(temp).sort(), ['frames.csv', 'report.json', 'report.md', 'signals.csv']);
    assert.equal(JSON.parse(fs.readFileSync(path.join(temp, 'report.json'))).schemaVersion, 1);
    assert.match(fs.readFileSync(path.join(temp, 'signals.csv'), 'utf8'), /attachment-change/);
    assert.match(fs.readFileSync(path.join(temp, 'report.md'), 'utf8'), /可信范围/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
test('CLI help and animation listing work', () => {
  assert.match(execFileSync(process.execPath, [cli, '--help'], { encoding: 'utf8' }), /--transition/);
  assert.match(execFileSync(process.execPath, [cli, '--input', fixture, '--list'], { encoding: 'utf8' }), /smooth_loop/);
});
test('CLI rejects missing input and invalid arguments with nonzero exit', () => {
  assert.notEqual(spawnSync(process.execPath, [cli], { encoding: 'utf8' }).status, 0);
  assert.notEqual(spawnSync(process.execPath, [cli, '--input', fixture, '--fps', 'NaN'], { encoding: 'utf8' }).status, 0);
});
test('invalid FPS, scale, regex, thresholds and animation are rejected', () => {
  for (const options of [{ fps: 0 }, { fps: NaN }, { fps: 1001 }, { scale: 0 }, { bones: '[' }, { meshVertices: 1.1 }, { thresholds: { speed: -1 } }, { thresholds: { mystery: 1 } }, { animations: ['missing'] }]) assert.throws(() => audit(options));
});
test('configured frame cap fails clearly', () => assert.throws(() => audit({ animations: ['stationary'], maxFrames: 3 }), /maxFrames/));
