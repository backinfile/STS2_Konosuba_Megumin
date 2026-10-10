"""Alternate-pose mesh rig from independently drawn animation references.

Source pixels are preserved. Pillow only copies them to padded atlas pages.
Each drawing is partitioned into local mesh slots; every mesh is bound in its
own reference pose. Standing pieces share an anatomical cage; large poses
isolate limb cages and preserve sleeve overlap at the shoulders.
The single unchanged staff is a rigid mesh parented to the right grip.
"""
from pathlib import Path
import sys,json,math,shutil,copy,csv
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.build-deps'))
import numpy as np
from PIL import Image
from shapely.geometry import Polygon,Point,box,MultiPoint,LineString,GeometryCollection
from shapely.ops import triangulate
import mapbox_earcut
from v7_pose_data import POSES,HANDS,ARM_R,ARM_L,HEADS,ENTRY,FALL,RECOVER,S

OUT=globals().get('OUT_OVERRIDE',ROOT/'actions-v7');EX=OUT/'export'
STABILIZE=globals().get('STABILIZE_PARTS',False)
FLOW=globals().get('CONTINUOUS_MOTION',False)
if FLOW:from v9_motion import Motion
EX.mkdir(exist_ok=True,parents=True)

if STABILIZE:
 from shapely import contains_xy
 head_measurements={};hand_measurements={}
 for name,p in POSES.items():
  alpha=np.asarray(Image.open(OUT/'source'/(name+'.png')).convert('RGBA'))[:,:,3]
  ys,xs=np.nonzero(alpha>32)
  keep=contains_xy(Polygon(HEADS[name]).buffer(0),xs+.5,ys+.5)
  xs,ys=xs[keep]+.5,ys[keep]+.5;mass=alpha[ys.astype(int),xs.astype(int)]/255
  head_measurements[name]=(float(mass.sum()),(float(np.average(xs,weights=mass)),float(np.average(ys,weights=mass))))
  ys,xs=np.nonzero(alpha>32)
  keep=contains_xy(Polygon(HANDS[name]).buffer(0),xs+.5,ys+.5)
  xs,ys=xs[keep]+.5,ys[keep]+.5;mass=alpha[ys.astype(int),xs.astype(int)]/255
  hand_measurements[name]=(float(mass.sum()),(float(np.average(xs,weights=mass)),float(np.average(ys,weights=mass))))
 for name,p in POSES.items():
  p['reference_scale']=p['scale']
  p['scale']=S*math.sqrt(head_measurements['E00'][0]/head_measurements[name][0])
  p['head_pivot']=head_measurements[name][1]
def rnd(x):return round(float(x),5)
def rot(v,a):
 r=math.radians(a);c,s=math.cos(r),math.sin(r)
 return(v[0]*c-v[1]*s,v[0]*s+v[1]*c)
def sub(a,b):return(a[0]-b[0],a[1]-b[1])
def ang(a,b):return math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
def smooth(x):return x*x*(3-2*x)
def world(p,xy):return((xy[0]-p['origin'][0])*p['scale'],(p['origin'][1]-xy[1])*p['scale'])
PARENTS={'root':None,'pelvis':'root','chest':'pelvis','head':'chest','cape_l':'chest','cape_r':'chest','upper_r':'chest','fore_r':'upper_r','hand_r':'fore_r','staff':'hand_r','upper_l':'chest','fore_l':'upper_l','hand_l':'fore_l','thigh_r':'pelvis','shin_r':'thigh_r','foot_r':'shin_r','thigh_l':'pelvis','shin_l':'thigh_l','foot_l':'shin_l'}
if STABILIZE:PARENTS['neck']='chest'
HEAD_CAGE=[(-100,0),(100,0),(-105,95),(105,95),(-65,170),(65,170)]
HAND_CAGE=[(-10,-10),(10,-10),(-10,10),(10,10)]
for i in range(len(HEAD_CAGE)):PARENTS['head_cage_'+str(i)]='head'
for i in range(len(HAND_CAGE)):PARENTS['grip_cage_'+str(i)]='hand_r'
for i in range(len(HAND_CAGE)):PARENTS['left_grip_cage_'+str(i)]='hand_l'
for i in range(4):PARENTS['frame_cage_'+str(i)]='root'
for s in 'rl':
 PARENTS['toe_'+s]='foot_'+s
 for limb,parent in [('arm','upper_'+s),('leg','thigh_'+s)]:
  for i in range(6):PARENTS[f'{limb}_{s}_edge_{i}']=parent
