"""v6 geometry-only construction. All anatomy textures come from one approved master."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
A=json.loads((ROOT/'assets/anatomy_v6.json').read_text());P=A['landmarks'];parts=[]
def inside(q,poly):
 x,y=q;c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c

def mesh(poly,step=20,fine_rows=()):
 pts=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  n=max(1,math.ceil(math.dist(a,b)/12));pts.extend([[a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n] for t in range(n)])
 x0=int(min(p[0] for p in poly))+3;y0=int(min(p[1] for p in poly))+3
 for y in range(y0,int(max(p[1] for p in poly)),8):
  for x in range(x0,int(max(p[0] for p in poly)),8):
   if all(abs(y-row)>75 for row in fine_rows) and ((x-x0)%24 or (y-y0)%24):continue
   if inside((x,y),poly):pts.append([x,y])
 pts=np.unique(np.round(pts,5),axis=0).tolist();tri=[]
 for ids in Delaunay(pts).simplices:
  q=np.array([pts[i] for i in ids])
  if inside(q.mean(0),poly):tri.append(ids.tolist())
 return pts,tri

def add(name,bone,poly,z,texture='master',meshed=False,uv=None,rows=()):
 v,t=mesh(poly,fine_rows=rows) if meshed else (poly,[])
 p={'name':name,'bone':bone,'vertices':v,'uv':v if uv is None else uv,'triangles':t,'texture':texture,'z':z,'outline':poly}
 parts.append(p);return p

def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
# Mother-head cut follows the hair silhouette; no upper-arm or cape fragment belongs to it.
head=[[374,317],[426,283],[472,251],[478,225],[497,173],[510,143],[500,123],[501,109],[524,95],[565,80],[614,62],[643,58],[661,69],[687,101],[717,139],[751,165],[769,179],[796,210],[813,247],[817,281],[803,270],[786,254],[770,239],[782,278],[832,325],[864,350],[849,353],[802,367],[741,372],[713,368],[710,397],[695,421],[691,448],[693,480],[706,512],[706,540],[697,529],[687,514],[681,499],[674,512],[664,496],[652,474],[648,451],[638,443],[618,442],[611,434],[600,430],[594,447],[606,477],[620,509],[621,537],[610,521],[599,499],[583,480],[568,455],[565,431],[553,412],[545,391],[514,392],[498,385],[483,375],[471,367],[464,349],[434,353],[406,343],[382,335]]
add('head_hat_hair','head',head,9)
# Original torso: visible cloth remains from mother; occluded-side backing will be inserted separately.
torso=[[563,463],[591,473],[620,496],[647,501],[662,481],[679,495],[689,534],[690,578],[698,623],[708,660],[694,693],[649,686],[593,706],[521,719],[520,698],[537,675],[562,649],[566,623],[557,590],[547,563],[548,530]]
add('bodice','torso',torso,4)
add('neck_skin_continuity','torso',[[588,426],[609,432],[629,438],[641,448],[649,465],[662,482],[650,499],[628,480],[610,475],[599,459],[590,445]],8)
# Precise cloth hem avoids the previous v3 mistake of including leg skin in the skirt layer.
skirt=[[524,690],[588,675],[651,663],[700,675],[714,698],[727,737],[731,779],[734,844],[720,839],[697,833],[674,829],[650,823],[626,817],[600,810],[576,805],[550,800],[526,798],[504,799],[478,806],[468,804],[482,771],[500,739]]
add('skirt_front','pelvis',skirt,5)
add('skirt_back','pelvis',[[469,805],[493,800],[503,800],[500,818],[491,827],[476,822]],-2)
# Near, anatomical right arm: constant shoulder/elbow/wrist lengths, no cape trim in the sleeve.
r_arm=[[540,501],[555,493],[558,526],[547,555],[536,586],[529,616],[519,638],[493,656],[465,671],[441,687],[430,674],[434,653],[438,638],[429,611],[428,590],[450,591],[468,598],[484,596],[490,572],[500,549],[516,527]]
# Upper sleeve and forearm are split along elbow-normal cross-section, no texture scaling.
def clip(poly,n,c,less=True):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa=np.dot(a,n)-c;fb=np.dot(b,n)-c;ia=fa<=0 if less else fa>=0;ib=fb<=0 if less else fb>=0
  if ia:out.append(a)
  if ia!=ib:
   t=fa/(fa-fb);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
 return out
q=add('R_continuous_sleeve','R_arm_cloth',r_arm,7,meshed=True,rows=[616])
h=np.array(P['R_shoulder']);k=np.array(P['R_elbow']);wrist=np.array(P['R_wrist']);axis=(k-h)/np.linalg.norm(k-h)+(wrist-k)/np.linalg.norm(wrist-k);axis/=np.linalg.norm(axis)
q['elbow_weights']=[smooth((np.dot(np.array(v)-k,axis)+34)/68) for v in q['vertices']]
# Mother hands stay unique rigid textures for the entire action.
add('R_hand','R_hand',[[390,565],[401,559],[410,559],[416,568],[416,578],[427,591],[434,609],[437,628],[428,636],[414,634],[402,636],[389,630],[381,623],[373,623],[369,614],[365,608],[365,590],[373,575]],12)
add('L_hand','L_hand',[[747,803],[758,793],[770,800],[780,817],[789,828],[800,842],[804,853],[801,879],[792,896],[786,899],[783,893],[778,899],[773,899],[769,888],[762,891],[758,886],[765,874],[770,859],[761,849],[757,843],[751,826]],13)
# Actual ankle is inside each boot. Boot shafts follow shins; only ankle-down feet lock.
leg_outlines={
'R':[[507,796],[547,797],[581,803],[611,815],[607,846],[594,876],[588,905],[573,944],[561,976],[547,1007],[533,1037],[518,1068],[506,1105],[496,1145],[489,1180],[488,1207],[497,1220],[500,1256],[481,1266],[477,1313],[474,1348],[481,1368],[477,1406],[469,1441],[465,1478],[435,1480],[409,1449],[414,1399],[415,1380],[416,1355],[421,1335],[418,1299],[411,1260],[395,1251],[399,1213],[413,1200],[427,1197],[428,1158],[433,1123],[444,1089],[461,1063],[476,1037],[482,1002],[481,965],[486,925],[491,887],[499,859],[500,831]],
'L':[[620,817],[650,824],[686,833],[719,839],[722,867],[719,903],[721,942],[722,989],[722,1034],[719,1072],[720,1113],[722,1161],[721,1194],[742,1204],[745,1230],[753,1260],[739,1255],[739,1300],[742,1327],[737,1338],[742,1354],[739,1380],[765,1418],[730,1434],[697,1414],[683,1390],[681,1362],[689,1340],[680,1316],[672,1275],[650,1254],[651,1212],[658,1199],[671,1197],[662,1160],[655,1128],[654,1092],[657,1056],[655,1024],[645,989],[638,954],[633,916],[626,879]]}
for side,outline in leg_outlines.items():
 h=np.array(P[side+'_hip']);k=np.array(P[side+'_knee']);a=np.array(P[side+'_ankle']);q=add(side+'_leg_skin',side+'_leg',outline,0 if side=='R' else -1,meshed=True,rows=[h[1],k[1],a[1]])
 axis=(k-h)/np.linalg.norm(k-h)+(a-k)/np.linalg.norm(a-k);axis/=np.linalg.norm(axis)
 q['knee_weights']=[smooth((np.dot(np.array(v)-k,axis)+55)/110) for v in q['vertices']]
 hipaxis=(k-h)/np.linalg.norm(k-h);q['hip_weights']=[smooth(np.dot(np.array(v)-h,hipaxis)/90) for v in q['vertices']]
 # The toe/heel cut starts inside the boot, with a narrow ankle blend for a continuous shaft.
 q['ankle_weights']=[smooth((v[1]-(a[1]-36))/72) for v in q['vertices']]
# Sole footprints copied exactly; no automatic stance narrowing or rescaling.
add('R_foot','R_foot',[[416,1367],[439,1363],[473,1367],[479,1380],[476,1405],[483,1431],[495,1464],[501,1480],[498,1496],[483,1509],[453,1516],[429,1511],[414,1501],[407,1488],[409,1458],[413,1424],[412,1398]],2)
add('L_foot','L_foot',[[688,1339],[710,1338],[735,1343],[740,1365],[749,1382],[776,1403],[813,1418],[824,1427],[825,1440],[810,1448],[787,1451],[757,1446],[733,1438],[706,1423],[686,1422],[683,1401],[681,1371]],2)
# Supplemental artwork is registered once. It never changes head/hand or bone scales.
cape_uv=[[x,y] for y in range(180,1321,60) for x in range(0,1025,64)]
cape_v=[[114+.678*x,241+.72*y] for x,y in cape_uv];ct=[]
for row in range(19):
 for col in range(16):
  i=row*17+col;ct.extend([[i,i+1,i+17],[i+1,i+18,i+17]])
parts.append({'name':'complete_cape','bone':'cape','vertices':cape_v,'uv':cape_uv,'triangles':ct,'texture':'cape_raw','z':-8})
back=[[518,496],[553,477],[594,474],[643,480],[681,492],[705,543],[709,600],[722,669],[708,703],[653,694],[600,708],[520,720],[510,695],[532,646],[529,592],[516,552]]
add('torso_occlusion','torso',back,3,'backing',uv=[[720+(x-683)/.82,765+(y-664)/.82] for x,y in back])
def register_arm(raw,src_a,src_b,dst_a,dst_b,width_scale):
 a=np.array(src_a,float);b=np.array(src_b,float);h=np.array(dst_a,float);k=np.array(dst_b,float);u=(b-a)/np.linalg.norm(b-a);v=(k-h)/np.linalg.norm(k-h);scale=np.linalg.norm(k-h)/np.linalg.norm(b-a)
 out=[]
 for pt in raw:
  q=np.array(pt)-a;out.append((h+v*np.dot(q,u)*scale+np.array([-v[1],v[0]])*np.dot(q,[-u[1],u[0]])*width_scale).tolist())
 return out
au=[[553,516],[558,484],[576,455],[604,435],[621,432],[645,441],[662,459],[671,482],[675,524],[687,567],[694,614],[706,659],[719,700],[733,743],[739,765],[702,775],[673,782],[647,768],[635,752],[640,736],[644,716],[625,687],[605,650],[592,609],[580,578],[576,551],[563,540]]
af=[[646,734],[670,725],[701,738],[735,758],[747,797],[778,832],[817,883],[817,890],[799,911],[776,933],[745,954],[718,965],[709,945],[696,901],[680,851],[665,805],[656,777],[638,761]]
for name,raw,sa,sb,da,db,ws,bone,z in [('L_upper_hidden',au,[610,470],[675,745],P['L_shoulder'],P['L_elbow'],.5,'L_upper',2),('L_forearm_hidden',af,[675,745],[766,951],P['L_elbow'],P['L_wrist'],.58,'L_forearm',10)]:
 add(name,bone,register_arm(raw,sa,sb,da,db,ws),z,'free_arm',uv=raw)
add('L_mother_cuff','L_forearm',[[714,703],[731,720],[753,736],[778,766],[777,778],[745,805],[732,796],[724,779],[713,749]],11)
# Original staff silhouette is retained. Generated staff supplies only the hand-occluded shaft.
staff_top=[[177,20],[184,27],[184,65],[191,103],[219,176],[233,216],[246,184],[259,165],[273,160],[291,169],[314,189],[335,212],[352,241],[368,272],[379,304],[379,333],[374,355],[361,383],[349,396],[360,424],[367,459],[377,498],[391,540],[401,564],[389,574],[373,531],[353,501],[338,500],[322,481],[304,455],[314,429],[321,411],[332,390],[339,369],[310,375],[276,370],[251,357],[237,339],[228,369],[222,373],[210,358],[188,306],[169,245],[149,184],[128,113],[125,98],[129,79],[145,49],[163,28]]
add('staff_original_head','R_hand',staff_top,10)
add('staff_original_lower','R_hand',[[402, 632], [422, 632], [427, 650], [435, 680], [436, 690], [440, 700], [454, 750], [468, 800], [481, 850], [491, 890], [496, 905], [523, 1000], [536, 1050], [550, 1100], [562, 1150], [575, 1200], [590, 1250], [604, 1300], [617, 1340], [623, 1360], [630, 1380], [636, 1400], [642, 1420], [645, 1430], [648, 1440], [651, 1450], [649, 1458], [639, 1460], [633, 1458], [620, 1450], [608, 1440], [596, 1430], [588, 1420], [589, 1400], [590, 1380], [591, 1360], [590, 1340], [580, 1300], [567, 1250], [554, 1200], [541, 1150], [529, 1100], [515, 1050], [501, 1000], [475, 905], [471, 890], [460, 850], [446, 800], [432, 750], [421, 700], [417, 690], [414, 680], [406, 650]],10)
# Backing runs only behind the fixed mother hand; a once-fitted longitudinal patch.
add('staff_grip_occlusion','R_hand',[[385,549],[404,547],[429,640],[410,645]],10,'staff_raw',uv=[[390,533],[411,529],[440,628],[418,634]])
# One continuous registered bandage texture uses EXACTLY the original leg mesh topology.
leg=next(p for p in parts if p['name']=='R_leg_skin')
q=json.loads(json.dumps(leg));q['name']='R_white_bandage_texture';q['texture']='unstaffed';q['z']=1
q['triangles']=[t for t in leg['triangles'] if 844<=sum(leg['vertices'][i][1] for i in t)/3 and max(leg['vertices'][i][1] for i in t)<=1204]
# A single fixed source registration follows original outline; it does not alter geometry.
def edges_at(y,outline):
 xs=[]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if min(a[1],b[1])<=y<max(a[1],b[1]):xs.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return (min(xs),max(xs)) if xs else (430,550)
rows=[820,860,900,950,1000,1035,1080,1120,1160,1200,1225]
clean_left=[510,509,505,500,490,477,447,434,432,434,434]
clean_right=[620,613,603,588,574,559,541,528,513,499,493]
uv=[]
for x,y in leg['vertices']:
 l,r=edges_at(y,leg['outline']);u=max(.012,min(.988,(x-l)/max(1,r-l)))
 nl=float(np.interp(y,rows,clean_left));nr=float(np.interp(y,rows,clean_right));ny=float(np.interp(y,[820,862,1035,1218,1510],[813,854,1045,1223,1515]))
 uv.append([nl+u*(nr-nl),ny])
q['uv']=uv;parts.append(q)
add('closed_eyes_face','head',[[607,309],[632,313],[647,330],[651,344],[662,331],[683,335],[683,351],[675,369],[666,385],[650,393],[633,389],[612,375],[600,355],[596,336],[600,320]],10,'closed_face')
(ROOT/'assets/rig_geometry.json').write_text(json.dumps({'canvas':A['canvas'],'landmarks':P,'parts':parts,'source_sha256':hashlib.sha256((ROOT/'assets/source/megumin_master_v6.png').read_bytes()).hexdigest()},indent=2))
print('v6 built',len(parts),'base parts; supplemental pieces registered')
