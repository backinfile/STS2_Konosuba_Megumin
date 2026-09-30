"""Diagnostic image composition only; never modifies source artwork."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_software_review as render
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'preview/leg_review';OUT.mkdir(exist_ok=True)
SNAP=ROOT.parent/'megumin-art-v3-snapshots/bf0e567'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
M=json.loads((ROOT/'tests/frame_metrics.json').read_text());R=json.loads((ROOT/'assets/rig_geometry.json').read_text())['rests']
DELTA=np.array(M[0]['bones']['head']['position'])+np.array([575,1508])-np.array(R['head'])

def native(n,snapshot=False,W=1400,H=1140,origin=(0,0),scale=.63):
 data=json.loads(((SNAP if snapshot else ROOT/'preview/software')/'native_geometry.json').read_text())
 render.DATA=data;render.W=W;render.H=H;render.cache.clear()
 canvas=np.zeros((H,W,4),np.float32);canvas[:,:,:3]=np.array([16,27,43])/255.;canvas[:,:,3]=1
 coords=np.fromfile((SNAP if snapshot else ROOT/'preview/software')/f'frame_{n:04d}.bin',dtype='<f4').reshape(-1,2)
 offset=0
 for p in data['frames'][n]['parts']:
  v=coords[offset:offset+p['count']];offset+=p['count'];render.raster_part(canvas,p['key'],v,np.asarray(origin),scale)
 return Image.fromarray(np.uint8((canvas[:,:,:3]*255).clip(0,255)))

def source_compare():
 W,H=1440,1160;scale=.63;dxy=DELTA
 im=native(0,True,W,H,np.array([755,120])+(np.array([575,1508])-dxy)*scale,scale)
 src=Image.open(ROOT/'assets/source/megumin_master.png').convert('RGBA').resize((645,968),Image.Resampling.LANCZOS)
 im.paste(src,(30,120),src)
 d=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,22)
 d.text((30,22),'SOURCE vs DELIVERED v3 / SAME HEAD SCALE + POSITION',font=ImageFont.truetype(FONT,29),fill='#f4ddae')
 d.text((30,76),'Original mother art',font=font,fill='#ccd9e7');d.text((755,76),'Delivered v3 natural idle',font=font,fill='#ccd9e7')
 points={'waist':[619,701],'L hip':[548,848],'R hip':[681,857],'L knee':[463,1053],'R knee':[720,1059],'L cuff':[348,1243],'R cuff':[779,1241]}
 bones={'waist':'torso','L hip':'thigh_left','R hip':'thigh_right','L knee':'shin_left','R knee':'shin_right','L cuff':'boot_left','R cuff':'boot_right'}
 report={}
 for name,p in points.items():
  q=np.array(M[0]['bones'][bones[name]]['position'])+np.array([575,1508])-dxy
  report[name]={'source':p,'v3_head_aligned':q.tolist(),'delta':(q-p).tolist()}
  for org,v in [(np.array([30,120]),np.array(p)),(np.array([755,120]),q)]:
   x,y=org+v*scale;d.ellipse((x-4,y-4,x+4,y+4),fill='#55dedc');d.text((x+6,y-15),name,font=ImageFont.truetype(FONT,13),fill='#71e9e2')
 d.text((30,1110),'Bone lengths unchanged. At the same head: waist ~0 px; knee height -1.76 / +5.75 px; soles +14.28 px.',font=ImageFont.truetype(FONT,17),fill='#d9c299')
 im.save(OUT/'source_vs_delivered_same_head.png')
 (OUT/'source_proportion_measurements.json').write_text(json.dumps({'head_translation_source_to_v3':dxy.tolist(),'landmarks':report},indent=2))

if __name__=='__main__':source_compare()