NAMES=list(PARENTS);BID={n:i for i,n in enumerate(NAMES)}
def transforms(p):
 q={k:world(p,v) for k,v in p['points'].items()};out={'root':(0,0,0)}
 body=ang(q['pelvis'],q['chest'])-90
 for name,k,r in [('pelvis','pelvis',body*.4),('chest','chest',body),('head','neck',p['head']),('cape_l','cape1',body*.4),('cape_r','cape2',body*.3)]:out[name]=(*q[k],p['head'] if name=='head' else 0)
 if STABILIZE:
  out['neck']=(*q['neck'],0)
  out['head']=(*world(p,p['head_pivot']),p['head'])
 for s in 'rl':
  for n,a,b in [('upper','s','e'),('fore','e','g'),('thigh','h','k'),('shin','k','a'),('foot','a','t')]:out[n+'_'+s]=(*q[a+s],0)
  out['hand_'+s]=(*q['g'+s],p['staff']-108 if s=='r' else ang(q['e'+s],q['g'+s]))
  out['toe_'+s]=(*q['t'+s],0)
  for limb,keys,widths in [('arm',['s','e','g'],[12,10,8]),('leg',['h','k','a'],[12,11,13])]:
   for j,(k,width) in enumerate(zip(keys,widths)):
    other=keys[j+1] if j<2 else keys[j-1]
    r=ang(q[k+s],q[other+s])+(90 if j<2 else -90)
    for z,sign in enumerate([-1,1]):
     dx,dy=rot((width*sign,0),r);out[f'{limb}_{s}_edge_{j*2+z}']=(q[k+s][0]+dx,q[k+s][1]+dy,0)
 out['staff']=(*q['gr'],p['staff'])
 for i,v in enumerate(HEAD_CAGE):
  v=rot(v,p['head']);out['head_cage_'+str(i)]=(q['neck'][0]+v[0],q['neck'][1]+v[1],0)
 for i,v in enumerate(HAND_CAGE):
  v=rot(v,p['staff']-108);out['grip_cage_'+str(i)]=(q['gr'][0]+v[0],q['gr'][1]+v[1],0)
 for i,v in enumerate(HAND_CAGE):
  v=rot(v,ang(q['el'],q['gl'])+90);out['left_grip_cage_'+str(i)]=(q['gl'][0]+v[0],q['gl'][1]+v[1],0)
 for i,v in enumerate([(-500,-400),(500,-400),(-500,700),(500,700)]):out['frame_cage_'+str(i)]=(*v,0)
 return out
def locals_from(w):
 r={}
 for n,parent in PARENTS.items():
  a=w[n]
  if parent is None:r[n]=a;continue
  b=w[parent];xy=rot(sub(a,b),-b[2]);r[n]=(*xy,((a[2]-b[2]+180)%360)-180)
 return r
WORLD={n:transforms(p) for n,p in POSES.items()}
HAND_TRANSFORMS={}
if STABILIZE:
 base_area,base_center=hand_measurements['E00']
 canonical=rot(sub(world(POSES['E00'],base_center),WORLD['E00']['hand_r']),-WORLD['E00']['hand_r'][2])
 for name,p in POSES.items():
  area,center=hand_measurements[name]
  factor=math.sqrt(base_area/area)*POSES['E00']['scale']/p['scale']
  offset=rot(canonical,WORLD[name]['hand_r'][2]);source_center=world(p,center)
  HAND_TRANSFORMS[name]=dict(scale=factor,translation=[WORLD[name]['hand_r'][i]+offset[i]-source_center[i]*factor for i in (0,1)])
LOCAL={n:locals_from(w) for n,w in WORLD.items()};SETUP=LOCAL['E00']
bones=[dict(name=n,**({'parent':PARENTS[n]} if PARENTS[n] else {}),x=rnd(SETUP[n][0]),y=rnd(SETUP[n][1]),rotation=rnd(SETUP[n][2])) for n in NAMES]

