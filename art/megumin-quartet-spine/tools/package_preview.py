"""Build an offline HTML preview and a compact editor-import archive."""
from pathlib import Path
import base64
import json
import zipfile
import shutil

root=Path(__file__).resolve().parents[1]
bundle={
    "skeleton":json.loads((root/'export/megumin.json').read_text(encoding='utf-8')),
    "atlas":(root/'export/megumin.atlas').read_text(encoding='utf-8'),
    "pages":{p.name:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii') for p in (root/'export').glob('*.png')},
}
html=(root/'index.html').read_text(encoding='utf-8')
js=(root/'preview.js').read_text(encoding='utf-8')
start=js.index(" const assets=new spine.AssetManager(gl,'export/');")
end=js.index(' data=new spine.SkeletonJson',start)
js=js[:start]+''' const packed=JSON.parse(document.getElementById('packed-spine').textContent);
 const raw=packed.skeleton,atlas=new spine.TextureAtlas(packed.atlas);
 await Promise.all(atlas.pages.map(page=>new Promise((resolve,reject)=>{
   const im=new Image();im.onload=()=>{page.setTexture(new spine.GLTexture(gl,im));resolve()};im.onerror=reject;im.src=packed.pages[page.name];
 })));
'''+js[end:]
runtime=(root/'vendor/spine-webgl-4.2.95.min.js').read_text(encoding='utf-8')
html=html.replace('<script src="vendor/spine-webgl-4.2.95.min.js"></script><script type="module" src="preview.js"></script>',
    '<script type="application/json" id="packed-spine">'+json.dumps(bundle,separators=(',',':')).replace('</','<\\/')+'</script>\n<script>'+runtime+'</script>\n<script type="module">'+js+'</script>')
(root/'preview.html').write_text(html,encoding='utf-8')
shutil.copyfile(root.parent/'megumin-concepts-20261009/quartet/motion-design.html',root/'motion-design-reference.html')
with zipfile.ZipFile(root/'megumin-spine-import.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ['export','images']:
        for p in sorted((root/folder).glob('*')):
            if p.is_file():z.write(p,p.relative_to(root))
    z.write(root/'README.md','README.md')
print('Offline preview:',(root/'preview.html').stat().st_size,'bytes')
print('Import archive:',(root/'megumin-spine-import.zip').stat().st_size,'bytes')
