from pathlib import Path
import json,math,hashlib
import numpy as np
from scipy.spatial import distance_matrix
R=Path(__file__).resolve().parents[1];G=json.loads((R/'assets/rig_geometry.json').read_text());D=json.loads((R/'preview/software/native_geometry.json').read_text());M=json.loads((R/'tests/frame_metrics.json').read_text());P=G['landmarks']
F=np.array([np.fromfile(R/'preview/software'/f'frame_{i:04d}.bin',dtype='<f4').reshape(-1,2) for i in range(len(D['frames']))],float)
checks=[];measures={}
def ck(name,ok,value=None):checks.append({'name':name,'passed':bool(ok),'value':value})
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
ck('217 native frames / 30fps / 7.2s',len(F)==217 and D['fps']==30 and abs(D['frames'][-1]['time']-7.2)<1e-5)
ck('approved mother source unchanged',hashlib.sha256((R/'assets/source/megumin_master_v6.png').read_bytes()).hexdigest()==G['source_sha256'])
ck('single cutout identity throughout',all(f['parts']==D['frames'][0]['parts'] for f in D['frames']))
ck('all bone scales remain one',max(abs(x-1) for m in M for b in m['bones'].values() for x in b['scale'])<1e-5)
for side in ['R','L']:
 for a,b,name in [('hip','knee','upper'),('knee','ankle','lower')]:
  expected=math.dist(P[side+'_'+a],P[side+'_'+b]);error=max(abs(m['ik'][side][name]-expected) for m in M);ck(side+' '+name+' bone fixed',error<.001,error)
 for a,b in [('upper','forearm'),('forearm','hand')]:
  vals=[math.dist(m['bones'][side+'_'+a]['position'],m['bones'][side+'_'+b]['position']) for m in M];ck(side+' '+a+' arm length fixed',max(vals)-min(vals)<.001,max(vals)-min(vals))
 pts=np.array([m['bones'][side+'_foot']['position'] for m in M]);ck(side+' true-ankle foot anchor fixed',np.max(abs(pts-pts[0]))<1e-6,float(np.max(abs(pts-pts[0]))))
 ck(side+' IK reachable',max(m['ik'][side]['reach_error'] for m in M)<.001,max(m['ik'][side]['reach_error'] for m in M))
 for i,label in [(0,'start'),(-1,'end')]:
  err=max(math.dist(np.array(M[i]['ik'][side][part])+[608,1510],P[side+'_'+part]) for part in ['hip','knee','ankle']);ck(side+' '+label+' matches mother anatomical stance',err<.003,err)
# Every non-skinned anatomy piece is rigid; leg local transitions must remain unflipped.
off=0
for item in D['frames'][0]['parts']:
 n=item['count'];name=item['key'];v=F[:,off:off+n];off+=n;p=next(p for p in G['parts'] if p['name']==name)
 if p['bone'].endswith('_leg') or p['bone']=='R_arm_cloth':
  rest=np.array(p['vertices']);tri=np.array(p['triangles']);q=rest[tri];area=cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);good=abs(area)>.05
  posed=v[:,tri];ar=cross(posed[:,:,1]-posed[:,:,0],posed[:,:,2]-posed[:,:,0]);rat=ar[:,good]/area[good];worst=float(rat.min())
  ck(name+' no folded mesh triangles',worst>0,worst);measures[name]={'vertices':n,'min_triangle_area_ratio':worst}
 elif p['bone']!='cape':
  ref=distance_matrix(v[0],v[0]);err=max(np.max(abs(distance_matrix(q,q)-ref)) for q in v);ck(name+' rigid shape',err<.001,float(err))
angles=np.degrees([m['bones']['R_hand']['rotation'] for m in M]);measures['staff_global_rotation_deg']=[float(angles.min()),float(angles.max())]
ck('staff stays near upright, no horizontal swing',angles.max()<40 and angles.min()>-15,measures['staff_global_rotation_deg'])
report={'passed':all(x['passed'] for x in checks),'checks':checks,'measurements':measures,'scope':'Godot native transforms and UV meshes; offline software raster preview is not engine framebuffer capture.'}
(R/'tests/v6_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'count':len(checks),'failed':[x for x in checks if not x['passed']],'measurements':measures},indent=2))