# Continuous piecewise affine weights, authored around anatomical landmarks.
# Unlike a nearest-limb classifier this field cannot acquire saw-tooth seams
# when neighboring vertices happen to choose a different limb. The anchors are
# actual Spine bones. UV parts remain independently replaceable attachments.
CAGES={};WEIGHT_CACHE={}
for name,w in WORLD.items():
 for region in ['all','standing','body','arm_r','arm_l','leg_r','leg_l']:
  if region in ('all','standing'):
   keep=[bn for bn in w if bn not in ('root','staff') and not bn.startswith(('frame_cage','grip_cage','left_grip_cage','arm_','leg_'))]
   keep=[bn for bn in keep if bn not in (('fore_l','hand_l','fore_r','hand_r') if region=='all' else ('fore_l','hand_l'))]
  elif region=='body':keep=['pelvis','chest','head','cape_l','cape_r','upper_r','upper_l','thigh_r','thigh_l']
  elif region.startswith('arm'):
   s=region[-1];keep=['upper_'+s,'fore_'+s,'hand_'+s]+[f'arm_{s}_edge_{i}' for i in range(6)]
   if s=='r':keep += ['grip_cage_'+str(i) for i in range(4)]
  else:
   s=region[-1];keep=['thigh_'+s,'shin_'+s,'foot_'+s,'toe_'+s]+[f'leg_{s}_edge_{i}' for i in range(6)]
  keep+=['frame_cage_'+str(i) for i in range(4)]
  anchors={w[bn][:2]:bn for bn in keep};tris=[]
  for poly in triangulate(MultiPoint(list(anchors))):
   coords=list(poly.exterior.coords)[:3];a,b,c=coords
   matrix=np.array([[a[0]-c[0],b[0]-c[0]],[a[1]-c[1],b[1]-c[1]]])
   tris.append((np.linalg.inv(matrix),np.array(c),[anchors[v] for v in coords],poly.bounds))
  CAGES[name,region]=tris;WEIGHT_CACHE[name,region]={}
def cage_weights(name,x,y,region='body'):
 cache=WEIGHT_CACHE[name,region];key=(x,y)
 if key in cache:return cache[key]
 p=world(POSES[name],key)
 for inv,c,names,bb in CAGES[name,region]:
  if not(bb[0]-1e-6<=p[0]<=bb[2]+1e-6 and bb[1]-1e-6<=p[1]<=bb[3]+1e-6):continue
  a,b=inv@(np.array(p)-c);v=(a,b,1-a-b)
  if min(v)>=-1e-6:
   result={bn:max(0,float(ww)) for bn,ww in zip(names,v) if ww>1e-8};cache[key]=result;return result
 raise ValueError(('Outside anatomical cage',name,key))

# No image resampling, painting, inpainting, or color change takes place here.
textures={};atlas=[]
for name,path in [(n,OUT/'source'/(n+'.png')) for n in POSES]+[(n+'-body',OUT/'source'/(n+'-body.png')) for n in ['E00','E05','brace','prone']]+[('staff-master',OUT/'source/staff-only.png')]:
 im=Image.open(path).convert('RGBA');w,h=im.size
 aw=2**math.ceil(math.log2(w+4));ah=2**math.ceil(math.log2(h+4))
 page=Image.new('RGBA',(aw,ah),(0,0,0,0));page.paste(im,(2,2));fn=name+'.png';page.save(EX/fn)
 textures[name]=(im,w,h)
 atlas.extend([fn,f'size: {aw},{ah}','format: RGBA8888','filter: MipMapLinearLinear,Linear','repeat: none','pma: false',name,'  rotate: false','  xy: 2, 2',f'  size: {w}, {h}',f'  orig: {w}, {h}','  offset: 0, 0','  index: -1',''])
(EX/'megumin.atlas').write_text('\n'.join(atlas),encoding='utf-8')

