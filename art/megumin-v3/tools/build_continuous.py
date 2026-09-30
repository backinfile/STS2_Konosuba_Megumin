"""Geometry-only cuts and editable native timelines; never repaints source PNGs."""
from pathlib import Path
import json, math, shutil
import numpy as np
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'assets/baseline'
src=json.loads((BASELINE/'rig_geometry_v1.json').read_text())
parts=[]
def clip(poly,n,c,less=True):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  fp=p[0]*n[0]+p[1]*n[1]-c;fq=q[0]*n[0]+q[1]*n[1]-c
  pin=fp<=0 if less else fp>=0;qin=fq<=0 if less else fq>=0
  if pin:out.append(p)
  if pin!=qin:
   t=fp/(fp-fq);out.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
 return out
def add(old,name=None,bone=None,vertices=None,z=None):
 p=json.loads(json.dumps(old));p['name']=name or p['name'];p['bone']=bone or p['group']
 if vertices is not None:p['vertices']=vertices;p['uv']=vertices;p['triangles']=[]
 if z is not None:p['z']=z
 parts.append(p);return p
def inside(point,polygon):
 x,y=point;c=False
 for p,q in zip(polygon,polygon[1:]+polygon[:1]):
  if (p[1]>y)!=(q[1]>y) and x<(q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:c=not c
 return c

def leg_mesh(outline,knee,upper,lower,band=44.):
 # Conforming contour + fine knee grid; one UV surface, no overlapping joint disc.
 points=[]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  n=max(1,math.ceil(math.dist(a,b)/14))
  points.extend([[a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n] for t in range(n)])
 x0=int(min(v[0] for v in outline))+4;y0=int(min(v[1] for v in outline))+4
 for y in range(y0,int(max(v[1] for v in outline)),8):
  for x in range(x0,int(max(v[0] for v in outline)),8):
   if abs(y-knee[1])>70 and abs(y-upper[1])>55 and ((x-x0)%24!=0 or (y-y0)%24!=0):continue
   if inside((x,y),outline):points.append([x,y])
 points=np.unique(np.round(points,5),axis=0).tolist();tri=[]
 for ids in Delaunay(points).simplices:
  p=np.array([points[i] for i in ids]);samples=[p.mean(0),*(.5*(p[i]+p[(i+1)%3]) for i in range(3))]
  if inside(p.mean(0),outline):tri.append(ids.tolist())
 axis=(np.array(knee)-upper)/math.dist(knee,upper)+(np.array(lower)-knee)/math.dist(lower,knee);axis/=np.linalg.norm(axis)
 weights=[]
 for p in points:
  d=float(np.dot(np.array(p)-knee,axis));w=max(0,min(1,(d+band)/(2*band)));weights.append(w*w*(3-2*w))
 return points,tri,weights,axis.tolist()

p={x['name']:x for x in src['parts']}
# Complete newly authored cloak; no UV cloth cloning remains.
uv=[[x,y] for y in range(390,1171,60) for x in range(0,1025,64)]
verts=[[x,480+(y-450)*.92] for x,y in uv]
tris=[]
for y in range(13):
 for x in range(16):
  a=y*17+x;tris.extend([[a,a+1,a+17],[a+1,a+18,a+17]])
parts.append({'name':'complete_cape','vertices':verts,'uv':uv,'triangles':tris,'bone':'cape','group':'cape','z':-7,'texture':'cape_v3'})
for side in ['left','right']:
 old=p['leg_'+side]
 if side=='left':
  v=[[494,810],[607,845],[593,879],[579,910],[559,938],[548,964],[530,998],[511,1026],[498,1052],[481,1080],[462,1108],[442,1143],[418,1180],[395,1215],[382,1244],[363,1246],[343,1240],[327,1232],[332,1214],[344,1175],[359,1139],[379,1105],[402,1076],[423,1049],[438,1020],[449,985],[460,949],[473,914],[479,881],[488,844]]
 else:
  v=[[630,844],[739,848],[741,891],[741,933],[747,978],[753,1022],[768,1076],[784,1119],[793,1163],[804,1210],[797,1230],[785,1236],[760,1235],[750,1231],[738,1210],[717,1174],[705,1132],[703,1093],[694,1050],[679,1007],[667,963],[657,918],[646,882]]
 split=1053 if side=='left' else 1059
 h=(548,848) if side=='left' else (681,857);k=(463,1053) if side=='left' else (720,1059);a=(348,1243) if side=='left' else (779,1241)
 vertices,triangles,weights,axis=leg_mesh(v,k,h,a)
 q=add(old,'leg_skin_'+side,'leg_'+side,vertices,0 if side=='left' else 1)
 q['triangles']=triangles;q['skin_weights']=weights;q['knee_band_halfwidth']=44.;q['knee_axis']=axis;q['outline']=v
 hip_axis=(np.array(k)-h)/math.dist(k,h);hip_weights=[]
 for point in vertices:
  d=float(np.dot(np.array(point)-h,hip_axis));lo,hi=((-18,52) if side=='left' else (0,90));w=max(0,min(1,(d-lo)/(hi-lo)));hip_weights.append(w*w*(3-2*w))
 q['hip_weights']=hip_weights;q['hip_band']=([-18,52] if side=='left' else [0,90])
 if side=='left':
  boot=[[299,1210],[318,1205],[331,1204],[329,1216],[326,1232],[343,1240],[363,1247],[383,1246],[397,1220],[407,1229],[413,1244],[407,1269],[397,1295],[390,1310],[348,1313],[343,1370],[333,1452],[322,1499],[277,1508],[243,1503],[241,1470],[264,1417],[280,1376],[280,1323],[291,1279],[278,1267],[285,1245]]
 else:
  boot=[[798,1191],[818,1197],[831,1206],[833,1233],[844,1254],[839,1269],[827,1284],[822,1276],[816,1289],[815,1311],[822,1337],[827,1361],[836,1384],[847,1405],[884,1425],[904,1451],[907,1465],[858,1473],[811,1468],[766,1445],[765,1418],[759,1386],[760,1340],[752,1310],[746,1298],[727,1291],[722,1268],[718,1240],[720,1222],[732,1210],[739,1207],[743,1217],[751,1230],[760,1235],[785,1237],[799,1230],[805,1211],[801,1197]]
 add(old,'boot_'+side,'boot_'+side,boot,2)

torso=[[501,449],[518,463],[548,480],[571,487],[599,483],[614,474],[633,447],[648,455],[663,470],[680,487],[688,514],[704,548],[700,605],[686,646],[704,671],[714,732],[660,730],[551,706],[530,669],[538,639],[521,610],[514,581],[480,583],[463,566],[439,570],[429,551],[432,523],[448,492],[464,475],[482,459]]
q=add(p['occlusion_torso'],bone='torso',vertices=torso,z=5);q['texture']='body_v3'
# The old skirt mask included 20-45 px of thighs. Split actual cloth from skin.
front_skirt=[[547,659],[630,655],[699,670],[719,705],[736,752],[756,792],[768,856],[769,862],[759,857],[744,854],[728,854],[706,857],[684,860],[662,861],[642,860],[626,857],[609,851],[593,846],[576,838],[558,829],[540,821],[522,814],[505,809],[489,805],[471,802],[453,801],[436,802],[423,806],[417,811],[418,803],[439,779],[463,749],[499,710]]
add(p['skirt'],'skirt','pelvis',front_skirt,4)
for name,back in [('left',[[417,811],[440,804],[470,803],[489,805],[473,862],[455,858],[439,851],[444,840],[425,828]]),('middle',[[599,850],[631,861],[638,882],[589,881]]),('right',[[744,854],[759,857],[769,862],[762,870],[746,875]])]:
 add(p['skirt'],'skirt_back_'+name,'pelvis',back,-1)
# The head/hat stays one rigid part. The collar stays with the torso.
head=p['head_and_collar']
# Follow the real hair / neck silhouette; no shoulder cape or gold neckline in head.
h=head['vertices'];idx=h.index([690,396]);tail=h.index([478,456])
clean_head=h[:idx+1]+[[693,429],[680,465],[666,469],[650,477],[631,477],[610,475],[609,479],[595,480],[580,478],[556,470],[548,473],[545,480],[575,498],[560,501],[538,496],[519,486],[505,482],[492,463]]+h[tail:]
add(head,'head_hat','head',clean_head,8)
# Remove cloak-trim fragments accidentally included in the v1 sleeve cut.
left_upper=[[489,530],[508,526],[518,534],[524,546],[519,562],[501,574],[481,580],[457,598],[444,620],[458,654],[451,698],[432,744],[415,739],[397,718],[388,688],[362,662],[355,642],[367,611],[397,582],[432,565],[462,552],[480,541]]
add(p['arm_left_upper'],bone='left_upper',vertices=clip(left_upper,(0,1),646),z=6)
add(p['arm_left_upper'],'left_sleeve_drape',bone='left_cuff',vertices=clip(left_upper,(0,1),611,False),z=7)
lower=p['arm_left_forearm'];v=lower['vertices'];n=(.957826,-.287348);c=495*n[0]+607*n[1]
add(lower,'arm_left_forearm','left_forearm',clip(v,n,c+8),7)
add(lower,'hand_left','left_hand',clip(v,n,c-8,False),9)
add(p['arm_right_upper'],bone='right_upper',vertices=[[657,536],[673,541],[697,566],[714,583],[739,592],[753,604],[753,636],[746,653],[727,667],[707,656],[693,640],[683,609],[671,589],[650,570]],z=6)
add(p['arm_right_forearm'],bone='right_forearm',z=7)
add(p['right_wrist'],'hand_right','right_hand',z=11)
for name in ['staff_complete_top','staff_complete_lower']:add(p[name],bone='right_hand')
# All anatomy transforms have unit scale. Staff image registration remains 0.83 as in v1.
rests={'pelvis':[614,852],'torso':[619,701],'head':[583,485],
'left_cuff':[415,631],'left_upper':[484,539],'left_forearm':[415,631],'left_hand':[495,607],
'right_upper':[674,545],'right_forearm':[740,631],'right_hand':[829,609],
'knee_left':[463,1053],'knee_right':[720,1059],'thigh_left':[548,848],'shin_left':[463,1053],'boot_left':[348,1243],
'thigh_right':[681,857],'shin_right':[720,1059],'boot_right':[779,1241]}
(ROOT/'assets/rig_geometry.json').write_text(json.dumps({'canvas':src['canvas'],'origin':src['origin'],'parts':parts,'rests':rests,'sole_centers':[[285,1508],[838,1470]],'boot_offsets':[[65,0],[-35,0]]},indent=2))
props=['hip_x','hip_drop','pelvis_tilt','torso_lean','head_tilt','left_shoulder','left_elbow','left_wrist','right_shoulder','right_elbow','right_wrist','cape_strength']
base={p:0 for p in props};base['cape_strength']=.5
# Smooth coherent five-second action. Angles are relative to the same source bones.
keys=[
(0.0,{}),
(.45,{'hip_x':-9,'hip_drop':24,'pelvis_tilt':-1,'torso_lean':-4,'head_tilt':3,'left_shoulder':-6,'left_elbow':-12,'right_shoulder':8,'right_elbow':-8,'right_wrist':-3,'cape_strength':.7}),
(1.2,{'hip_x':-13,'hip_drop':14,'pelvis_tilt':-1,'torso_lean':-5,'head_tilt':3,'left_shoulder':42,'left_elbow':-52,'left_wrist':-2,'right_shoulder':-43,'right_elbow':-29,'right_wrist':43,'cape_strength':1}),
(2.0,{'hip_x':-8,'hip_drop':5,'pelvis_tilt':0,'torso_lean':-3,'head_tilt':1,'left_shoulder':70,'left_elbow':-105,'left_wrist':0,'right_shoulder':-63,'right_elbow':-37,'right_wrist':80,'cape_strength':1.2}),
(2.65,{'hip_x':-6,'hip_drop':7,'pelvis_tilt':0,'torso_lean':-3,'head_tilt':1,'left_shoulder':71,'left_elbow':-104,'left_wrist':0,'right_shoulder':-62,'right_elbow':-38,'right_wrist':80,'cape_strength':1.3}),
(3.0,{'hip_x':13,'hip_drop':32,'pelvis_tilt':3,'torso_lean':8,'head_tilt':-7,'left_shoulder':-27,'left_elbow':-38,'left_wrist':10,'right_shoulder':-36,'right_elbow':-9,'right_wrist':65,'cape_strength':1.8}),
(3.35,{'hip_x':17,'hip_drop':38,'pelvis_tilt':3,'torso_lean':9,'head_tilt':-6,'left_shoulder':-31,'left_elbow':-31,'left_wrist':8,'right_shoulder':-32,'right_elbow':-6,'right_wrist':62,'cape_strength':1.5}),
(4.15,{'hip_x':7,'hip_drop':18,'pelvis_tilt':1,'torso_lean':2,'head_tilt':1,'left_shoulder':-10,'left_elbow':-7,'right_shoulder':4,'right_elbow':-9,'right_wrist':-1,'cape_strength':.8}),
(4.7,{'hip_x':4,'hip_drop':48,'pelvis_tilt':2,'torso_lean':9,'head_tilt':7,'left_shoulder':-32,'left_elbow':-5,'left_wrist':0,'right_shoulder':14,'right_elbow':-12,'right_wrist':-5,'cape_strength':.4}),
(5.4,{})]
# Neutral: both knees flex just 8 degrees, solved with the actual two-hip pivot.
# The single pelvis roll is countered by torso rotation; all source lengths stay fixed.
neutral={'hip_drop':-16.6879351,'pelvis_tilt':8.53055893,'torso_lean':-8.53055893}
keys=[(t,{p:v.get(p,base[p])+neutral.get(p,0.) for p in props}) for t,v in keys]

# Bake a minimum-jerk ease through art-directed keys into ordinary LINEAR value tracks.
# This avoids Godot cubic overshoot without discrete frame changes; all properties interpolate.
dense=[]
for i in range(325):
 t=i/60
 for j in range(len(keys)-1):
  if t<=keys[j+1][0]+1e-7:break
 t0,a=keys[j];t1,b=keys[j+1];u=max(0,min(1,(t-t0)/(t1-t0)));s=u*u*u*(u*(u*6-15)+10)
 vals={p:float(a.get(p,base[p])+(b.get(p,base[p])-a.get(p,base[p]))*s) for p in props}
 dense.append((t,vals))
text='[gd_resource type="Animation" format=3]\n\n[resource]\nresource_name = "ContinuousCast"\nlength = 5.4\n'
for i,p in enumerate(props):
 times=', '.join(f'{t:.7f}' for t,v in dense);vs=', '.join(f'{v[p]:.7f}' for t,v in dense)
 text+=f'tracks/{i}/type = "value"\ntracks/{i}/path = NodePath(".:{p}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = false\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array({times}),\n"transitions": PackedFloat32Array({", ".join("1" for _ in dense)}),\n"update": 0,\n"values": [{vs}]\n}}\n'
(ROOT/'animations/ContinuousCast.tres').write_text(text)
(ROOT/'animations/art_directed_keys.json').write_text(json.dumps({'duration':5.4,'keys':keys,'properties':props,'interpolation':'minimum_jerk_sampled_60hz_linear_playback'},indent=2))
print('Built',len(parts),'rigid/cloth parts and',len(dense),'continuous keys per track')
