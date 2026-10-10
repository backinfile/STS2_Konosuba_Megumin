"""Faithful layered Spine rig: original-visible pixels + hidden-area fills.

Pillow is used only to pack unchanged input pixels into power-of-two atlas
pages. All part selection, deformation and masking is Spine UV geometry.
Raster retouching and hidden art are separate built-in imagegen outputs.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.build-deps'))
import json, math, shutil, hashlib
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, box, MultiPolygon, GeometryCollection, MultiPoint
from shapely import contains_xy
import mapbox_earcut

OUT=ROOT/'actions-v4'; EXPORT=OUT/'export'; IMAGES=OUT/'images'
for folder in [EXPORT,IMAGES]:folder.mkdir(exist_ok=True,parents=True)
S=320/1320; ORIGIN=(608,1353)
def world(x,y):return ((x-ORIGIN[0])*S,(ORIGIN[1]-y)*S)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def mix(a,b,t):return a+(b-a)*t
def dist(a,b):return math.hypot(b[0]-a[0],b[1]-a[1])
def angle(a,b):return math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
def roundv(v):return round(float(v),7)

# Keep each source intact; atlas padding enables trilinear mipmaps in WebGL 1.
textures={};atlas=[]
for name,file in [('reference','clean-reference.png'),('body_base','body-base.png'),('blink','blink-source.png'),('tired','tired-expression.png'),('support_grip','support-grip.png'),('arms','arms-hands.png'),('legs','legs-boots.png'),('costume','costume-plates.png'),('focus','focus-expression.png'),('release_face','release-expression.png'),('hit_face','hit-expression.png')]:
    im=Image.open(OUT/'source'/file).convert('RGBA');w,h=im.size
    size=2**math.ceil(math.log2(max(w,h)+4))
    packed=Image.new('RGBA',(size,size),(0,0,0,0));packed.paste(im,(2,2))
    page=name+'-atlas.png';packed.save(EXPORT/page)
    shutil.copyfile(OUT/'source'/file,IMAGES/(name+'.png'))
    textures[name]={'w':w,'h':h,'image':im,'page':page,'size':size}
    atlas.extend([page,f'size: {size},{size}','format: RGBA8888','filter: MipMapLinearLinear,Linear','repeat: none','pma: false',name,'  rotate: false','  xy: 2, 2',f'  size: {w}, {h}',f'  orig: {w}, {h}','  offset: 0, 0','  index: -1',''])
(EXPORT/'megumin.atlas').write_text('\n'.join(atlas),encoding='utf-8')

bones=[];bind={};bid={}
def add_bone(name,point,parent='root',rotation=0,length=0):
    wx,wy=point
    px,py,pa=bind.get(parent,(0,0,0));r=math.radians(-pa)
    x=(wx-px)*math.cos(r)-(wy-py)*math.sin(r);y=(wx-px)*math.sin(r)+(wy-py)*math.cos(r)
    b=dict(name=name,x=roundv(x),y=roundv(y),rotation=roundv(rotation-pa))
    if name!='root':b['parent']=parent
    if length:b['length']=roundv(length)
    bid[name]=len(bones);bones.append(b);bind[name]=(wx,wy,rotation)
    return b

P={k:world(*v) for k,v in {
 'pelvis':(628,1009),'chest':(626,771),'head':(632,656),
 'shoulder_r':(538,792),'elbow_r':(449,855),'grip_r':(310,886),
 'shoulder_l':(704,795),'elbow_l':(730,896),'grip_l':(779,1028),
 'hip_r':(564,1023),'knee_r':(530,1127),'ankle_r':(512,1225),
 'hip_l':(661,1024),'knee_l':(656,1128),'ankle_l':(655,1225),
}.items()}
add_bone('root',(0,0));add_bone('pelvis',P['pelvis']);add_bone('chest',P['chest'],'pelvis')
add_bone('head',P['head'],'chest');add_bone('cape_l',world(440,949),'pelvis');add_bone('cape_r',world(752,1007),'pelvis')
add_bone('staff',P['grip_r']);add_bone('grip_r',P['grip_r'],'staff')
add_bone('grip_l',P['grip_l']);add_bone('hand_l',P['grip_l'],'grip_l')
for side in ['r','l']:
    a,e,g=P['shoulder_'+side],P['elbow_'+side],P['grip_'+side]
    add_bone('upper_'+side,a,'chest',angle(a,e),dist(a,e))
    add_bone('fore_'+side,e,'upper_'+side,angle(e,g),dist(e,g))
for side in ['r','l']:
    h,k,a=P['hip_'+side],P['knee_'+side],P['ankle_'+side]
    add_bone('foot_'+side,a)
    add_bone('thigh_'+side,h,'pelvis',angle(h,k),dist(h,k))
    add_bone('shin_'+side,k,'thigh_'+side,angle(k,a),dist(k,a))

# Partition follows visible boundaries in the cleanup reference. Exact shared
# edges make the combined setup pose reconstruct that one source image.
polys={
 'hand_r':[(272,833),(319,829),(347,842),(367,839),(394,914),(368,920),(336,930),(295,934),(278,916)],
 'staff':[(27,168),(113,167),(145,357),(169,368),(202,386),(232,409),(253,438),(268,475),(273,515),(269,538),(266,558),(242,605),(273,723),(317,846),(344,938),(398,1144),(471,1306),(475,1350),(394,1363),(377,1347),(384,1245),(352,1164),(319,1065),(281,937),(268,851),(230,735),(195,666),(148,622),(121,596),(128,563),(111,516),(120,471),(143,438),(133,428),(107,451),(84,421),(26,279)],
 'head':[(0,0),(1148,0),(1148,631),(814,632),(785,675),(758,798),(722,805),(710,746),(704,706),(697,647),(677,656),(649,663),(613,664),(577,657),(558,643),(545,664),(561,712),(558,765),(554,808),(522,787),(500,729),(488,699),(474,685),(439,651),(0,645)],
 'hand_l':[(737,973),(786,958),(805,975),(822,1020),(813,1069),(784,1079),(751,1063),(735,1025)],
 'arm_r':[(552,754),(558,777),(545,811),(517,852),(478,886),(435,917),(400,941),(379,925),(362,861),(360,837),(410,823),(463,809),(497,784),(524,765)],
 'arm_l':[(696,741),(724,779),(746,813),(771,870),(804,952),(790,973),(746,984),(734,947),(720,901),(700,858),(687,820)],
 'leg_r':[(524,1014),(607,1018),(601,1052),(588,1110),(571,1163),(554,1196),(563,1198),(565,1238),(549,1247),(548,1294),(571,1317),(579,1334),(578,1356),(470,1361),(453,1344),(462,1234),(455,1230),(461,1191),(480,1182),(493,1128),(509,1068)],
 'leg_l':[(625,1016),(699,1017),(695,1077),(688,1132),(689,1194),(701,1194),(714,1231),(700,1246),(699,1290),(736,1314),(761,1328),(761,1357),(617,1358),(607,1340),(616,1242),(607,1230),(613,1192),(623,1190),(622,1134),(621,1069)],
}
canvas_poly=box(0,0,textures['reference']['w'],textures['reference']['h']);used=GeometryCollection();parts={}
for name,points in polys.items():
    g=Polygon(points).buffer(0).intersection(canvas_poly).difference(used)
    parts[name]=g;used=used.union(g)
parts['body']=canvas_poly.difference(used)

slots=[];attachments={};geometry={}
def slot(name,bone,default=None):
    if name not in attachments:
        slots.append({'name':name,'bone':bone,**({'attachment':default} if default else {})});attachments[name]={}

def polygons(g):
    if isinstance(g,Polygon):yield g
    elif hasattr(g,'geoms'):
        for v in g.geoms:yield from polygons(v)

def mesh_geometry(shape,step=28):
    points=[];lookup={};tri=[]
    def vertex(p):
        key=(round(float(p[0]),7),round(float(p[1]),7))
        if key not in lookup:lookup[key]=len(points);points.append(key)
        return lookup[key]
    if shape.is_empty:return [],[]
    minx,miny,maxx,maxy=shape.bounds
    for y in range(math.floor(miny/step)*step,math.ceil(maxy/step)*step,step):
      for x in range(math.floor(minx/step)*step,math.ceil(maxx/step)*step,step):
        cell=shape.intersection(box(x,y,x+step,y+step))
        for poly in polygons(cell):
            if poly.area<1e-6:continue
            rings=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors]
            coords=np.array([p for ring in rings for p in ring],dtype=np.float64)
            ends=np.cumsum([len(r) for r in rings],dtype=np.uint32)
            indices=mapbox_earcut.triangulate_float64(coords,ends)
            ids=[vertex(p) for p in coords]
            for i in indices:tri.append(ids[int(i)])
    return points,tri

def inverse_bind(name,x,y):
    bx,by,a=bind[name];r=math.radians(-a);dx,dy=x-bx,y-by
    return (dx*math.cos(r)-dy*math.sin(r),dx*math.sin(r)+dy*math.cos(r))

def make_mesh(slot_name,name,texture,shape,weight_fn,point_fn=world,default=False,step=28):
    slot(slot_name,'root',name if default else None)
    tex=textures[texture];points,tri=mesh_geometry(shape,step);verts=[];uv=[];expected=[]
    for x,y in points:
        wx,wy=point_fn(x,y);uv.extend([x/tex['w'],y/tex['h']]);expected.extend([wx,wy])
        weights={k:v for k,v in weight_fn(x,y).items() if v>1e-7};total=sum(weights.values());verts.append(len(weights))
        for bone,w in weights.items():
            lx,ly=inverse_bind(bone,wx,wy);verts.extend([bid[bone],roundv(lx),roundv(ly),w/total])
    attachment={'type':'mesh','path':texture,'uvs':uv,'triangles':tri,'vertices':verts,'hull':0,'width':tex['w']*S,'height':tex['h']*S}
    attachments[slot_name][name]=attachment
    alpha=tex['image'].getchannel('A')
    visible=[i for i,(x,y) in enumerate(points) if alpha.getpixel((max(0,min(tex['w']-1,round(x))),max(0,min(tex['h']-1,round(y)))))>64]
    geometry[name]={'points':points,'expected_world':expected,'triangles':tri,'visible_vertices':visible}
    return attachment

def arm_weights(side,x,y):
    # Blend inside the elbow, keep hand and sleeve endpoints on their own bone.
    e=P['elbow_'+side];a=P['shoulder_'+side];g=P['grip_'+side];p=world(x,y)
    v=(g[0]-a[0],g[1]-a[1]);dot=lambda p:(p[0]-a[0])*v[0]+(p[1]-a[1])*v[1]
    projection=(dot(p)-dot(e))/math.hypot(*v)
    t=smooth((projection+5)/10)
    return {'upper_'+side:1-t,'fore_'+side:t}

def leg_weights(side,x,y):
    if y>=1203:return {'foot_'+side:1}
    t=smooth((y-1085)/85)
    f=smooth((y-1175)/28)
    return {'thigh_'+side:(1-t)*(1-f),'shin_'+side:t*(1-f),'foot_'+side:f}

def body_weights(x,y):
    if y>926 and x<504:return {'cape_l':1}
    if y>1012 and x>698:return {'cape_r':1}
    t=smooth((y-805)/150)
    return {'chest':1-t,'pelvis':t}

# Concealed costume, drawn behind all original-visible parts. A smaller inner
# patch prevents new art from enlarging the original idle silhouette.
# Map the generated plate to the actual collar/hem coordinates in the source.
def fill_point(x,y):
    return world(628+(x-650)*.53,656+(y-286)*.64)
fill_shape=Polygon([(500,325),(740,325),(772,490),(789,813),(848,1022),(357,1022),(408,790),(477,480)])
def fill_weights(x,y):
    wx,wy=fill_point(x,y);sx=wx/S+ORIGIN[0];sy=ORIGIN[1]-wy/S
    return body_weights(sx,sy)
# A dark inner-cape sample fills the space behind moving legs without copying
# a second gold hem or border into the silhouette.
def cape_gap_point(x,y):return world(483+(x-430)*6.7,1001+(y-970)*1.03)
make_mesh('costume_under','costume_under','body_base',box(430,970,463,1126),lambda x,y:{'pelvis':1},cape_gap_point,True,22)
head_area=Polygon(polys['head']).buffer(0)
leg_area=Polygon(polys['leg_r']).union(Polygon(polys['leg_l']))
cape_outline=Polygon([(473,679),(696,652),(726,805),(792,1044),(808,1202),(755,1175),(686,1150),(575,1143),(490,1148),(401,1176),(337,1201),(357,1070),(395,961),(434,839)])
repair_body=canvas_poly.difference(head_area).difference(leg_area).intersection(cape_outline)
make_mesh('body_repair','body_repair','body_base',repair_body,body_weights,default=True)
# Use the original visible center of the costume; the repaired base covers
# exposed cape and removes minified texture bleed from the former arm/staff.
removed=Polygon(polys['staff']).union(Polygon(polys['arm_r'])).union(Polygon(polys['arm_l'])).union(Polygon(polys['hand_r'])).union(Polygon(polys['hand_l']))
visible_torso=Polygon([(471,680),(706,650),(710,781),(742,933),(752,1017),(488,1019),(505,905),(534,849),(516,777)])
make_mesh('body','body','reference',parts['body'].difference(removed.buffer(10)).intersection(visible_torso),body_weights,default=True)
for side in ['l','r']:
    make_mesh('leg_'+side,'leg_'+side,'reference',parts['leg_'+side],lambda x,y,s=side:leg_weights(s,x,y),default=True)
make_mesh('staff','staff','reference',parts['staff'],lambda x,y:{'staff':1},default=True)
for side in ['l','r']:
    make_mesh('arm_'+side,'arm_'+side,'reference',parts['arm_'+side],lambda x,y,s=side:arm_weights(s,x,y),default=True)
make_mesh('hand_r','hand_r','reference',parts['hand_r'],lambda x,y:{'grip_r':1},default=True)
make_mesh('hand_l','hand_open','reference',parts['hand_l'],lambda x,y:{'hand_l':1},default=True)
make_mesh('head_repair','head_repair','body_base',head_area,lambda x,y:{'head':1},default=True)
make_mesh('head','head','reference',parts['head'].difference(Polygon(polys['staff']).buffer(10)),lambda x,y:{'head':1},default=True)

# Just the eye patch changes; the face contour and hair always use reference.
eye=Polygon([(527,495),(635,495),(648,525),(641,591),(530,592),(526,551)])
make_mesh('eye','eye_blink','blink',eye,lambda x,y:{'head':1},default=False,step=16)
make_mesh('eye','eye_tired','tired',eye.union(box(620,601,681,634)),lambda x,y:{'head':1},default=False,step=16)

# Left support grip. Orient generated wrist-to-grasp axis to the original
# forearm direction; its grasp maps exactly to the terminal IK target.
native_grip=(740,560);native_wrist=(470,937)
native_angle=math.atan2(native_wrist[1]-native_grip[1],native_grip[0]-native_wrist[0])
fore_angle=math.radians(bind['fore_l'][2]);grip_scale=.112*S;rotation=fore_angle-native_angle
def grip_point(x,y):
    dx=(x-native_grip[0])*grip_scale;dy=(native_grip[1]-y)*grip_scale
    return (P['grip_l'][0]+dx*math.cos(rotation)-dy*math.sin(rotation),P['grip_l'][1]+dx*math.sin(rotation)+dy*math.cos(rotation))
make_mesh('hand_l','hand_support','support_grip',box(305,255,1050,1104),lambda x,y:{'hand_l':1},grip_point,False,45)

order=['costume_under','body_repair','body','leg_l','leg_r','head_repair','staff','arm_l','arm_r','hand_r','hand_l','head','eye']
slots.sort(key=lambda s:order.index(s['name']))
ik=[]
for i,side in enumerate(['r','l']):
    ik.append(dict(name='hand_lock_'+side,order=i,bones=['upper_'+side,'fore_'+side],target='grip_'+side,mix=1,bendPositive=(side=='l'),stretch=True))
for i,side in enumerate(['r','l']):
    ik.append(dict(name='foot_lock_'+side,order=2+i,bones=['thigh_'+side,'shin_'+side],target='foot_'+side,mix=1,bendPositive=True,stretch=True))

# All motions start from the same source-aligned rig. Poses are offsets from
# setup. Foot targets and the right-hand staff target are explicitly tracked.
IDLE=dict(body_x=0,body_y=0,body_r=0,chest_r=0,head_r=0,cape_l=0,cape_r=0,
          staff_x=0,staff_y=0,staff_r=0,left_x=0,left_y=0,
          foot_rx=0,foot_ry=0,foot_rr=0,foot_lx=0,foot_ly=0,foot_lr=0)
def pose(**kw):return dict(IDLE,**kw)
def blend(a,b,t):return {k:mix(a[k],b[k],t) for k in IDLE}
def through(keys,t):
    for (ta,a),(tb,b) in zip(keys,keys[1:]):
        if t<=tb:return blend(a,b,smooth((t-ta)/(tb-ta)))
    return dict(keys[-1][1])
def hold_both(p):
    p=dict(p);a=math.radians(p['staff_r']);dx,dy=-42*S,122*S
    x=P['grip_r'][0]+p['staff_x']+dx*math.cos(a)-dy*math.sin(a)
    y=P['grip_r'][1]+p['staff_y']+dx*math.sin(a)+dy*math.cos(a)
    p['left_x']=x-P['grip_l'][0];p['left_y']=y-P['grip_l'][1]
    return p
CHANT=hold_both(pose(body_r=-2,head_r=2,staff_x=98,staff_y=-8,staff_r=-75))
RELEASE=hold_both(pose(body_x=8,body_y=-4.5,body_r=-8,chest_r=-2,head_r=9,staff_x=112,staff_y=-10,staff_r=-96,cape_l=5,cape_r=3))
TIRED=pose(body_y=-14,body_r=4,head_r=-9,staff_x=4,staff_y=-10,staff_r=-5,left_y=-8)
SIT=pose(body_x=-5,body_y=-43,body_r=16,head_r=-17,cape_l=-6,cape_r=6,
         staff_x=0,staff_y=-16,staff_r=-25,left_x=-5,left_y=-5,
         foot_rx=45,foot_ry=0,foot_rr=0,foot_lx=43,foot_ly=0,foot_lr=0)
DOWN=pose(body_x=-5,body_y=-25,body_r=77,head_r=-18,cape_l=27,cape_r=-65,
          staff_x=46,staff_y=-94,staff_r=-108,left_x=-65,left_y=-28,
          foot_rx=68,foot_ry=-5,foot_rr=65,foot_lx=14,foot_ly=-10,foot_lr=73)
DEAD=pose(body_x=-8,body_y=-22,body_r=82,head_r=-22,cape_l=30,cape_r=-69,
          staff_x=44,staff_y=-96,staff_r=-108,left_x=-71,left_y=-38,
          foot_rx=59,foot_ry=-13,foot_rr=63,foot_lx=11,foot_ly=-7,foot_lr=75)

def shoulder_world(side,p):
    def rotate(v,a):r=math.radians(a);return(v[0]*math.cos(r)-v[1]*math.sin(r),v[0]*math.sin(r)+v[1]*math.cos(r))
    base=P['pelvis'];c=rotate((P['chest'][0]-base[0],P['chest'][1]-base[1]),p['body_r'])
    chest=(base[0]+p['body_x']+c[0],base[1]+p['body_y']+c[1])
    a0=rotate((P['shoulder_'+side][0]-P['chest'][0],P['shoulder_'+side][1]-P['chest'][1]),p['body_r']+p['chest_r'])
    return (chest[0]+a0[0],chest[1]+a0[1])

def solve_arm(side,p):
    # Compute the forearm world angle for hand artwork orientation. Spine's IK
    # solves the same two-link chain during playback; this does not drive bones.
    a=shoulder_world(side,p);g=P['grip_'+side]
    t=(g[0]+p['left_x'],g[1]+p['left_y']) if side=='l' else (g[0]+p['staff_x'],g[1]+p['staff_y'])
    l1=dist(P['shoulder_'+side],P['elbow_'+side]);l2=dist(P['elbow_'+side],P['grip_'+side])
    dx,dy=t[0]-a[0],t[1]-a[1];d=math.hypot(dx,dy)
    ca=max(-1,min(1,(d*d-l1*l1-l2*l2)/(2*l1*l2)));b=math.acos(ca)*(1 if side=='l' else -1)
    alpha=math.atan2(dy,dx)-math.atan2(l2*math.sin(b),l1+l2*math.cos(b))
    return math.degrees(alpha+b)

# Measure the actual opaque prop silhouette, not just mesh vertices, so a
# curved staff tip cannot tunnel between sparsely sampled vertices.
alpha_array=np.asarray(textures['reference']['image'].getchannel('A'))
ay,ax=np.nonzero(alpha_array>64)
staff_mask=contains_xy(parts['staff'],ax+.5,ay+.5)
staff_hull=MultiPoint(np.column_stack([ax[staff_mask]+.5,ay[staff_mask]+.5])).convex_hull
staff_points=[world(x,y) for x,y in list(staff_hull.exterior.coords)]
def safe_prop(p):
    p=dict(p);r=math.radians(p['staff_r']);gx,gy=P['grip_r']
    low=min((x-gx)*math.sin(r)+(y-gy)*math.cos(r)+gy+p['staff_y'] for x,y in staff_points)
    if low<1:p['staff_y']+=1-low
    # Avoid the singular inner radius while the falling arm folds tightly.
    a=shoulder_world('r',p);tx=gx+p['staff_x'];ty=gy+p['staff_y'];dx,dy=tx-a[0],ty-a[1];d=math.hypot(dx,dy)
    minimum=abs(dist(P['shoulder_r'],P['elbow_r'])-dist(P['elbow_r'],P['grip_r']))+.03
    if d<minimum:
        p['staff_x']+=dx/max(d,1e-7)*(minimum-d);p['staff_y']+=dy/max(d,1e-7)*(minimum-d)
    return p

animations={};pose_samples={}
def sampled(name,duration,fn,support=False,blink=None,events=None):
    tracks={};poses=[]
    def add(b,c,t,**values):tracks.setdefault(b,{}).setdefault(c,[]).append(dict(time=roundv(t),**{k:roundv(v) for k,v in values.items()}))
    for i in range(round(duration*60)+1):
        t=min(i/60,duration);p=safe_prop(fn(t));poses.append(p)
        add('pelvis','translate',t,x=p['body_x'],y=p['body_y']);add('pelvis','rotate',t,value=p['body_r'])
        for b,key in [('chest','chest_r'),('head','head_r'),('cape_l','cape_l'),('cape_r','cape_r')]:add(b,'rotate',t,value=p[key])
        add('staff','translate',t,x=p['staff_x'],y=p['staff_y']);add('staff','rotate',t,value=p['staff_r'])
        add('grip_l','translate',t,x=p['left_x'],y=p['left_y'])
        hand_angle=solve_arm('l',p)-bind['fore_l'][2]
        # Keep angle continuous around the reference orientation.
        hand_angle=(hand_angle+180)%360-180
        add('hand_l','rotate',t,value=hand_angle)
        for side in ['r','l']:
            add('foot_'+side,'translate',t,x=p['foot_'+side+'x'],y=p['foot_'+side+'y'])
            add('foot_'+side,'rotate',t,value=p['foot_'+side+'r'])
    anim={'bones':tracks,'slots':{'hand_l':{'attachment':[{'time':0,'name':'hand_support' if support else 'hand_open'}]},'eye':{'attachment':blink or [{'time':0,'name':None}]}}}
    if events:anim['events']=events
    animations[name]=anim;pose_samples[name]=poses
    return anim

def idle(t):
    k=math.sin(t/4*math.tau);return pose(body_y=.32*k,head_r=.06*k,cape_l=.16*k,cape_r=-.13*k)
sampled('idle_loop',4,idle,blink=[{'time':0,'name':None},{'time':2.4,'name':'eye_blink'},{'time':2.53,'name':None},{'time':4,'name':None}])
cast=pose(head_r=2,left_x=19,left_y=62,cape_r=-2)
sampled('cast_short',.7,lambda t:through([(0,IDLE),(.2,cast),(.41,cast),(.7,IDLE)],t))
a=sampled('chant_enter',.7,lambda t:blend(IDLE,CHANT,smooth(t/.7)))
a['slots']['hand_l']['attachment']=[{'time':0,'name':'hand_open'},{'time':.57,'name':'hand_support'}]
sampled('chant_loop',2,lambda t:hold_both(dict(CHANT,body_y=.28*math.sin(t/2*math.tau),cape_l=.3*math.sin(t/2*math.tau))),True)
a=sampled('chant_cancel',.6,lambda t:blend(CHANT,IDLE,smooth(t/.6)),True)
a['slots']['hand_l']['attachment'].append({'time':.12,'name':'hand_open'})
sampled('chant_ack',.5,lambda t:dict(CHANT,head_r=2-3*math.sin(t/.5*math.pi)),True)
short=pose(body_r=-4,head_r=3,staff_x=45,staff_y=14,staff_r=-44,left_x=4,left_y=12,cape_l=3)
sampled('attack_short',.65,lambda t:through([(0,IDLE),(.15,pose(body_r=2)),(.28,short),(.38,short),(.65,IDLE)],t),events=[{'time':.28,'name':'impact','string':'ordinary'}])
wind=hold_both(dict(CHANT,body_r=2,head_r=-2,staff_x=86,staff_y=-5,staff_r=-69))
sampled('explosion_release',.6,lambda t:hold_both(through([(0,CHANT),(.28,wind),(.4,RELEASE),(.6,RELEASE)],t)),True,events=[{'time':.4,'name':'release','string':'explosion'}])
sampled('explosion_hold',.6,lambda t:hold_both(dict(RELEASE,cape_l=5+.3*math.sin(t/.6*math.tau))),True)
a=sampled('explosion_exit',.5,lambda t:blend(RELEASE,TIRED,smooth(t/.5)),True)
a['slots']['hand_l']['attachment'].append({'time':.18,'name':'hand_open'})
a['slots']['eye']['attachment'].append({'time':.24,'name':'eye_tired'})
for name,base,support in [('hit',IDLE,False),('hit_chant',CHANT,True)]:
    recoil=dict(base,body_r=base['body_r']+5,body_y=base['body_y']-2,head_r=-6,cape_l=-3)
    sampled(name,.4,lambda t,b=base,r=recoil:through([(0,b),(.07,r),(.15,r),(.4,b)],t),support,
            [{'time':0,'name':None},{'time':.045,'name':'eye_tired'},{'time':.27,'name':None}])
closed=[{'time':0,'name':'eye_tired'}]
sampled('relaxed_fall',1.05,lambda t:through([(0,TIRED),(.38,SIT),(.57,SIT),(1.05,DOWN)],t),blink=closed)
sampled('relaxed_loop',3,lambda t:dict(DOWN,body_y=DOWN['body_y']+.2*math.sin(t/3*math.tau)),blink=closed)
sampled('get_up',1.3,lambda t:through([(0,DOWN),(.56,SIT),(.74,SIT),(1.3,IDLE)],t),blink=[{'time':0,'name':'eye_tired'},{'time':.74,'name':None}])
sampled('dead',1.1,lambda t:through([(0,IDLE),(.2,TIRED),(.47,SIT),(1.0,DEAD),(1.1,DEAD)],t),blink=closed)
sampled('dead_from_down',.35,lambda t:blend(DOWN,DEAD,smooth(t/.35)),blink=closed)
sampled('hit_down',.3,lambda t:dict(DOWN,body_x=DOWN['body_x']-1.4*math.sin(t/.3*math.pi)),blink=closed)
sampled('setup_pose',4,lambda t:IDLE)

exec((ROOT/'tools/actions_v4_overrides.py').read_text(encoding='utf-8'))

raw={'skeleton':{'hash':'megumin-faithful-layered-v4','spine':'4.2.11','x':-270,'y':-10,'width':570,'height':400,'images':'../images/','fps':60},
     'bones':bones,'slots':slots,'ik':ik,'skins':[{'name':'default','attachments':attachments}],
     'events':{'impact':{'string':'ordinary'},'release':{'string':'explosion'}},'animations':animations}
content=json.dumps(raw,ensure_ascii=False,separators=(',',':'))
for file in ['megumin.json','megumin.spine-json']:(EXPORT/file).write_text(content,encoding='utf-8')
(OUT/'geometry.json').write_text(json.dumps(geometry,separators=(',',':')),encoding='utf-8')
(OUT/'source/partition.json').write_text(json.dumps(polys,indent=2),encoding='utf-8')
manifest={'version':'0.4.0','spine':'4.2.11','bones':len(bones),'slots':len(slots),'animations':list(animations),
          'attachments':{s:list(a) for s,a in attachments.items()},'source_scale':S,'source_origin':ORIGIN,
          'texture_filters':'MipMapLinearLinear / Linear; power-of-two padding, no raster resampling',
          'artwork':'Approved idle body retained; geometric UV cuts plus built-in imagegen sleeve, palm, leg, boot, torso/cape and local expression correctives. Original raster source pixels preserved in atlas packing.',
          'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'source').glob('*.png')},
          'limitations':['No native Spine editor or STS2 import verified.','Drawings and motion require visual review; source-aligned pose alone is not an animation-quality guarantee.']}
(EXPORT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['version','bones','slots','animations']},ensure_ascii=False,indent=2))