SLOTS=['body_under','cape','body','leg_l','leg_r','arm_l','hand_l','arm_r','head','staff','hand_r']
atts={n:{} for n in SLOTS}
slots=[dict(name=n,bone='root',attachment=('rigid_staff' if n=='staff' else 'E00/'+n)) for n in SLOTS]
SHAPES={n:{'hand_r':Polygon(HANDS[n]),'arm_r':Polygon(ARM_R[n]),'arm_l':Polygon(ARM_L[n]),**({'head':Polygon(HEADS[n])} if n in HEADS else {})} for n in POSES}
AREAS={}
for name,p in POSES.items():
 im,w,h=textures[name];q=p['points'];canvas=box(0,0,w-1,h-1);used=GeometryCollection();areas={}
 shapes={'hand_r':Polygon(HANDS[name]),'hand_l':Point(q['gl']).buffer(82 if name in ('brace','crouch','kneel-rise','fall-lean','lower','prone') else 49),'head':Polygon(HEADS[name]).buffer(0),'arm_r':Polygon(ARM_R[name]).buffer(0),'arm_l':Polygon(ARM_L[name]).buffer(0)}
 for s in 'rl':shapes['leg_'+s]=LineString([q['h'+s],q['k'+s],q['a'+s],q['t'+s]]).buffer(82)
 shapes['body']=LineString([q['pelvis'],q['chest']]).buffer(123)
 for sn,shape in shapes.items():
  areas[sn]=shape.intersection(canvas).difference(used);used=used.union(areas[sn])
 areas['cape']=canvas.difference(used);AREAS[name]=areas

def each_polygon(g):
 if isinstance(g,Polygon):yield g
 elif hasattr(g,'geoms'):
  for child in g.geoms:yield from each_polygon(child)
def clipped_geometry(shape,alpha,step=22):
 points=[];indices=[];lookup={}
 if shape.is_empty:return points,indices
 minx,miny,maxx,maxy=shape.bounds;h,w=alpha.shape
 for y in range(max(0,math.floor(miny/step)*step),min(h,math.ceil(maxy)),step):
  for x in range(max(0,math.floor(minx/step)*step),min(w,math.ceil(maxx)),step):
   xx=min(w-1,x+step);yy=min(h-1,y+step)
   # Generated cutouts include disconnected, nearly transparent prop-removal
   # residue. Do not build geometry for those empty-looking atlas tiles.
   if alpha[y:yy+1,x:xx+1].max()<32:continue
   for poly in each_polygon(shape.intersection(box(x,y,xx,yy))):
    if poly.area<1e-5:continue
    rings=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors]
    coords=np.array([v for ring in rings for v in ring],dtype=np.float64)
    tri=mapbox_earcut.triangulate_float64(coords,np.cumsum([len(r) for r in rings],dtype=np.uint32));ids=[]
    for v in coords:
     key=(round(float(v[0]),6),round(float(v[1]),6))
     if key not in lookup:lookup[key]=len(points);points.append(key)
     ids.append(lookup[key])
    indices.extend(ids[int(i)] for i in tri)
 return points,indices
def segment(p,a,b):
 v=sub(b,a);len2=v[0]**2+v[1]**2
 t=max(0,min(1,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/max(1e-8,len2)))
 c=(a[0]+v[0]*t,a[1]+v[1]*t)
 return math.dist(p,c),t
def classify(name,x,y):
 p=POSES[name];q=p['points'];xy=(x,y)
 point=Point(x,y);sh=SHAPES[name]
 if sh['hand_r'].covers(point):return 'hand_r'
 if math.dist(xy,q['gl'])<48:return 'hand_l'
 arm='arm_r' if sh['arm_r'].covers(point) else 'arm_l' if sh['arm_l'].covers(point) else None
 if 'head' in sh and sh['head'].covers(point):
  im,w,h=textures[name];r,g,b,a=im.getpixel((max(0,min(w-1,round(x))),max(0,min(h-1,round(y)))))
  cloth=(r>g*1.3 and r>b*1.3) or (r>150 and g>80 and b<g*.7)
  if not(arm and cloth and y>q['neck'][1]-20):return 'head'
 if arm:return arm
 # Caps around the actually drawn limbs prevent the cape from inheriting an
 # unrelated forearm's motion merely because it is close in the atlas.
 options=[]
 for s in 'rl':
  d3,_=segment(xy,q['h'+s],q['k'+s]);d4,_=segment(xy,q['k'+s],q['a'+s]);d5,_=segment(xy,q['a'+s],q['t'+s])
  options.append((min(d3/53,d4/48,d5/68),'leg_'+s))
 d,kind=min(options)
 if d<1:return kind
 # A plane following the neck and its illustrated tilt separates the head
 # from the torso in upright and prone poses alike.
 h=rot(sub(world(p,xy),world(p,q['neck'])),-p['head'])
 if h[1]>-2:return 'head'
 d,t=segment(xy,q['pelvis'],q['chest'])
 return 'body' if d<122 else 'cape'

