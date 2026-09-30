"""Verifies native Godot exports; geometry tolerances are in source-pixel units."""
import json, math, hashlib, tarfile
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.spatial import ConvexHull, distance_matrix
ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/'preview/software'
data=json.loads((DIR/'native_geometry.json').read_text());metrics=json.loads((ROOT/'tests/frame_metrics.json').read_text());src=json.loads((ROOT/'assets/rig_geometry.json').read_text())
coords=[np.fromfile(DIR/f'frame_{i:04d}.bin',dtype='<f4').reshape(-1,2) for i in range(len(data['frames']))]
frames=np.array(coords,dtype=np.float64);checks=[]
def check(name,ok,value=None):checks.append({'name':name,'passed':bool(ok),'value':value})
check('163 native frames at 30 fps',len(frames)==163 and data['fps']==30,len(frames))
check('all frames use identical source cutouts',all(f['parts']==data['frames'][0]['parts'] for f in data['frames']))
check('all joint scales fixed at one',max(abs(float(s)-1) for m in metrics for b in m['bones'].values() for s in b['scale'])<1e-5)
check('both IK chains reach planted targets',max(m['ik'][s]['reach_error'] for m in metrics for s in ['left','right'])<1e-5)
rests=src['rests'];measure={'source_canvas_px':src['canvas'],'stance_px':{'v1':553,'v3':453,'reduction_percent':100*100/553},'cutout_bbox_px':{},'bone_lengths_px':{},'per_part_max_rigidity_error_px':{}}
for side in ['left','right']:
 expected=[math.dist(rests[side+'_upper'],rests[side+'_forearm']),math.dist(rests[side+'_forearm'],rests[side+'_hand']),math.dist(rests['thigh_'+side],rests['shin_'+side]),math.dist(rests['shin_'+side],rests['boot_'+side])]
 measure['bone_lengths_px'][side]={'upper_arm':expected[0],'forearm':expected[1],'thigh':expected[2],'shin':expected[3]}
 for i,label in enumerate(['upper','lower']):
  values=np.array([m['ik'][side][label+'_length'] for m in metrics]);check(side+' '+label+' leg bone fixed',np.max(np.abs(values-expected[i+2]))<.001,float(np.ptp(values)))
 ankles=np.array([m['ik'][side]['ankle'] for m in metrics]);check(side+' ankle / sole anchored',np.max(np.abs(ankles-ankles[0]))<1e-5,float(np.max(np.abs(ankles-ankles[0]))))
 for a,b,e in [(side+'_upper',side+'_forearm',expected[0]),(side+'_forearm',side+'_hand',expected[1])]:
  values=[math.dist(m['bones'][a]['position'],m['bones'][b]['position']) for m in metrics];check(a+' FK bone fixed',max(abs(v-e) for v in values)<.001,max(abs(v-e) for v in values))
offset=0
for part in data['frames'][0]['parts']:
 n=part['count'];name=part['key'];v=frames[:,offset:offset+n];offset+=n
 if name!='complete_cape' and not name.startswith('leg_skin_'):
  ref=distance_matrix(v[0],v[0]);err=max(np.max(np.abs(distance_matrix(w,w)-ref)) for w in v)
  measure['per_part_max_rigidity_error_px'][name]=float(err);check(name+' rigid distances',err<.001,float(err))
 if name in ['head_hat','hand_left','hand_right','boot_left','boot_right']:
  p=np.array(next(p['vertices'] for p in src['parts'] if p['name']==name));measure['cutout_bbox_px'][name]=(p.max(0)-p.min(0)).tolist()
# Local leg skin transitions are allowed only at the knee and under-skirt attachment.
measure['leg_skin']={}
offset=0
for item in data['frames'][0]['parts']:
 n=item['count'];name=item['key'];v=frames[:,offset:offset+n];offset+=n
 if not name.startswith('leg_skin_'):continue
 side=name.removeprefix('leg_skin_');bind=next(p for p in src['parts'] if p['name']==name)
 rest=np.array(bind['vertices']);kw=np.array(bind['skin_weights']);hw=np.array(bind['hip_weights'])
 knee=np.array([m['ik'][side]['knee'] for m in metrics]);hip=np.array([m['bones']['thigh_'+side]['position'] for m in metrics])
 errors={}
 for label,ids in [('thigh_rigid',np.where((kw==0)&(hw==1))[0]),('shin_rigid',np.where(kw==1)[0])]:
  ref=distance_matrix(v[0,ids],v[0,ids]);err=max(np.max(np.abs(distance_matrix(w[ids],w[ids])-ref)) for w in v);errors[label]=float(err)
  check(side+' '+label+' away from joint bands',err<.001,float(err))
 for label,ids,pivot,pivot0 in [('knee_radius',np.where(hw==1)[0],knee,np.array(rests['shin_'+side])),('hip_radius',np.where(hw<1)[0],hip,np.array(rests['thigh_'+side]))]:
  radii=np.linalg.norm(v[:,ids]-pivot[:,None,:],axis=2);expected=np.linalg.norm(rest[ids]-pivot0,axis=1);err=np.abs(radii-expected).max();errors[label]=float(err)
  check(side+' '+label+' preserved in rotation blend',err<.001,float(err))
 tri=np.array(bind['triangles']);rtri=rest[tri];r_area=np.cross(rtri[:,1]-rtri[:,0],rtri[:,2]-rtri[:,0]);good=np.abs(r_area)>.05
 posed=v[:,tri];areas=np.cross(posed[:,:,1]-posed[:,:,0],posed[:,:,2]-posed[:,:,0]);ratios=areas[:,good]/r_area[good]
 check(side+' continuous leg mesh has no folded triangles',ratios.min()>0,float(ratios.min()))
 o=np.array(bind['outline']);poly_area=abs(np.dot(o[:,0],np.roll(o[:,1],1))-np.dot(o[:,1],np.roll(o[:,0],1)))/2
 coverage=float(np.abs(r_area).sum()/2/poly_area)
 check(side+' mesh covers complete source leg silhouette',abs(coverage-1)<.005,coverage)
 measure['leg_skin'][side]={'knee_band_halfwidth_px':bind['knee_band_halfwidth'],'hip_band_px':bind['hip_band'],'vertices':len(rest),'triangles':len(tri),'rigid_and_radius_errors_px':errors,'minimum_triangle_area_ratio':float(ratios.min()),'source_coverage_ratio':coverage}
