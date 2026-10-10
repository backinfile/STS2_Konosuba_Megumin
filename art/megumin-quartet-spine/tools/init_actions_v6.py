from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'actions-v6'
out.mkdir(exist_ok=True)
shutil.copytree(root/'actions-v5/source',out/'source',dirs_exist_ok=True)
for name in ['build_actions_v5.py','actions_v5_overrides.py','bake_floor_v5.mjs','validate_actions_v5.mjs','package_actions_v5.py','gallery_actions_v5.py','build_review_v5.py']:
    target=root/'tools'/name.replace('v5','v6')
    if not target.exists():
        text=(root/'tools'/name).read_text(encoding='utf-8').replace('actions-v5','actions-v6').replace('actions_v5','actions_v6').replace('layered-v5','layered-v6').replace('MOTION V5','MOTION V6').replace('0.5.0','0.6.0')
        target.write_text(text,encoding='utf-8')
for name in ['index.html','preview.js','README.md']:
    source=root/'actions-v5'/name
    if source.exists() and not (out/name).exists():
        (out/name).write_text(source.read_text(encoding='utf-8').replace('actions-v5','actions-v6').replace('actions_v5','actions_v6').replace('MOTION V5','MOTION V6'),encoding='utf-8')
print(out)
