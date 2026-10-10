"""Fail packaging if active animation art has no reviewed original-size check."""
from pathlib import Path
import hashlib,json,os
root=Path(__file__).resolve().parents[1]/os.environ.get('MEGUMIN_ACTIONS','actions-v8')
report=json.loads((root/'verification/moire.json').read_text(encoding='utf-8'))
assert report['native_resolution'] and report['visual_review']['reviewed'],'Visual moire review is incomplete'
rows={a['input']:a for a in report['assets']}
meta=json.loads((root/'authoring.json').read_text(encoding='utf-8'))
files=list((root/'source').glob('*.png'))+[root/'references'/(name+'.png') for name in meta['poses']]
for file in files:
    name=file.relative_to(root).as_posix();row=rows[name]
    assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'],f'Recheck changed image: {name}'
    assert row['disposition']=='preserve_original' and row['source_copy'] and row['pixels_unchanged'],f'Review and record adoption before building: {name}'
    assert row['alpha_unchanged'],f'Alpha changed: {name}'
print(f'Moire provenance: {len(files)} active assets checked, original pixels retained.')
