"""Build the continuous-motion candidate; preserve v8 as the A/B baseline."""
from pathlib import Path
import runpy, shutil, json, hashlib
root = Path(__file__).resolve().parents[1]
src, out = root/'actions-v8', root/'actions-v9'
for directory in ('source', 'references'):
    (out/directory).mkdir(parents=True, exist_ok=True)
    for file in (src/directory).iterdir():
        if file.suffix in ('.png', '.txt'):
            shutil.copyfile(file, out/directory/file.name)
for name in ('attachment-switches.json', 'preview.js', 'index.template.html'):
    shutil.copyfile(src/name, out/name)
template = (out/'index.template.html').read_text(encoding='utf-8')
template = template.replace('v8', 'v9').replace('V8', 'V9').replace('体积校准 · 固定握杖手 · 连续手臂轨迹', '连续速度 · 曲线轨迹 · 身体跟随')
(out/'index.template.html').write_text(template, encoding='utf-8')
(out/'verification').mkdir(exist_ok=True)
# Identical source pixels inherit the original-resolution Mi-Ripple evidence;
# validate_moire.py checks every active source hash again for this build.
report_file=src/'verification/moire.json'
report=json.loads(report_file.read_text(encoding='utf-8'))
report['inherited_from']={'version':'actions-v8','report_sha256':hashlib.sha256(report_file.read_bytes()).hexdigest(),'reason':'All active source pixels unchanged; validate_moire.py rechecks the current hashes.'}
(out/'verification/moire.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for file in (src/'verification/moire').rglob('*'):
    if file.is_file() and (file.suffix in ('.json','.xml') or file.name.startswith('review-') and file.suffix=='.jpg'):
        target=out/'verification/moire'/file.relative_to(src/'verification/moire')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(file,target)
runpy.run_path(str(root/'tools/build_actions_v7.py'), init_globals={'OUT_OVERRIDE': out, 'STABILIZE_PARTS': True, 'CONTINUOUS_MOTION': True})
