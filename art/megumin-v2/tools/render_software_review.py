"""Offline raster preview of Godot-exported native Polygon2D geometry.
This is not a Godot screen recording. Authored source PNGs are never modified.
"""
from pathlib import Path
import json, math, sys, time, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
DIR=Path(os.getenv('MEGUMIN_RENDER_DIR',str(ROOT/'preview/software')))
DATA=json.loads((DIR/'native_geometry.json').read_text())
W,H=1440,900
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
cache={}
def build_texture(info):
 path=ROOT/info['texture'].replace('res://','')
 im=Image.open(path).convert('RGBA')
 mask=info.get('mask',{})
 if mask:
  alpha=im.getchannel('A')
  cut=Image.new('L',im.size,0);d=ImageDraw.Draw(cut)
  d.polygon([tuple(p) for p in mask['prop_cut']],fill=255)
  d.polygon([tuple(p) for p in mask['hand_keep']],fill=0)
  for keep_key in ['prop_keep_head','prop_keep_leg']:
   if keep_key in mask:d.polygon([tuple(p) for p in mask[keep_key]],fill=0)
  if mask.get('common_lower') and not mask.get('upper_only'):
   d.polygon([tuple(p) for p in mask['leg_cut_left']],fill=255)
   d.polygon([tuple(p) for p in mask['leg_cut_right']],fill=255)
   if mask['lower_clip_y']<im.height:d.rectangle((0,mask['lower_clip_y'],im.width,im.height),fill=255)
   if 'lower_keep' in mask:d.polygon([tuple(p) for p in mask['lower_keep']],fill=0)
  a=np.array(alpha).copy();a[np.asarray(cut)>0]=0
  if mask.get('front_only'):
   keep=Image.new('L',im.size,0);ImageDraw.Draw(keep).polygon([tuple(p) for p in mask['front_polygon']],fill=255)
   a[np.asarray(keep)==0]=0
  im.putalpha(Image.fromarray(a))
 arr=np.asarray(im).astype(np.float32)/255.
 arr[:,:,:3]*=arr[:,:,3,None]
 mips=[arr]
 for k in range(1,5):
  h,w=arr.shape[:2]
  # Proper premultiplied-alpha box mip chain, no broad blur of the original art.
  arr=np.asarray(Image.fromarray((arr*255).round().clip(0,255).astype('uint8'),'RGBA').resize((max(1,w//2),max(1,h//2)),Image.Resampling.BOX)).astype(np.float32)/255.
  mips.append(arr)
 return mips

def sample_bilinear(tex,uv,level):
 scale=2**level
 u=uv[:,0]/scale;v=uv[:,1]/scale
 ix=np.floor(u).astype(np.int32);iy=np.floor(v).astype(np.int32)
 fx=u-ix;fy=v-iy
 ix=np.clip(ix,0,tex.shape[1]-1);iy=np.clip(iy,0,tex.shape[0]-1)
 jx=np.minimum(ix+1,tex.shape[1]-1);jy=np.minimum(iy+1,tex.shape[0]-1)
 return tex[iy,ix]*(1-fx[:,None])*(1-fy[:,None])+tex[iy,jx]*fx[:,None]*(1-fy[:,None])+tex[jy,ix]*(1-fx[:,None])*fy[:,None]+tex[jy,jx]*fx[:,None]*fy[:,None]

def raster_part(canvas,key,points,origin,scale):
 info=DATA['geometry'][key]
 if key not in cache:cache[key]=build_texture(info)
 mips=cache[key]
 uv=np.asarray(info['uv'],dtype=np.float64)
 points=points*scale+origin
 xmin=max(0,int(np.floor(points[:,0].min())));xmax=min(W,int(np.ceil(points[:,0].max()))+1)
 ymin=max(0,int(np.floor(points[:,1].min())));ymax=min(H,int(np.ceil(points[:,1].max()))+1)
 if xmax<=xmin or ymax<=ymin:return
 layer=np.zeros((ymax-ymin,xmax-xmin,4),np.float32)
 for inds in info['triangles']:
  tri=points[inds];textri=uv[inds]
  l=max(xmin,int(np.floor(tri[:,0].min())));r=min(xmax,int(np.ceil(tri[:,0].max()))+1)
  t=max(ymin,int(np.floor(tri[:,1].min())));b=min(ymax,int(np.ceil(tri[:,1].max()))+1)
  if r<=l or b<=t:continue
  # Skip triangles whose source texture is wholly transparent.
  sl=max(0,int(textri[:,0].min())-1);sr=min(mips[0].shape[1],int(textri[:,0].max())+2)
  st=max(0,int(textri[:,1].min())-1);sb=min(mips[0].shape[0],int(textri[:,1].max())+2)
  if sr<=sl or sb<=st or mips[0][st:sb,sl:sr,3].max()==0:continue
  x,y=np.meshgrid(np.arange(l,r)+.5,np.arange(t,b)+.5)
  x=x.ravel();y=y.ravel()
  a,c,e=tri
  den=(c[1]-e[1])*(a[0]-e[0])+(e[0]-c[0])*(a[1]-e[1])
  if abs(den)<1e-8:continue
  wa=((c[1]-e[1])*(x-e[0])+(e[0]-c[0])*(y-e[1]))/den
  wb=((e[1]-a[1])*(x-e[0])+(a[0]-e[0])*(y-e[1]))/den
  wc=1-wa-wb
  mask=(wa>=-1e-6)&(wb>=-1e-6)&(wc>=-1e-6)
  if not mask.any():continue
  sample_uv=wa[mask,None]*textri[0]+wb[mask,None]*textri[1]+wc[mask,None]*textri[2]
  e1=textri[1]-textri[0];e2=textri[2]-textri[0]
  uv_area=abs(e1[0]*e2[1]-e1[1]*e2[0])
  ratio=math.sqrt(abs(den)/max(uv_area,1e-5))
  mip=min(3.99,max(0.,math.log2(1/max(ratio,1e-5))))
  lo=int(mip);mix=mip-lo
  colors=sample_bilinear(mips[lo],sample_uv,lo)*(1-mix)+sample_bilinear(mips[lo+1],sample_uv,lo+1)*mix
  px=np.floor(x[mask]).astype(int)-xmin;py=np.floor(y[mask]).astype(int)-ymin
  layer[py,px]=colors
 dst=canvas[ymin:ymax,xmin:xmax]
 dst[:,:,:3]=layer[:,:,:3]+dst[:,:,:3]*(1-layer[:,:,3,None])
 dst[:,:,3]=1

PHASES={'coil':'01  COIL + BEND','chant':'03  RAISE + CHANT','release':'04  FULL-BODY RELEASE','exhaust':'06  EXHAUST + SETTLE','raise':'02  ELBOW LIFT + OPEN','recover':'05  RELEASE FOLLOW-THROUGH'}
def render_frame(n,save=True):
 frame=DATA['frames'][n]
 im=Image.new('RGB',(W,H),'#090e18');d=ImageDraw.Draw(im)
 d.rectangle((32,108,912,793),fill='#101b2b');d.rectangle((938,108,1408,793),fill='#142133')
 def text(pos,s,size,color):d.text(pos,s,font=ImageFont.truetype(FONT,size),fill=color)
 text((52,31),'MEGUMIN  /  CASTING v2',29,'#f1d5a0')
 text((53,75),'AUTHORED SILHOUETTES + EDITABLE GODOT TIMELINES',13,'#869cba')
 text((54,118),'LARGE MOTION REVIEW',14,'#8aa5c4')
 text((966,118),'320 px CHARACTER REFERENCE',14,'#8aa5c4')
 text((966,152),'ALL VFX OFF  /  1x SPEED',17,'#e2ce9e')
 for y in range(180,748,80):d.line((54,y,887,y),fill='#172638',width=1)
 d.line((54,754,886,754),fill='#3a5067',width=1);d.line((958,726,1386,726),fill='#40586f',width=1)
 for x,y in [(442-443*.42,753),(442+443*.42,753-45*.42)]:d.line((x,y-1,x,y+10),fill='#849cab',width=2)
 for x,y in [(1138-443*320/1100,725),(1138+443*320/1100,725-45*320/1100)]:d.line((x,y-1,x,y+10),fill='#849cab',width=2)
 phase=PHASES[frame['pose']]
 if 1.15<=frame['time']<1.40:phase='03  FULL CHARGE / HOLD'
 text((53,804),phase,23,'#f4ddae');text((1195,808),f"{min(frame['time'],3.5):.2f} s",20,'#cedbeb')
 text((54,848),'Pinned soles  /  No limb scaling  /  No pose crossfade',14,'#849cbb')
 text((940,848),'SOFTWARE RASTER PREVIEW',13,'#d8b780')
 text((940,869),'Godot geometry + timeline; not engine capture',11,'#849cbb')
 d.rectangle((53,782,53+1332*min(frame['time']/3.5,1),785),fill='#d8b780')
 canvas=np.concatenate((np.asarray(im).astype(np.float32)/255.,np.ones((H,W,1),np.float32)),axis=2)
 coords=np.fromfile(DIR/f'frame_{n:04d}.bin',dtype='<f4').reshape(-1,2)
 for origin,scale in [(np.array([442,753]),.42),(np.array([1138,725]),320/1100)]:
  offset=0
  for part in frame['parts']:
   pts=coords[offset:offset+part['count']];offset+=part['count']
   raster_part(canvas,part['key'],pts,origin,scale)
 out=Image.fromarray((canvas[:,:,:3]*255).clip(0,255).astype('uint8'))
 if save:out.save(DIR/f'frame_{n:04d}.png')
 return out
if __name__=='__main__':
 frames=[5,12,29,38,48,68,83] if '--keys' in sys.argv else range(len(DATA['frames']))
 start=time.time()
 if '--parallel' in sys.argv:
  from concurrent.futures import ProcessPoolExecutor
  with ProcessPoolExecutor(max_workers=4) as pool:
   for n,_ in zip(frames,pool.map(render_frame,frames)):
    if n%15==0:print(f'frame {n:04d} / {time.time()-start:.1f}s',flush=True)
 else:
  for n in frames:
   render_frame(n);print(f'frame {n:04d} / {time.time()-start:.1f}s',flush=True)