def weights(name,x,y):
 p=POSES[name];q=p['points'];xy=(x,y);kind=classify(name,x,y)
 if kind=='hand_r':return {'hand_r':1}
 if kind=='hand_l':return {'hand_l':1}
 if kind=='head':return {'head':1}
 if kind.startswith('arm_'):
  s=kind[-1];d,t=segment(xy,q['s'+s],q['e'+s]);d2,u=segment(xy,q['e'+s],q['g'+s])
  if d<=d2:
   a=smooth(max(0,min(1,(t-.58)/.42)));return {'upper_'+s:1-a,'fore_'+s:a}
  a=smooth(max(0,min(1,(u-.55)/.45)));return {'fore_'+s:1-a,'hand_'+s:a}
 if kind.startswith('leg_'):
  s=kind[-1];d,t=segment(xy,q['h'+s],q['k'+s]);d2,u=segment(xy,q['k'+s],q['a'+s]);d3,v=segment(xy,q['a'+s],q['t'+s])
  if d3<min(d,d2):return {'foot_'+s:1}
  if d<=d2:
   a=smooth(max(0,min(1,(t-.55)/.45)));return {'thigh_'+s:1-a,'shin_'+s:a}
  a=smooth(max(0,min(1,(u-.6)/.4)));return {'shin_'+s:1-a,'foot_'+s:a}
 d,t=segment(xy,q['pelvis'],q['chest'])
 if kind=='body':return {'pelvis':1-t,'chest':t}
 k='cape_l' if math.dist(xy,q['cape1'])<math.dist(xy,q['cape2']) else 'cape_r'
 return {k:.72,'chest':.28}

def make_mesh(name,slot,texture,points,tri,weight_func=None,point_func=None):
 im,w,h=textures[texture];verts=[];uv=[]
 for x,y in points:
  uv.extend([rnd(x/w),rnd(y/h)])
  wp=point_func(x,y) if point_func else world(POSES[name],(x,y))
  if STABILIZE and slot=='hand_r':
   transform=HAND_TRANSFORMS[name]
   wp=tuple(wp[i]*transform['scale']+transform['translation'][i] for i in (0,1))
  rigid=False
  region='body' if slot=='body_under' else 'arm_'+slot[-1] if slot.startswith(('arm_','hand_')) else slot if slot.startswith('leg_') else 'all'
  if slot!='body_under' and name in ('E00','E01','turn-upright','E05','E08','E12','release'):region='standing'
  elif slot.startswith('leg_') and name in ('fall-lean','kneel-rise'):region='all'
  part_rigid=STABILIZE and slot in ('head','hand_r')
  ww={slot:1} if part_rigid else weight_func(x,y) if weight_func else ({slot:1} if rigid else cage_weights(name,x,y,region))
  if not weight_func and not part_rigid and region.startswith('arm_'):
   hand='hand_'+region[-1];shape=SHAPES[name]['hand_r'] if hand=='hand_r' else AREAS[name]['hand_l']
   influence=1-smooth(min(1,shape.distance(Point(x,y))/38))
   ww={b:v*(1-influence) for b,v in ww.items()};ww[hand]=ww.get(hand,0)+influence
  ww={b:v for b,v in ww.items() if v>1e-5};total=sum(ww.values());verts.append(len(ww))
  for b,v in ww.items():
   bw=WORLD[name][b];local=(0,0) if not weight_func and not part_rigid and region in ('all','standing','body') else rot(sub(wp,bw),-bw[2])
   verts.extend([BID[b],rnd(local[0]),rnd(local[1]),rnd(v/total)])
 att=dict(type='mesh',path=texture,uvs=uv,triangles=tri,vertices=verts,hull=0,width=w*POSES[name]['scale'],height=h*POSES[name]['scale'])
 atts[slot][('rigid_staff' if slot=='staff' else name+'/'+slot)]=att

