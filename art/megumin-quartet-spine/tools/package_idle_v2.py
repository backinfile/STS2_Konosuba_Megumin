"""Package the faithful idle and an offline before/after viewer."""
from pathlib import Path
import base64
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'idle-v2'
def bundle(folder,name):
    return dict(skeleton=json.loads((folder/f'{name}.json').read_text(encoding='utf-8')),
                atlas=(folder/f'{name}.atlas').read_text(encoding='utf-8'),
                pages={f.name:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode('ascii') for f in folder.glob('*.png')})
packed=dict(current=bundle(OUT/'export','megumin-idle'),legacy=bundle(ROOT/'export','megumin'),
            meta=json.loads((OUT/'export/manifest.json').read_text(encoding='utf-8')),
            validation=json.loads((OUT/'export/validation.json').read_text(encoding='utf-8')))
html=(OUT/'preview-template.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(packed,separators=(',',':')).replace('</','<\\/')).replace('__RUNTIME__',(ROOT/'vendor/spine-webgl-4.2.95.min.js').read_text(encoding='utf-8')).replace('__JS__',(OUT/'preview.js').read_text(encoding='utf-8'))
(OUT/'preview.html').write_text(html,encoding='utf-8')
with zipfile.ZipFile(OUT/'megumin-idle-v2-import.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for folder in ['export','images']:
        for f in sorted((OUT/folder).iterdir()):
            if f.is_file():archive.write(f,f.relative_to(OUT))
    archive.write(OUT/'README.md','README.md')
print('Offline preview:',(OUT/'preview.html').stat().st_size,'bytes')
print('Spine import archive:',(OUT/'megumin-idle-v2-import.zip').stat().st_size,'bytes')
