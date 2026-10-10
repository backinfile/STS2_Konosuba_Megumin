"""Measure source opacity inside each exported triangle (no artwork edits).

The runtime audit maps these mass/barycentric samples through the actual
deformed mesh. Transparent padding therefore cannot masquerade as anatomy.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]/os.environ.get('MEGUMIN_ACTIONS','actions-v7')
raw=json.loads((root/'export/megumin.json').read_text());images={};result={}
for slot,attachments in raw['skins'][0]['attachments'].items():
 if slot not in ('head','hand_r','leg_l','leg_r','body'):continue
 for name,a in attachments.items():
  path=a['path'];p=root/'source'/('staff-only.png' if path=='staff-master' else path+'.png')
  if path not in images:images[path]=np.asarray(Image.open(p).convert('RGBA'))[:,:,3]/255
  alpha=images[path];h,w=alpha.shape;uv=np.array(a['uvs']).reshape(-1,2)*[w,h];stats=[]
  for ids in np.array(a['triangles']).reshape(-1,3):
   pts=uv[ids];lo=np.maximum(0,np.floor(pts.min(axis=0)).astype(int));hi=np.minimum([w,h],np.ceil(pts.max(axis=0)).astype(int))
   yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xy=np.stack([xx+.5,yy+.5],axis=-1).reshape(-1,2)
   matrix=np.column_stack((pts[0]-pts[2],pts[1]-pts[2]));det=np.linalg.det(matrix)
   if abs(det)<1e-8:stats.append([0,1/3,1/3,1/3]);continue
   bary=(xy-pts[2])@np.linalg.inv(matrix).T;bary=np.column_stack([bary,1-bary.sum(axis=1)])
   mass=alpha[yy,xx].ravel()*np.all(bary>=-1e-7,axis=1);total=mass.sum()
   mean=np.average(bary,weights=mass,axis=0) if total else [1/3]*3
   stats.append([round(float(total/(abs(det)/2)),7),*[round(float(x),7) for x in mean]])
  result[name]=stats
(root/'verification').mkdir(exist_ok=True)
(root/'verification/alpha-triangles.json').write_text(json.dumps(result,separators=(',',':')))
print('Measured',len(result),'attachments')
