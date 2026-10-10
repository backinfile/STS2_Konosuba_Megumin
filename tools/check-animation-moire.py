"""Run Mi-Ripple on original-size assets; keep candidates separate for visual review.

Usage: .local/moire-env/Scripts/python tools/check-animation-moire.py
Mi-Ripple is installed in the project-local environment, never globally.
"""
import concurrent.futures, hashlib, json, subprocess, os
from pathlib import Path
from PIL import Image
from mi_ripple.pipeline import run

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')
OUT=ART/'verification/moire'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check(source):
    rel=source.relative_to(ART);dest=OUT/rel.parent/source.stem
    sidecar=dest/(source.stem+'_restored.json')
    result=json.loads(sidecar.read_text()) if sidecar.exists() else None
    if result is None or result['source_sha256']!=sha(source):
        result=run(source,dest,allow_regen=False,max_regen=0)
    candidate=result.get('final')
    row={'input':str(rel).replace('\\','/'),'sha256':sha(source),'outcome':result['outcome'],
         'actions':[s['action'] for s in result['steps']],'source_copy':result['final_is_source_copy'],
         'report':str(sidecar.relative_to(ART)).replace('\\','/'),'candidate':None}
    if candidate:
        original=Image.open(source).convert('RGBA');filtered=Image.open(candidate).convert('RGBA')
        assert original.size==filtered.size,(source,'dimensions changed')
        # The tool's filtering path is RGB-only. Restore the exact source alpha;
        # this candidate still requires review before it can enter a build.
        filtered.putalpha(original.getchannel('A'))
        rgba=dest/(source.stem+'_candidate-rgba.png');filtered.save(rgba)
        assert filtered.getchannel('A').tobytes()==original.getchannel('A').tobytes()
        row.update(candidate=str(rgba.relative_to(ART)).replace('\\','/'),
                   pixels_unchanged=filtered.tobytes()==original.tobytes(),alpha_unchanged=True)
    print(json.dumps(row),flush=True)
    return row

if __name__=='__main__':
    sources=sorted(p for folder in ['source','references'] for p in (ART/folder).glob('*.png'))
    OUT.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:rows=list(pool.map(check,sources))
    commit=subprocess.check_output(['git','-C',str(ROOT/'.local/tools/Mi-Ripple'),'rev-parse','HEAD'],text=True).strip()
    report={'tool':'Mi-Ripple','version':'0.1.0','commit':commit,'native_resolution':True,'regeneration':False,
            'assets':rows,'visual_review':'pending; candidates have not been adopted'}
    (ART/'verification/moire.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Completed',len(rows),'original-size checks.')
