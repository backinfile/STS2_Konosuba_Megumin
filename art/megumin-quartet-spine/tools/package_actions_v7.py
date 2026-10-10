from pathlib import Path
import json,base64,shutil,zipfile,hashlib
root=Path(__file__).resolve().parents[1];out=globals().get('OUT_OVERRIDE',root/'actions-v7')
version=out.name.split('-')[-1]
uri=lambda p:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
meta=json.loads((out/'authoring.json').read_text())
raw=json.loads((out/'export/megumin.json').read_text())
atlas=(out/'export/megumin.atlas').read_text()
pages=[line.strip() for line in atlas.splitlines() if line.endswith('.png')]
images=out/'images';images.mkdir(exist_ok=True)
for name in pages:
 source=out/'source'/('staff-only.png' if name=='staff-master.png' else name)
 shutil.copyfile(source,images/name)
for slots in raw['skins'][0]['attachments'].values():
 for attachment in slots.values():assert (images/(attachment['path']+'.png')).is_file(),attachment['path']
assert raw['skeleton']['images']=='../images/'
shutil.copyfile(out/'export/megumin.json',out/'export/megumin.spine-json')
docs=out/'docs';docs.mkdir(exist_ok=True)
guide=(root.parents[1]/'docs/Spine动画制作指引.md').read_text(encoding='utf-8')
(docs/'Spine动画制作指引.md').write_text(guide.replace('../art/megumin-quartet-spine/'+out.name+'/','../').replace('../art/megumin-quartet-spine/','../../'),encoding='utf-8')
shutil.copyfile(root.parents[1]/'docs/mod-lab.md',docs/'mod-lab.md')
shutil.copyfile(root/'vendor/SPINE-RUNTIME-LICENSE.txt',out/'SPINE-RUNTIME-LICENSE.txt')
bundle=dict(skeleton=raw,atlas=atlas,pages={name:uri(out/'export'/name) for name in pages},references={n:uri(out/'references'/(n+'.png')) for n in meta['poses']},meta=meta)
html=(out/'index.template.html').read_text(encoding='utf-8').replace('__BUNDLE__',json.dumps(bundle,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('__RUNTIME__',(root/'vendor/spine-webgl-4.2.95.min.js').read_text()).replace('__APP__',(out/'preview.js').read_text(encoding='utf-8'))
(out/'preview.html').write_text(html,encoding='utf-8')
# The network preview keeps PNGs separate to avoid large inline-image decoder
# limits. The offline preview above remains a self-contained distribution.
bundle['pages']={name:'export/'+name for name in pages}
bundle['references']={n:'references/'+n+'.png' for n in meta['poses']}
network=(out/'index.template.html').read_text(encoding='utf-8').replace('__BUNDLE__',json.dumps(bundle,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('__RUNTIME__',(root/'vendor/spine-webgl-4.2.95.min.js').read_text()).replace('__APP__',(out/'preview.js').read_text(encoding='utf-8'))
(out/'index.html').write_text(network,encoding='utf-8')
print('Preview bytes:',len(html.encode()))
files=[out/'README.md',out/'SPINE-RUNTIME-LICENSE.txt',out/'authoring.json',out/'attachment-switches.json',out/'frame-plan.csv',out/'export/megumin.json',out/'export/megumin.spine-json',out/'export/megumin.atlas',out/'export/validation.json',docs/'Spine动画制作指引.md']
files += [out/'export'/name for name in pages]+list(images.glob('*.png'))
files += [out/'references'/(n+'.png') for n in meta['poses']]
files += list((out/'references').glob('*prompt.txt'))+list((out/'source').glob('*prompt.txt'))
files += list((out/'verification').glob('*.json'))
files += [docs/'mod-lab.md']+list((out/'verification/native').glob('*-switches.jpg'))
if (out/'verification/moire').exists():
 files += list((out/'verification/moire').rglob('*.json'))+list((out/'verification/moire').rglob('*.xml'))+list((out/'verification/moire').glob('review-*.jpg'))
manifest={str(p.relative_to(out)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=out/f'megumin-actions-{version}-import.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[out/'manifest.json']:z.write(p,p.relative_to(out))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert not any(n.startswith('research/') for n in z.namelist())
 for name,item in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
print('Import archive:',archive.stat().st_size,'bytes;',len(manifest),'verified entries')
