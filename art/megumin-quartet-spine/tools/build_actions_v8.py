"""Build the size-calibrated candidate without changing the v7 baseline."""
from pathlib import Path
import runpy,shutil
root=Path(__file__).resolve().parents[1]
src=root/'actions-v7';out=root/'actions-v8'
for directory in ['source','references']:
 (out/directory).mkdir(parents=True,exist_ok=True)
 for file in (src/directory).iterdir():
  if file.suffix in ('.png','.txt'):shutil.copyfile(file,out/directory/file.name)
for name in ['attachment-switches.json','preview.js','index.template.html']:
 shutil.copyfile(src/name,out/name)
template=(out/'index.template.html').read_text(encoding='utf-8').replace('v7','v8').replace('V7','V8').replace('姿势绑定 · 局部附件变体 · 单根刚体法杖','体积校准 · 固定握杖手 · 连续手臂轨迹')
template=template.replace('research/sts2-animation-study.html','../actions-v7/research/sts2-animation-study.html')
(out/'index.template.html').write_text(template,encoding='utf-8')
(out/'verification').mkdir(exist_ok=True)
runpy.run_path(str(root/'tools/build_actions_v7.py'),init_globals={'OUT_OVERRIDE':out,'STABILIZE_PARTS':True})