# One regular topology per drawing is partitioned into meaningful slots.
# Shared vertices use the SAME weighting function on either side, so their
# world coordinates stay identical while a pose is being interpolated.
mesh_stats=[]
for name in POSES:
 im,w,h=textures[name];alpha=np.asarray(im)[:,:,3]
 for sn,shape in AREAS[name].items():
  if sn.startswith('arm_') and name not in ('E00','E01','turn-upright','E05','E08','E12','release'):shape=shape.union(shape.buffer(38).intersection(Point(POSES[name]['points']['s'+sn[-1]]).buffer(90)))
  points,tri=clipped_geometry(shape,alpha)
  if not tri:continue
  make_mesh(name,sn,name,points,tri)
  mesh_stats.append(dict(pose=name,slot=sn,vertices=len(points),triangles=len(tri)//3))
 print('Bound',name,flush=True)

# Painted hidden areas behind separate arms. These are complete source layers;
# only their torso/cape triangles are used, avoiding duplicate faces or legs.
FILL_FOR={n:('E00' if n in ('E00','E01','turn-upright') else 'brace' if n in ('brace','crouch','kneel-rise') else 'prone' if n in ('lower','prone') else 'E05') for n in POSES}
for source in ['E00','E05','brace','prone']:
 im,w,h=textures[source+'-body'];alpha=np.asarray(im)[:,:,3];areas=AREAS[source]
 fill=areas['body'].union(areas['arm_r']).union(areas['arm_l']).union(areas['hand_r']).union(areas['hand_l'])
 if source in ('E00','E05'):fill=fill.intersection(box(0,0,w,POSES[source]['points']['pelvis'][1]+70))
 points,indices=clipped_geometry(fill,alpha)
 make_mesh(source,'body_under',source+'-body',points,indices)
for n in POSES:
 source=FILL_FOR[n]
 if n!=source:atts['body_under'][n+'/body_under']=atts['body_under'][source+'/body_under']

# A newly completed prop layer also contains the shaft hidden by the original
# hand. A permanent gap in the old cutout cannot survive a new grip silhouette.
# Calibrate once to the original orb and tail; scale never changes in a clip.
im,w,h=textures['staff-master'];bounds=im.getchannel('A').getbbox();l,t,r,b=bounds
pts=[(l,t),(l,b),(r,t),(r,b)]
sa=(303,385);sb=(605,1315);ta=(188,489);tb=(419,1325)
factor=math.dist(ta,tb)/math.dist(sa,sb);delta=ang(ta,tb)-ang(sa,sb)
def staff_point(x,y):
 v=rot(sub((x,y),sa),delta);return world(POSES['E00'],(ta[0]+v[0]*factor,ta[1]+v[1]*factor))
make_mesh('E00','staff','staff-master',pts,[0,1,2,2,1,3],lambda x,y:{'staff':1},staff_point)

animations={};plans={}
switch_file=OUT/'attachment-switches.json'
SWITCHES=json.loads(switch_file.read_text())['thresholds'] if switch_file.exists() else {}
def interp_schedule(schedule,t):
 if t<=schedule[0][0]:return schedule[0][1],schedule[0][1],0
 for i in range(1,len(schedule)):
  b,nb=schedule[i];a,na=schedule[i-1]
  if t<=b:return na,nb,smooth((t-a)/(b-a))
 return schedule[-1][1],schedule[-1][1],0
def interpolate_pose(a,b,u):
 # Interpolate desired world transforms, then derive local transforms. This
 # keeps wrist arcs and chosen contacts independent of parent rotations.
 w={}
 for n in NAMES:
  x,y,r=WORLD[a][n];xx,yy,rr=WORLD[b][n];dr=(rr-r+180)%360-180
  w[n]=(x+(xx-x)*u,y+(yy-y)*u,r+dr*u)
 return w
def build_anim(name,schedule,loop=False,mode=None,event=None):
 duration=schedule[-1][0];bt={n:{'translate':[],'rotate':[]} for n in NAMES};st={sn:{'attachment':[]} for sn in SLOTS};frames=[];prev=None;order=[];previous_behind=None
 motion=Motion(schedule,WORLD) if FLOW else None
 count=math.ceil(duration*60)
 for i in range(count+1):
  t=min(i/60,duration);a,b,u=interp_schedule(schedule,t);active=a if u<SWITCHES.get(a+' > '+b,.5) else b
  w=motion.at(t) if FLOW else interpolate_pose(a,b,u);pulse=math.sin(math.pi*t/duration)**2
  crossing=(a in ('turn-upright','E05') and b in ('turn-upright','E05') and a!=b)
  if crossing and not FLOW:
   # The far arm passes behind the body in 3D. Keep each visible-side drawing
   # near its own silhouette; switch the hidden arm during the occluded phase.
   arm_u=u if STABILIZE else (u*.24 if u<.5 else 1-(1-u)*.24)
   arm_w=interpolate_pose(a,b,arm_u)
   for bn in NAMES:
    if bn in ('upper_l','fore_l','hand_l') or bn.startswith(('arm_l_edge','left_grip_cage')):w[bn]=arm_w[bn]
  if mode in ('idle','chant','prone','hold'):
   breath=(.7 if mode=='idle' else .40)*math.sin(2*math.pi*t/duration)
   for bn in ['chest','head','upper_r','fore_r','hand_r','staff','upper_l','fore_l','hand_l','cape_l','cape_r']+[n for n in NAMES if n.startswith(('head_cage','grip_cage','left_grip_cage','arm_'))]:
    x,y,r=w[bn];w[bn]=(x,y+breath*(.22 if mode=='prone' else 1),r)
   for bn in ['cape_l','cape_r']:
    x,y,r=w[bn];w[bn]=(x+(math.sin(2*math.pi*t/duration-.5)-math.sin(-.5))*.75,y,r)
  if mode in ('hit','ack'):
   amount=1.7 if mode=='ack' else 4
   hx,hy,hr=w['head']
   for bn in [n for n in NAMES if n.startswith('head_cage')]:
    x,y,r=w[bn];v=rot((x-hx,y-hy),pulse*amount);w[bn]=(hx+v[0]-pulse*amount*.3,hy+v[1]-pulse*amount*.2,r)
   x,y,r=w['head'];w['head']=(x-pulse*amount*.3,y-pulse*amount*.2,r+pulse*amount)
   if mode=='hit':
    for bn in ['chest','upper_r','fore_r','hand_r','staff']:
     x,y,r=w[bn];w[bn]=(x-1.6*pulse,y,r)
  local=locals_from(w)
  for bn in NAMES:
   x,y,r=local[bn];sx,sy,sr=SETUP[bn]
   bt[bn]['translate'].append(dict(time=rnd(t),x=rnd(x-sx),y=rnd(y-sy)))
   bt[bn]['rotate'].append(dict(time=rnd(t),value=rnd((r-sr+180)%360-180)))
  hidden_far_arm=crossing and .15<u<.85
  attachment_state=(active,hidden_far_arm,crossing)
  if attachment_state!=prev:
   for sn in SLOTS:
    at='rigid_staff' if sn=='staff' else active+'/'+sn
    visible=(sn!='body_under' or hidden_far_arm) and not(not STABILIZE and hidden_far_arm and sn in ('arm_l','hand_l'))
    st[sn]['attachment'].append(dict(time=rnd(t),name=at if visible and at in atts[sn] else None))
   prev=attachment_state
  behind=(a in ('turn-upright','E05') and b in ('turn-upright','E05') and a!=b and .08<u<.95)
  if behind!=previous_behind:
   # Draw the far left arm behind the reconstructed chest while it crosses
   # from the visible far side to the rear of the torso during the turn.
   order.append(dict(time=rnd(t),**({'offsets':[{'slot':'arm_l','offset':-SLOTS.index('arm_l')},{'slot':'hand_l','offset':1-SLOTS.index('hand_l')},{'slot':'staff','offset':-1}]} if behind else {})))
   previous_behind=behind
  frames.append(dict(frame=i,time=rnd(t),reference=active,from_pose=a,to_pose=b,blend=rnd(u),right_grip=[rnd(v) for v in w['hand_r'][:2]],staff_angle=rnd(w['staff'][2])))
 data=dict(bones=bt,slots=st,drawOrder=order)
 if event:data['events']=[dict(time=event[0],name=event[1],string=event[2])]
 animations[name]=data;plans[name]=dict(duration=duration,loop=loop,schedule=schedule,frames=frames)

build_anim('idle_loop',[(0,'E00'),(3.4,'E00')],True,'idle')
build_anim('chant_enter',ENTRY)
build_anim('chant_loop',[(0,'E12'),(2.4,'E12')],True,'chant')
build_anim('chant_cancel',[(1.30-t,p) for t,p in reversed(ENTRY)])
build_anim('chant_ack',[(0,'E12'),(.50,'E12')],mode='ack')
build_anim('explosion_release',[(0,'E12'),(.22,'E12'),(.44,'release'),(.7,'release')],event=(.44,'release','explosion'))
build_anim('explosion_hold',[(0,'release'),(.7,'release')],True,'hold')
build_anim('explosion_exit',[(0,'release'),(.6,'fall-lean')])
build_anim('relaxed_fall',FALL)
build_anim('relaxed_loop',[(0,'prone'),(3.0,'prone')],True,'prone')
build_anim('get_up',RECOVER)
for n,p in [('hit','E00'),('hit_chant','E12'),('hit_down','prone')]:build_anim(n,[(0,p),(.42,p)],mode='hit')
build_anim('dead',[(0,'E00'),(.28,'turn-upright'),(.6,'fall-lean'),(.84,'crouch'),(1.10,'brace'),(1.36,'lower'),(1.66,'prone'),(1.85,'prone')])
build_anim('dead_from_down',[(0,'prone'),(.45,'prone')])
build_anim('dead_loop',[(0,'prone'),(2,'prone')],True)
short=[(t*.52,p) for t,p in ENTRY]+[(.82,'E12')]+[(.82+(1.3-t)*.52,p) for t,p in list(reversed(ENTRY))[1:]]
build_anim('attack_short',short,event=(.76,'impact','ordinary'))
build_anim('cast_short',short)
# Dedicated bind poses expose all variants for the Spine editor. They are not
# intended for gameplay; the clips preserve their own attachment reset keys.
for name in POSES:build_anim('_bind/'+name,[(0,name),(.1,name)])
skeleton=dict(skeleton=dict(hash='megumin-continuous-v9' if FLOW else 'megumin-calibrated-v8' if STABILIZE else 'megumin-reference-v7',spine='4.2.43',x=-220,y=-35,width=520,height=405,images='../images/',fps=60),bones=bones,slots=slots,skins=[dict(name='default',attachments=atts)],events={'release':{'string':'explosion'},'impact':{'string':'ordinary'}},animations=animations)
(EX/'megumin.json').write_text(json.dumps(skeleton,separators=(',',':')),encoding='utf-8')
metadata=dict(poses=POSES,mesh_stats=mesh_stats,clips=plans,method='Alternate anatomical UV meshes, bound at the illustrated pose, with one permanent rigid staff. No whole-image crossfading.',bone_count=len(bones),slot_count=len(slots))
if STABILIZE:metadata['hand_transforms']=HAND_TRANSFORMS
if FLOW:metadata['motion']={'interpolation':'Bounded vector cubic Hermite for body/grip paths; monotone angular and support channels. Shared tangents across waypoints, zero tangents at endpoints and true holds.','phase_offsets_seconds':{'head':-.035,'chest':-.015,'elbow':.012,'grip':.025,'left_hand':.040,'cape':.060},'source_pixels':'Unchanged v8 images; hash-checked Mi-Ripple provenance.'}
(OUT/'authoring.json').write_text(json.dumps(metadata,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
with (OUT/'frame-plan.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.writer(f);writer.writerow(['clip','frame60fps','time','reference','from','to','blend','right_grip_x','right_grip_y','staff_angle'])
 for n,p in plans.items():
  if n.startswith('_bind/'):continue
  for a in p['frames']:writer.writerow([n,a['frame'],a['time'],a['reference'],a['from_pose'],a['to_pose'],a['blend'],*a['right_grip'],a['staff_angle']])
print('Exported',len(bones),'bones',sum(len(v) for v in atts.values()),'attachments',len(animations),'clips')