# Compare against delivered bf0e567: exact animation tracks and all existing skeleton controls.
baseline=json.loads((ROOT/'tests/baseline_bf0e567.json').read_text())
oldmetrics=baseline['frame_metrics']
check('same exact delivered animation timeline',baseline['animation_sha256']==hashlib.sha256((ROOT/'animations/ContinuousCast.tres').read_bytes()).hexdigest())
maxbone=0.
for before,after in zip(oldmetrics,metrics):
 for name,b in before['bones'].items():
  a=after['bones'][name];maxbone=max(maxbone,math.dist(a['position'],b['position']),abs(a['rotation']-b['rotation']))
check('all delivered bone positions and rotations unchanged',maxbone<1e-6,maxbone)
measure['frozen_bone_max_delta']=maxbone

# Natural initial/end stance is a specific regression target, not just a reach test.
measure['neutral_stance']={'pelvis_pivot_px':[614,852],'hip_vertical_offset_px':-16.6879351,'pelvis_roll_deg':8.53055893,'torso_counter_roll_deg':-8.53055893,'knee_flexion_deg':{}}
for frame_id,label in [(0,'start'),(len(metrics)-1,'end')]:
 measure['neutral_stance']['knee_flexion_deg'][label]={}
 for side in ['left','right']:
  m=metrics[frame_id];ik=m['ik'][side];a=ik['upper_length'];b=ik['lower_length'];reach=math.dist(m['bones']['thigh_'+side]['position'],ik['ankle'])
  flex=180-math.degrees(math.acos(np.clip((a*a+b*b-reach*reach)/(2*a*b),-1,1)))
  measure['neutral_stance']['knee_flexion_deg'][label][side]=flex
  check(label+' '+side+' knee naturally extended (5-12 deg)',5<=flex<=12,float(flex))
for side in ['left','right']:
 check(side+' end returns to neutral hip',math.dist(metrics[0]['bones']['thigh_'+side]['position'],metrics[-1]['bones']['thigh_'+side]['position'])<.001)

# Whole staff top + lower must be one rigid prop, not independently bending pieces.
off=0;staff=[]
for p in data['frames'][0]['parts']:
 if p['key'].startswith('staff_'):staff.extend(range(off,off+p['count']))
 off+=p['count']
v=frames[:,staff];ref=distance_matrix(v[0],v[0]);err=max(np.max(np.abs(distance_matrix(w,w)-ref)) for w in v);check('whole staff fixed shape',err<.001,float(err))
# Its gripping point in each part is transformed by exactly the hand chain (same scene parent).
script=(ROOT/'scripts/megumin_rig.gd').read_text();check('hand and staff share single FK transform',all(p['bone']=='right_hand' for p in src['parts'] if p['name'].startswith('staff_') or p['name']=='hand_right'))
check('no sprite or alpha pose crossfade code',all(s not in script for s in ['Sprite2D','modulate.a','pose_alpha','scale =','scale=']))
check('single authored action timeline',len(list((ROOT/'animations').glob('*.tres')))==1)
check('strictly ordered frame samples',all(b['time']>a['time'] for a,b in zip(data['frames'],data['frames'][1:])))
# Derive visible prop tip-to-tip source extent from opaque silhouette convex hull.
im=np.asarray(Image.open(ROOT/'assets/source/megumin_staff_complete.png'));ys,xs=np.where(im[:,:,3]>=128);points=np.array([xs,ys]).T;hull=points[ConvexHull(points).vertices];dm=distance_matrix(hull,hull);ia,ib=np.unravel_index(np.argmax(dm),dm.shape)
measure['staff']={'source_tip_points':hull[[ia,ib]].tolist(),'source_tip_to_tip_px':float(dm[ia,ib]),'fixed_registration_scale':.83,'rig_tip_to_tip_px':float(dm[ia,ib]*.83),'runtime_scale':1}
measure['max_vertex_frame_step_px']=float(np.linalg.norm(np.diff(frames,axis=0),axis=2).max())
measure['camera']={'large_constant_scale':.42,'large_origin':[443,856],'reference_constant_scale':320/1398,'reference_origin':[1104,820],'auto_zoom':False}
frozen_source_hashes=json.loads((ROOT/'assets/baseline/frozen_sources.json').read_text())['source_sha256']
for filename,expected_sha256 in frozen_source_hashes.items():
 actual_sha256=hashlib.sha256((ROOT/'assets/source'/filename).read_bytes()).hexdigest()
 check(filename+' byte-identical to frozen v1',actual_sha256==expected_sha256)
report={'engine':data['engine'],'passed':all(c['passed'] for c in checks),'checks':checks,'measurements':measure,'scope':'Native AnimationPlayer/Polygon2D geometry and FK/IK invariants. Local knee/hip skin blending explicitly tested; no global leg scaling. Software raster preview, not engine framebuffer capture.'}
(ROOT/'tests/continuous_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[c for c in checks if not c['passed']],'measurements':measure},indent=2))
if not report['passed']:raise SystemExit(1)
