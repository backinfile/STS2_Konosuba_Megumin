"""Read-only geometry/animation checks; writes only tests/five_states_* reports."""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/five_states'
DATA=json.loads((OUT/'native_geometry.json').read_text())
METRICS=json.loads((ROOT/'tests/five_states_frame_metrics.json').read_text())
GEOMETRY=json.loads((ROOT/'assets/rig_geometry.json').read_text())
LANDMARKS=GEOMETRY['landmarks']
CHECKS=[]
MEASURES={}

def check(name,passed,value=None,category='numeric'):
    CHECKS.append({'name':name,'passed':bool(passed),'value':value,'category':category})

def cross(a,b): return a[...,0]*b[...,1]-a[...,1]*b[...,0]

def signature(frame): return [(p['key'],p['count'],p['z_index']) for p in frame['parts']]

def run():
    frames=DATA['frames']+DATA['qa_frames']
    expected=['Idle','Cast','Attack','Hit','Relaxed']
    check('only five requested states exported',[s['state'] for s in DATA['segments']]==expected)
    check('30 fps, original timing',DATA['fps']==30 and all(abs(f['time']-i/30)<1e-5 for i,f in enumerate(DATA['frames'])))
    check('no retiming beyond terminal frame rounding',0<=DATA['video_duration']-DATA['duration']<1/30+1e-7,DATA['video_duration']-DATA['duration'])
    check('source hashes unchanged during export',DATA['source_unchanged_during_export'])
    for source,digest in DATA['source_hashes'].items():
        path=ROOT/source.removeprefix('res://')
        check(source+' unchanged after export',hashlib.sha256(path.read_bytes()).hexdigest()==digest)
    for key,part in DATA['geometry'].items():
        path=ROOT/part['texture'].removeprefix('res://')
        check(key+' original source texture unchanged',hashlib.sha256(path.read_bytes()).hexdigest()==part['texture_sha256'])
    check('same visible cutout topology and depth throughout',all(signature(f)==signature(frames[0]) for f in frames))
    vertices=np.asarray([np.fromfile(OUT/f['file'],dtype='<f4').reshape(-1,2) for f in frames],dtype=np.float64)
    check('finite native vertices',np.isfinite(vertices).all())
    transforms=np.asarray([p['transform'] for f in frames for p in f['parts']])
    check('finite exported native transforms',np.isfinite(transforms).all())
    for label,origin,scale,bounds in [
        ('large view',np.array([445.,856.]),.42,(32,108,912,884)),
        ('320 px reference',np.array([1120.,820.]),320/1452,(938,108,1408,884))]:
        mapped=vertices*scale+origin
        lo=mapped.min(axis=(0,1));hi=mapped.max(axis=(0,1))
        check(label+' native geometry stays inside fixed review panel',
              lo[0]>=bounds[0] and lo[1]>=bounds[1] and hi[0]<=bounds[2] and hi[1]<=bounds[3],
              {'minimum':lo.tolist(),'maximum':hi.tolist()})
    check('all bone scales remain one',max(abs(v-1) for m in METRICS for b in m['bones'].values() for v in b['scale'])<1e-5)
    for state in expected:
        chosen=[m for m in METRICS if m['state']==state]
        drops=[m['parameters']['hip_drop'] for m in chosen]
        xs=[m['parameters']['hip_x'] for m in chosen]
        rolls=[m['parameters']['pelvis_roll'] for m in chosen]
        limit=2 if state=='Hit' else 1.5
        check(state+' minimal hip travel',min(drops)>=-1e-6 and max(drops)<=limit+1e-6 and max(map(abs,xs))<=1.000001 and max(map(abs,rolls))==0,{'max_drop':max(drops),'max_abs_x':max(map(abs,xs))})
        check(state+' no death-only controls',all(m['parameters'][p]==0 for m in chosen for p in ['staff_ground_contact','face_state','R_heel_raise','L_heel_raise','cape_collapse']))
        duration=next(seg['duration'] for seg in DATA['segments'] if seg['state']==state)
        terminal=next(m for m in chosen if abs(m['state_time']-duration)<1e-6)
        stance_error=max(math.dist(np.asarray(terminal['ik'][side][part])+[608,1510],LANDMARKS[side+'_'+part])
                         for side in ['R','L'] for part in ['hip','knee','ankle'])
        check(state+' terminal leg stance equals current neutral anatomy',stance_error<.003,stance_error)
    for side in ['R','L']:
        for a,b,label in [('hip','knee','upper'),('knee','ankle','lower')]:
            expected_length=math.dist(LANDMARKS[side+'_'+a],LANDMARKS[side+'_'+b])
            error=max(abs(m['ik'][side][label]-expected_length) for m in METRICS)
            check(side+' '+label+' bone length fixed',error<.001,error)
        for a,b in [('upper','forearm'),('forearm','hand')]:
            lengths=[math.dist(m['bones'][side+'_'+a]['position'],m['bones'][side+'_'+b]['position']) for m in METRICS]
            drift=max(lengths)-min(lengths)
            check(side+' '+a+' arm segment length fixed',drift<.001,drift)
        points=np.asarray([m['bones'][side+'_foot']['position'] for m in METRICS])
        drift=float(np.max(np.abs(points-points[0])))
        check(side+' foot anchor fixed',drift<1e-6,drift)
        reach=max(m['ik'][side]['reach_error'] for m in METRICS)
        check(side+' full-sequence IK reachable',reach<.001,reach)
        rotations=[m['bones'][side+'_foot']['rotation'] for m in METRICS]
        check(side+' foot orientation fixed',max(rotations)-min(rotations)<1e-6)
    offset=0
    for part in frames[0]['parts']:
        name,n=part['key'],part['count']
        v=vertices[:,offset:offset+n];offset+=n
        indices=np.asarray(DATA['geometry'][name]['triangles'])
        tris=v[:,indices]
        areas=cross(tris[:,:,1]-tris[:,:,0],tris[:,:,2]-tris[:,:,0])
        baseline=areas[0]
        significant=np.abs(baseline)>.05
        ratios=areas[:,significant]/baseline[significant]
        minimum=float(ratios.min())
        check(name+' no inverted mesh triangles',minimum>0,minimum)
        MEASURES[name]={'vertex_count':n,'triangle_count':len(indices),'checked_non_degenerate_triangles':int(significant.sum()),'minimum_signed_area_ratio':minimum}
        source=next(p for p in GEOMETRY['parts'] if p['name']==name)
        if not source['bone'].endswith('_leg') and source['bone'] not in ['R_arm_cloth','cape']:
            distances=np.sqrt(np.sum((v[:,:,None,:]-v[:,None,:,:])**2,axis=-1))
            error=float(np.max(np.abs(distances-distances[0])))
            check(name+' rigid shape / no stretch',error<.001,error)
    for b in DATA['boundaries']:
        check(b['from']+' to '+b['to']+' exact continuous boundary',b['max_vertex_delta_px']<.001,b['max_vertex_delta_px'])
    check('Idle 3 s loop including cape closes',DATA['idle_loop_max_vertex_delta_px']<.001,DATA['idle_loop_max_vertex_delta_px'])
    mage=(ROOT/'animations/MageCast.tres').read_text()
    attack=(ROOT/'animations/Attack.tres').read_text()
    check('Attack first 12 tracks exactly preserve MageCast',attack.split('tracks/12/type')[0]==mage.replace('resource_name = "MageCast"','resource_name = "Attack"',1))
    check('Attack impact is single method at 3.5 s',attack.count('"method": &"_emit_attack_impact"')==1 and '"times": PackedFloat32Array(3.5)' in attack)
    for state in expected:
        path=ROOT/'animations'/f'{state}.tres'
        text=path.read_text()
        check(state+' resource exists with correct name',f'resource_name = "{state}"' in text)
        if state!='Attack':check(state+' has no impact method','_emit_attack_impact' not in text)
    rendered='--no-images' not in sys.argv
    if rendered:
        from PIL import Image
        sizes=[]
        for f in frames:
            path=OUT/Path(f['file']).with_suffix('.png')
            if not path.is_file():
                check('all frames rasterized',False,str(path),category='render')
                break
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:sizes.append(im.size)
        else:check('all movie and key frames rasterized',True,len(sizes),category='render')
        check('fixed 1440x960 review canvas',bool(sizes) and all(s==(1440,960) for s in sizes),category='render')
        movie=ROOT/'preview/megumin_v6_five_states_review.mp4'
        if movie.is_file():
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration','-of','json',str(movie)]))['streams'][0]
            check('movie 30 fps / 1440x960 / complete frame count',probe['width']==1440 and probe['height']==960 and probe['r_frame_rate']=='30/1' and int(probe['nb_frames'])==len(DATA['frames']),probe,category='render')
        else:check('review movie exists',False,category='render')
    result={'passed':all(c['passed'] for c in CHECKS),'numeric_frames_tested':len(frames),'movie_frames':len(DATA['frames']),'exact_keyframes':len(DATA['qa_frames']),'render_validation_run':rendered,'visual_review':'Manual key-PNG inspection is separate; see tests/five_states_visual_review.md when present.','scope':DATA['scope'],'checks':CHECKS,'measurements':MEASURES}
    (ROOT/'tests/five_states_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'passed':result['passed'],'checks':len(CHECKS),'numeric_frames':len(frames),'render_validation_run':rendered,'failed':[c for c in CHECKS if not c['passed']]},indent=2))
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':run()
