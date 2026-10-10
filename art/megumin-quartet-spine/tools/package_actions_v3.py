from pathlib import Path
import base64,json,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'actions-v3'
bundle={'skeleton':json.loads((OUT/'export/megumin.json').read_text(encoding='utf-8')),'atlas':(OUT/'export/megumin.atlas').read_text(encoding='utf-8'),'pages':{f.name:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode('ascii') for f in (OUT/'export').glob('*.png')}}
html=(OUT/'index.html').read_text(encoding='utf-8');js=(OUT/'preview.js').read_text(encoding='utf-8')
start=js.index(" const assets=new spine.AssetManager(gl,'export/');");end=js.index(' data=new spine.SkeletonJson',start)
js=js[:start]+''' const packed=JSON.parse(document.getElementById('packed-spine').textContent);
 const raw=packed.skeleton,atlas=new spine.TextureAtlas(packed.atlas);
 await Promise.all(atlas.pages.map(page=>new Promise((resolve,reject)=>{
   const im=new Image();im.onload=()=>{page.setTexture(new spine.GLTexture(gl,im));resolve()};im.onerror=reject;im.src=packed.pages[page.name];
 })));
'''+js[end:]
runtime=(ROOT/'vendor/spine-webgl-4.2.95.min.js').read_text(encoding='utf-8')
html=html.replace('<script src="../vendor/spine-webgl-4.2.95.min.js"></script><script type="module" src="preview.js"></script>', '<script id="packed-spine" type="application/json">'+json.dumps(bundle,separators=(',',':')).replace('</','<\\/')+'</script><script>'+runtime+'</script><script type="module">'+js+'</script>')
(OUT/'preview.html').write_text(html,encoding='utf-8')
if (OUT/'README.md').exists():
    with zipfile.ZipFile(OUT/'megumin-actions-v3-import.zip','w',zipfile.ZIP_DEFLATED) as z:
        for folder in ['export','images']:
            for f in sorted((OUT/folder).glob('*')):
                if f.is_file():z.write(f,f.relative_to(OUT))
        z.write(OUT/'README.md','README.md')
print('Preview:',(OUT/'preview.html').stat().st_size)
