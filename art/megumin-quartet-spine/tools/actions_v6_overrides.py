"""V5 corrective rig; executed by build_actions_v6.py in its authoring context."""
add_bone('hand_r_free',P['grip_r'],'grip_r')
add_bone('hat_follow',P['head'],'head')
add_bone('hair_follow',P['head'],'head')
add_bone('ground_cape',(0,0))

# Geometric source selection only. The full raster sources remain unchanged.
def axis_map(start,end,a,b,width_scale):
    sx,sy=start;dx=end[0]-sx;dy=end[1]-sy;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
    vx,vy=b[0]-a[0],b[1]-a[1];vl=math.hypot(vx,vy);nx,ny=-vy/vl,vx/vl
    def mapped(x,y):
        along=((x-sx)*ux+(y-sy)*uy)/length
        across=((x-sx)*(-uy)+(y-sy)*ux)*width_scale
        return (a[0]+vx*along-nx*across,a[1]+vy*along-ny*across)
    return mapped

def hand_map(anchor,target,scale,orientation=0):
    a=math.radians(orientation)
    def mapped(x,y):
        dx=(x-anchor[0])*scale;dy=(anchor[1]-y)*scale
        return (target[0]+dx*math.cos(a)-dy*math.sin(a),target[1]+dx*math.sin(a)+dy*math.cos(a))
    return mapped

for side in ['r','l']:
    a,e,g=P['shoulder_'+side],P['elbow_'+side],P['grip_'+side]
    fa=math.radians(bind['fore_'+side][2]);wrist=(g[0]-6*math.cos(fa),g[1]-6*math.sin(fa))
    make_mesh('upper_piece_'+side,'upper_piece_'+side,'arms',box(35,165,478,410),lambda x,y,s=side:{'upper_'+s:1},axis_map((76,277),(439,320),a,e,.065),True,45)
    make_mesh('fore_piece_'+side,'fore_piece_'+side,'arms',box(568,210,1000,432),lambda x,y,s=side:{'fore_'+s:1},axis_map((612,301),(967,325),e,wrist,.074),True,45)
    # Thigh and shin stay separate at a bent knee, with rounded overlap.
    h,k,f=P['hip_'+side],P['knee_'+side],P['ankle_'+side]
    if side=='r':
        thigh_shape=box(252,92,423,355);thigh_start=(340,113);thigh_end=(345,321)
        shin_shape=box(697,106,840,400);shin_start=(769,147);shin_end=(765,380)
    else:
        thigh_shape=box(1111,95,1295,479);thigh_start=(1202,127);thigh_end=(1198,441)
        shin_shape=box(226,590,379,980);shin_start=(302,623);shin_end=(305,944)
    make_mesh('thigh_piece_'+side,'thigh_piece_'+side,'legs',thigh_shape,lambda x,y,s=side:{'thigh_'+s:1},axis_map(thigh_start,thigh_end,h,k,.098),True,40)
    make_mesh('shin_piece_'+side,'shin_piece_'+side,'legs',shin_shape,lambda x,y,s=side:{'shin_'+s:1},axis_map(shin_start,shin_end,k,f,.098),True,40)
    make_mesh('boot_piece_'+side,'boot_piece_'+side,'legs',box(598,578,923,954),lambda x,y,s=side:{'foot_'+s:1},hand_map((734,621),f,.095),True,40)
    make_mesh('boot_piece_'+side,'boot_sole_'+side,'legs',box(1055,595,1451,970),lambda x,y,s=side:{'foot_'+s:1},hand_map((1175,643),f,.095),False,40)

# New palm/sleeve artwork is small and matched to the original limb widths.
make_mesh('hand_l','hand_cast','arms',box(1108,62,1520,477),lambda x,y:{'hand_l':1},hand_map((1164,421),P['grip_l'],.051,bind['fore_l'][2]-60),False,35)
make_mesh('hand_l','hand_ground','arms',box(580,614,992,940),lambda x,y:{'hand_l':1},hand_map((648,681),P['grip_l'],.052,0),False,35)
make_mesh('hand_r','hand_free','arms',box(1099,674,1500,967),lambda x,y:{'hand_r_free':1},hand_map((1149,744),P['grip_r'],.051,bind['fore_r'][2]),False,35)

def torso_map(x,y):return world(628+(x-232)*.63,662+(y-124)*.725)
make_mesh('torso_fill','torso_fill','costume',box(48,103,442,616),lambda x,y:{'chest':1-smooth((y-290)/230),'pelvis':smooth((y-290)/230)},torso_map,True,35)
make_mesh('ground_cape','ground_cape','costume',box(1080,270,2098,710),lambda x,y:{'ground_cape':1},lambda x,y:((x-1600)*.20,(710-y)*.105+1),True,40)
make_mesh('body_repair','body_repair_upper','body_base',repair_body.intersection(box(0,0,1148,1027)),body_weights,default=False)

face_patch=Polygon([(523,447),(640,445),(650,526),(645,594),(527,594)]).union(box(615,595,687,654))
for name,tex in [('face_focus','focus'),('face_release','release_face'),('face_hit','hit_face')]:
    make_mesh('eye',name,tex,face_patch,lambda x,y:{'head':1},default=False,step=16)

# Reweight only the existing hat and long hair. Setup coordinates are exact.
def head_follow(x,y):
    hat=1-smooth((y-382)/115)
    hair=smooth((y-647)/118)*(1 if x<563 or x>706 else 0)*(1-hat)
    return {'head':1-hat-hair,'hat_follow':hat,'hair_follow':hair}
for s,tex,shape in [('head','reference',parts['head'].difference(Polygon(polys['staff']).buffer(10))),('head_repair','body_base',head_area)]:
    make_mesh(s,s,tex,shape,head_follow,default=True)

# A narrow boot-edge fragment was inside the old staff partition. Keep only
# the staff's own shaft/tip contour at its lower end.
staff_shape=parts['staff'].difference(Polygon([(465,1298),(480,1298),(480,1368),(426,1368),(429,1350),(457,1349)]))
make_mesh('staff','staff','reference',staff_shape,lambda x,y:{'staff':1},default=True)

# Turned artwork is an alternate attachment set, never a horizontal mirror.
def side_head_point(x,y):return (P['head'][0]+(x-703)*.225,P['head'][1]+(685-y)*.225)
def side_body_point(x,y):return (P['head'][0]+(x-1398)*.16,P['head'][1]+(272-y)*.16)
make_mesh('side_head','side_head','side',box(30,10,1080,870),lambda x,y:{'head':1},side_head_point,True,35)
make_mesh('side_body','side_body','side',box(1100,195,1615,926),lambda x,y:{'chest':1-smooth((y-420)/300),'pelvis':smooth((y-420)/300)},side_body_point,True,35)
side_front=Polygon([(1274,232),(1490,236),(1508,390),(1532,571),(1584,770),(1460,794),(1270,758),(1340,596),(1368,455),(1392,388),(1402,274)])
make_mesh('side_front','side_front','side',side_front,lambda x,y:{'chest':1-smooth((y-420)/300),'pelvis':smooth((y-420)/300)},side_body_point,True,25)
def side_face_point(x,y):
    if y<595:return side_head_point(701+(x-588)*.46,556+(y-544)*.95)
    return side_head_point(751+(x-649)*.5,642+(y-622)*.7)
make_mesh('eye','side_shout','release_face',box(615,597,680,649),lambda x,y:{'head':1},side_face_point,False,12)
make_mesh('eye','side_hit','hit_face',box(529,495,643,589).union(box(615,597,680,649)),lambda x,y:{'head':1},side_face_point,False,12)

order=['ground_cape','costume_under','body_repair','torso_fill','body','side_body','side_front','leg_l','leg_r',
       'thigh_piece_l','shin_piece_l','boot_piece_l','thigh_piece_r','shin_piece_r','boot_piece_r',
       'head_repair','arm_l','arm_r','upper_piece_l','fore_piece_l','upper_piece_r','fore_piece_r',
       'head','side_head','eye','staff','hand_r','hand_l']
slots.sort(key=lambda s:order.index(s['name']))
new_slots=[s for s in order if '_piece_' in s]+['torso_fill','ground_cape','side_head','side_body','side_front']
for s in slots:
    if s['name'] in new_slots:s['color']='ffffff00'

# Retain the previous approved idle geometry, draw order and motion. The staff
# is brought in front only for action clips, using standard draw-order keys.
idle_order=['ground_cape','costume_under','body_repair','torso_fill','body','side_body','side_front','leg_l','leg_r',
       'thigh_piece_l','shin_piece_l','boot_piece_l','thigh_piece_r','shin_piece_r','boot_piece_r',
       'head_repair','staff','arm_l','arm_r','upper_piece_l','fore_piece_l','upper_piece_r','fore_piece_r',
       'hand_r','hand_l','head','side_head','eye']
slots.sort(key=lambda s:idle_order.index(s['name']))

IDLE.update(limbs=0,legs=0,free=0,right_x=0,right_y=0,groundcape=0,cape_x=0,cape_y=0,
            palm=0,hat=0,hair=0,knee=1,both=0,pelvis_r=0,turn=0,headturn=0,bendr=-1,prone=0,rearstaff=0)
def pose(**kw):return dict(IDLE,**kw)
def hold_both(p):
    p=dict(p);a=math.radians(p['staff_r']);dx,dy=-19,57
    p['left_x']=P['grip_r'][0]+p['staff_x']+dx*math.cos(a)-dy*math.sin(a)-P['grip_l'][0]
    p['left_y']=P['grip_r'][1]+p['staff_y']+dx*math.sin(a)+dy*math.cos(a)-P['grip_l'][1]
    return p
CHANT=pose(body_r=-6,chest_r=-2,head_r=3,staff_x=120,staff_y=34,staff_r=-88,limbs=1,left_x=-73,left_y=4,turn=1)
RELEASE=pose(body_x=7,body_y=-3,body_r=-11,chest_r=-3,head_r=2,staff_x=141,staff_y=28,staff_r=-94,cape_l=5,cape_r=4,limbs=1,hat=1.5,hair=2,left_x=-80,left_y=7,turn=1)
TIRED=pose(body_y=-12,body_r=6,head_r=-11,staff_x=4,staff_y=-10,staff_r=-5,left_y=-8,limbs=1,legs=1,knee=-1,hat=-1)
SIT=pose(body_x=-1,body_y=-47,body_r=12,head_r=-12,staff_x=15,staff_y=-28,staff_r=-26,
         left_x=-31,left_y=-60,limbs=1,legs=1,foot_rx=32,foot_lx=27,knee=-1,groundcape=1,cape_x=-20)
DOWN=pose(body_x=-4,body_y=-18,body_r=84,head_r=-29,staff_x=80,staff_y=-105,staff_r=-109,
          left_x=-52,left_y=-21,free=1,right_x=-25,right_y=31,limbs=1,legs=1,groundcape=1,cape_x=-45,
          foot_rx=70,foot_ry=12,foot_rr=74,foot_lx=27,foot_ly=14,foot_lr=36,knee=-1,hat=-2,hair=-3,pelvis_r=84)
# A different collapsed side silhouette: head hangs, knees drawn in, hands slack.
DEAD=pose(body_x=-25,body_y=-45,body_r=60,chest_r=-3,head_r=8,staff_x=87,staff_y=-105,staff_r=-109,
          left_x=-92,left_y=-29,free=1,right_x=-38,right_y=20,limbs=1,legs=1,groundcape=1,cape_x=-55,
          foot_rx=37,foot_ry=-19,foot_rr=90,foot_lx=5,foot_ly=-17,foot_lr=85,knee=-1,hat=-3,hair=-5,pelvis_r=60)
SUPPORT=pose(body_x=-1,body_y=-49,body_r=72,head_r=-31,staff_x=80,staff_y=-105,staff_r=-109,
          left_x=-71,left_y=-65.9,free=1,right_x=0,right_y=30,limbs=1,legs=1,groundcape=1,cape_x=-41,
          foot_rx=32,foot_ry=0,foot_rr=0,foot_lx=27,foot_ly=0,foot_lr=0,knee=-1,palm=1)
CROUCH=pose(body_x=0,body_y=-60,body_r=50,head_r=-25,staff_x=80,staff_y=-105,staff_r=-109,
          left_x=-71,left_y=-65.9,free=1,right_x=14,right_y=35,limbs=1,legs=1,groundcape=1,cape_x=-30,
          foot_rx=32,foot_lx=27,knee=-1,palm=1)

base_shoulder_world=shoulder_world
def prone_shoulder_x(side,p):
    return -5 if side=='r' else 5-20*smooth((p['prone']-.55)/.45)
def shoulder_world(side,p):
    x,y=base_shoulder_world(side,p)
    r=math.radians(p['body_r']+p['chest_r'])
    projection=math.cos(math.radians(p['turn']*50))
    dx=(P['shoulder_'+side][0]-P['chest'][0])*(projection-1)
    dx=mix(dx,prone_shoulder_x(side,p)-(P['shoulder_'+side][0]-P['chest'][0]),p['prone'])
    x+=dx*math.cos(r);y+=dx*math.sin(r)
    return x,y

def solve_arm(side,p):
    a=shoulder_world(side,p);g=P['grip_'+side]
    if side=='l':t=(g[0]+p['left_x'],g[1]+p['left_y'])
    else:t=(mix(g[0]+p['staff_x'],p['right_x'],p['free']),mix(g[1]+p['staff_y'],p['right_y'],p['free']))
    l1=dist(P['shoulder_'+side],P['elbow_'+side]);l2=dist(P['elbow_'+side],P['grip_'+side]);dx,dy=t[0]-a[0],t[1]-a[1];d=math.hypot(dx,dy)
    b=math.acos(max(-1,min(1,(d*d-l1*l1-l2*l2)/(2*l1*l2))))*(1 if side=='l' else p['bendr'])
    return math.degrees(math.atan2(dy,dx)-math.atan2(l2*math.sin(b),l1+l2*math.cos(b))+b)

# Constrain only rigid staff floor contact. The free hand is independent.
hand_mask=contains_xy(parts['hand_r'],ax+.5,ay+.5)
hand_hull=MultiPoint(np.column_stack([ax[hand_mask]+.5,ay[hand_mask]+.5])).convex_hull
held_hand_points=[world(x,y) for x,y in list(hand_hull.exterior.coords)]
def safe_prop(p):
    p=dict(p);r=math.radians(p['staff_r']);gx,gy=P['grip_r']
    contact_points=staff_points+(held_hand_points if p['free']<.18 else [])
    low=min((x-gx)*math.sin(r)+(y-gy)*math.cos(r)+gy+p['staff_y'] for x,y in contact_points)
    if low<1:p['staff_y']+=1-low
    # Keep targets out of the two-bone singular circle. Free hands are limited
    # by shoulder reach; while holding, any correction moves the rigid staff.
    for side in ['r','l']:
        sx,sy=shoulder_world(side,p);g=P['grip_'+side]
        if side=='r':tx,ty=mix(g[0]+p['staff_x'],p['right_x'],p['free']),mix(g[1]+p['staff_y'],p['right_y'],p['free'])
        else:tx,ty=g[0]+p['left_x'],g[1]+p['left_y']
        l1=dist(P['shoulder_'+side],P['elbow_'+side]);l2=dist(P['elbow_'+side],g)
        dx,dy=tx-sx,ty-sy;d=math.hypot(dx,dy)
        minimum=math.sqrt(l1*l1+l2*l2+2*l1*l2*math.cos(math.radians(140)))
        extension_margin=(.05+1.0*p['turn']) if side=='l' else .0000001
        safe=max(minimum,min(l1+l2-extension_margin,d))
        ox,oy=dx*(safe/max(d,1e-6)-1),dy*(safe/max(d,1e-6)-1)
        if side=='r' and p['free']<.5:
            p['staff_x']+=ox;p['staff_y']+=oy;p['left_x']+=ox*p['both'];p['left_y']+=oy*p['both']
        elif side=='r':
            p['right_x']+=ox/max(p['free'],.01);p['right_y']+=oy/max(p['free'],.01)
        else:p['left_x']+=ox;p['left_y']+=oy
    if p['legs']>.35:
        for side in ['r','l']:
            boots=['boot_piece_'+side]+(['boot_sole_r'] if side=='r' and p['foot_rr']>35 else [])
            bx,by=P['ankle_'+side];a=math.radians(p['foot_'+side+'r'])
            low=min((geometry[boot]['expected_world'][i*2]-bx)*math.sin(a)+(geometry[boot]['expected_world'][i*2+1]-by)*math.cos(a)+by+p['foot_'+side+'y'] for boot in boots for i in geometry[boot]['visible_vertices'])
            prone_leg='prone_leg_'+side
            if p['prone']>.45 and prone_leg in geometry:
                g=geometry[prone_leg]
                low=min(low,min((g['expected_world'][i*2]-bx)*math.sin(a)+(g['expected_world'][i*2+1]-by)*math.cos(a)+by+p['foot_'+side+'y'] for i in g['visible_vertices'] if g['points'][i][0]<1095))
            if low<.6:p['foot_'+side+'y']+=.6-low
    return p

saved_idle=animations['idle_loop'];saved_setup=animations['setup_pose'];animations={};pose_samples={}
def arm_arc_through(keys,t):
    # A hand crossing the shoulder cannot travel along a Cartesian chord: that
    # passes through the inner IK circle and reverses the elbow. Author a wrist
    # arc around the moving shoulder, with radius and angle eased separately.
    for (ta,a),(tb,b) in zip(keys,keys[1:]):
        if t<=tb:
            k=smooth((t-ta)/(tb-ta));aa=safe_prop(a);bb=safe_prop(b);p=blend(aa,bb,k)
            polar=[]
            for q in [aa,bb]:
                sx,sy=shoulder_world('r',q)
                tx=mix(P['grip_r'][0]+q['staff_x'],q['right_x'],q['free'])
                ty=mix(P['grip_r'][1]+q['staff_y'],q['right_y'],q['free'])
                polar.append((math.atan2(ty-sy,tx-sx),math.hypot(tx-sx,ty-sy)))
            angle0,radius0=polar[0];angle1,radius1=polar[1]
            delta=(angle1-angle0+math.pi)%math.tau-math.pi
            angle=angle0+delta*k;radius=mix(radius0,radius1,k);sx,sy=shoulder_world('r',p)
            tx,ty=sx+radius*math.cos(angle),sy+radius*math.sin(angle)
            if p['free']>.001:
                p['right_x']=(tx-(P['grip_r'][0]+p['staff_x'])*(1-p['free']))/p['free']
                p['right_y']=(ty-(P['grip_r'][1]+p['staff_y'])*(1-p['free']))/p['free']
            else:p['staff_x']=tx-P['grip_r'][0];p['staff_y']=ty-P['grip_r'][1]
            return p
    return dict(keys[-1][1])
def sampled(name,duration,fn,support=False,blink=None,events=None):
    tracks={};poses=[];slot_tracks={};iktracks={}
    def add(b,c,t,**values):tracks.setdefault(b,{}).setdefault(c,[]).append(dict(time=roundv(t),**{k:roundv(v) for k,v in values.items()}))
    def color(s,t,a):slot_tracks.setdefault(s,{}) .setdefault('rgba',[]).append({'time':roundv(t),'color':'ffffff'+format(round(max(0,min(1,a))*255),'02x'),'curve':'stepped'})
    hands=[];cape_keys=[];last_cape=None;boot_keys=[];last_boot=None;eye_keys=[];last_eye='unset';draw_keys=[];last_turn=None
    for i in range(math.ceil(duration*60)+1):
        t=min(i/60,duration);p=safe_prop(fn(t));poses.append(p)
        add('pelvis','translate',t,x=p['body_x'],y=p['body_y']);add('pelvis','rotate',t,value=p['pelvis_r'])
        add('torso','rotate',t,value=p['body_r']-p['pelvis_r'])
        for side in ['r','l']:
            dx=(P['shoulder_'+side][0]-P['chest'][0])*(math.cos(math.radians(p['turn']*50))-1)
            dx=mix(dx,prone_shoulder_x(side,p)-(P['shoulder_'+side][0]-P['chest'][0]),p['prone'])
            add('upper_'+side,'translate',t,x=dx,y=0)
        iktracks.setdefault('hand_lock_r',[]).append({'time':roundv(t),'mix':1,'bendPositive':p['bendr']>=0,'stretch':True})
        for b,key in [('chest','chest_r'),('head','head_r'),('cape_l','cape_l'),('cape_r','cape_r'),('hat_follow','hat'),('hair_follow','hair')]:add(b,'rotate',t,value=p[key])
        add('staff','translate',t,x=p['staff_x'],y=p['staff_y']);add('staff','rotate',t,value=p['staff_r'])
        gx,gy=P['grip_r'];dx=(p['right_x']-gx-p['staff_x'])*p['free'];dy=(p['right_y']-gy-p['staff_y'])*p['free'];r=math.radians(-p['staff_r'])
        add('grip_r','translate',t,x=dx*math.cos(r)-dy*math.sin(r),y=dx*math.sin(r)+dy*math.cos(r))
        add('grip_l','translate',t,x=p['left_x'],y=p['left_y'])
        ar=(solve_arm('r',p)-bind['fore_r'][2]-p['staff_r']+180)%360-180
        al=(solve_arm('l',p)-bind['fore_l'][2]+180)%360-180
        # Palm attachment is drawn for wrist-to-ground orientation, then kept level.
        add('hand_l','rotate',t,value=mix(al,0,p['palm']));add('hand_r_free','rotate',t,value=ar)
        add('ground_cape','translate',t,x=p['cape_x'],y=p['cape_y'])
        for side in ['r','l']:
            add('foot_'+side,'translate',t,x=p['foot_'+side+'x'],y=p['foot_'+side+'y']);add('foot_'+side,'rotate',t,value=p['foot_'+side+'r'])
            arm_visible=1 if p['limbs']>.35 else 0
            if name=='cast_short' and side=='r':arm_visible=0
            if name=='hit':arm_visible=0
            legs_visible=1 if p['legs']>.35 else 0
            for s in ['upper_piece_'+side,'fore_piece_'+side]:color(s,t,arm_visible)
            color('arm_'+side,t,1-arm_visible);color('leg_'+side,t,1-legs_visible)
            for s in ['thigh_piece_'+side,'shin_piece_'+side,'boot_piece_'+side]:color(s,t,legs_visible)
            iktracks.setdefault('foot_lock_'+side,[]).append({'time':roundv(t),'mix':1,'bendPositive':p['knee']>=0,'stretch':True})
        # Quartet A03 is a three-quarter pose. Retain the approved head and
        # shoulder identity throughout the turn: no opaque whole-face swap.
        turned=False;turn_alpha=0
        for s in ['head','head_repair','body','body_repair']:color(s,t,1-turn_alpha)
        for s in ['side_head','side_body','side_front']:color(s,t,turn_alpha)
        color('torso_fill',t,p['limbs']*(1-turn_alpha));ground=1 if p['groundcape']>.5 else 0;color('ground_cape',t,ground)
        color('costume_under',t,(1-ground)*(1-turn_alpha))
        prone_visible=p['prone']>.56
        if 'prone_body' in attachments:
            for s in ['prone_body','prone_head','prone_leg_r','prone_leg_l']:color(s,t,1 if prone_visible else 0)
            if prone_visible:
                for s in ['head','head_repair','body','body_repair','torso_fill','ground_cape','costume_under','leg_r','leg_l','thigh_piece_r','shin_piece_r','boot_piece_r','thigh_piece_l','shin_piece_l','boot_piece_l']:color(s,t,0)
        eye_name=None
        for key in blink or []:
            if key['time']<=t:eye_name=key['name']
        if turned:eye_name={'face_release':'side_shout','face_hit':'side_hit'}.get(eye_name)
        if prone_visible:eye_name=None
        if eye_name!=last_eye:eye_keys.append({'time':roundv(t),'name':eye_name});last_eye=eye_name
        layer_state=(p['rearstaff']>.5,p['turn']>.08)
        if layer_state!=last_turn:
            source=[s['name'] for s in slots];front=['staff','hand_r','hand_l'];rear=[]
            moved=front[:]
            desired=[s for s in source if s not in front]+front
            if p['rearstaff']>.5:
                moved=['staff','hand_r','fore_piece_r','hand_l']
                desired=[s for s in source if s not in moved]
                at=desired.index('head_repair');desired[at:at]=['fore_piece_r','staff','hand_r'];desired+=['hand_l']
            draw_keys.append({'time':roundv(t),'offsets':[{'slot':s,'offset':desired.index(s)-i} for i,s in enumerate(source) if s in moved]});last_turn=layer_state
        cape_name='body_repair_upper' if ground else 'body_repair'
        if cape_name!=last_cape:cape_keys.append({'time':roundv(t),'name':cape_name});last_cape=cape_name
        boot_name='boot_sole_r' if p['foot_rr']>45 and p['legs']>.95 else 'boot_piece_r'
        if boot_name!=last_boot:boot_keys.append({'time':roundv(t),'name':boot_name});last_boot=boot_name
        hands.append((t,'hand_free' if p['free']>.18 else 'hand_r','hand_ground' if p['palm']>.6 else 'hand_support' if support else 'hand_open'))
    for ix,s in [(1,'hand_r'),(2,'hand_l')]:
        values=[];last=None
        for row in hands:
            if row[ix]!=last:values.append({'time':roundv(row[0]),'name':row[ix]});last=row[ix]
        slot_tracks.setdefault(s,{})['attachment']=values
    slot_tracks['eye']={'attachment':eye_keys}
    slot_tracks.setdefault('body_repair',{})['attachment']=cape_keys
    slot_tracks['boot_piece_r']['attachment']=boot_keys
    for b,channels in tracks.items():
        for channel in ['rotate']:
            keys=channels.get(channel,[])
            for prev,key in zip(keys,keys[1:]):
                while key['value']-prev['value']>180:key['value']-=360
                while key['value']-prev['value']< -180:key['value']+=360
    # All action props/hands draw in front of the hat when crossing the body.
    anim={'bones':tracks,'slots':slot_tracks,'ik':iktracks,'drawOrder':draw_keys}
    if events:anim['events']=events
    animations[name]=anim;pose_samples[name]=poses;return anim

animations['idle_loop']=saved_idle
cast=pose(head_r=-2,left_x=20,left_y=67,limbs=1,cape_r=-2,hat=.6)
a=sampled('cast_short',.7,lambda t:through([(0,IDLE),(.22,cast),(.4,cast),(.7,IDLE)],t),blink=[{'time':0,'name':None},{'time':.18,'name':'face_focus'},{'time':.49,'name':None}])
a['slots']['hand_l']['attachment']=[{'time':0,'name':'hand_open'},{'time':.1,'name':'hand_cast'},{'time':.58,'name':'hand_open'}]
focus=[{'time':0,'name':'face_focus'}];shout=[{'time':0,'name':'face_release'}];closed=[{'time':0,'name':'eye_tired'}]
LIFT=pose(staff_x=32,staff_y=52,staff_r=-37,left_x=2,left_y=28,limbs=1)
ARC=pose(staff_x=75,staff_y=67,staff_r=-68,left_x=-16,left_y=27,limbs=1,turn=.5)
STRAIGHT=pose(body_y=.4)
NEG_STRAIGHT=dict(STRAIGHT,knee=-1)
a=sampled('chant_enter',1.05,lambda t:through([(0,IDLE),(.35,LIFT),(.62,ARC),(1.05,CHANT)],t),blink=[{'time':0,'name':None},{'time':.36,'name':'face_focus'}])
sampled('chant_loop',2,lambda t:dict(CHANT,body_y=.2*math.sin(t/2*math.tau),cape_l=.3*math.sin(t/2*math.tau)),False,focus)
sampled('chant_cancel',.95,lambda t:through([(0,CHANT),(.35,ARC),(.62,LIFT),(.95,IDLE)],t),False,[{'time':0,'name':'face_focus'},{'time':.6,'name':None}])
sampled('chant_ack',.5,lambda t:dict(CHANT,head_r=3-3*math.sin(t/.5*math.pi),hat=.6*math.sin(t/.5*math.pi)),False,focus)
short=dict(CHANT,body_y=-2,body_r=-7,head_r=-2,staff_x=120,staff_y=31,staff_r=-80,cape_l=3,hat=1.5)
sampled('attack_short',1.05,lambda t:through([(0,IDLE),(.2,LIFT),(.37,ARC),(.52,short),(.62,short),(.77,ARC),(.9,LIFT),(1.05,IDLE)],t),blink=[{'time':0,'name':None},{'time':.19,'name':'face_focus'},{'time':.92,'name':None}],events=[{'time':.52,'name':'impact','string':'ordinary'}])
wind=dict(CHANT,body_r=-2,head_r=-2,staff_x=105,staff_y=35,staff_r=-85,hat=-1,hair=-1)
sampled('explosion_release',.68,lambda t:through([(0,CHANT),(.3,wind),(.46,RELEASE),(.68,RELEASE)],t),False,[{'time':0,'name':'face_focus'},{'time':.34,'name':'face_release'}],[{'time':.46,'name':'release','string':'explosion'}])
sampled('explosion_hold',.6,lambda t:dict(RELEASE,cape_l=5+.3*math.sin(t/.6*math.tau)),False,shout)
sampled('explosion_exit',1.1,lambda t:through([(0,RELEASE),(.3,ARC),(.58,LIFT),(.83,STRAIGHT),(.88,NEG_STRAIGHT),(1.1,TIRED)],t),False,[{'time':0,'name':'face_release'},{'time':.21,'name':'eye_tired'}])
for name,base,support in [('hit',IDLE,False),('hit_chant',CHANT,False)]:
    recoil=dict(base,body_x=base['body_x']-3,body_r=base['body_r']+7,body_y=base['body_y']-2,head_r=7,cape_l=-4,hat=-3,hair=-2,limbs=1)
    sampled(name,.44,lambda t,b=base,r=recoil:through([(0,b),(.065,r),(.12,dict(r,hat=3,head_r=-2)),(.44,b)],t),support,[{'time':0,'name':'face_focus' if name=='hit_chant' else None},{'time':.035,'name':'face_hit'},{'time':.31,'name':'face_focus' if name=='hit_chant' else None}])
sampled('relaxed_fall',1.2,lambda t:arm_arc_through([(0,TIRED),(.36,SIT),(.52,SIT),(1.09,DOWN),(1.2,DOWN)],t),blink=closed)
sampled('relaxed_loop',3,lambda t:dict(DOWN,chest_r=.22*math.sin(t/3*math.tau)),blink=closed)
UP=pose(body_y=-15,body_r=-4,head_r=2,staff_x=32,staff_y=20,staff_r=-30,limbs=1,legs=.4,foot_rx=7,foot_lx=7,knee=-1)
STOOP=pose(body_y=-35,body_r=26,head_r=-16,staff_x=1,staff_y=-33,staff_r=-20,left_x=-35,left_y=-12,limbs=1,legs=1,foot_rx=24,foot_lx=17,knee=-1,groundcape=1,cape_x=-15)
def get_up(t):
    p=arm_arc_through([(0,DOWN),(.46,SUPPORT),(.86,CROUCH),(1.07,dict(CROUCH,palm=0,left_y=-30)),(1.25,dict(CROUCH,palm=0,left_y=-30,free=0)),(1.55,STOOP),(1.85,UP),(2.15,NEG_STRAIGHT),(2.2,STRAIGHT),(2.35,IDLE)],t)
    return p
a=sampled('get_up',2.35,get_up,blink=[{'time':0,'name':'eye_tired'},{'time':.92,'name':'face_focus'},{'time':2.15,'name':None}])
sampled('dead',1.5,lambda t:through([(0,IDLE),(.12,STRAIGHT),(.16,NEG_STRAIGHT),(.35,TIRED),(.63,SIT),(1.36,DEAD),(1.5,DEAD)],t),blink=[{'time':0,'name':None},{'time':.06,'name':'face_hit'},{'time':.4,'name':'eye_tired'}])
sampled('dead_from_down',.45,lambda t:blend(DOWN,DEAD,smooth(t/.45)),blink=closed)
sampled('hit_down',.3,lambda t:dict(DOWN,body_x=DOWN['body_x']-1.2*math.sin(t/.3*math.pi),head_r=DOWN['head_r']+2*math.sin(t/.3*math.pi)),blink=[{'time':0,'name':'eye_tired'},{'time':.03,'name':'face_hit'},{'time':.24,'name':'eye_tired'}])
animations['setup_pose']=saved_setup
exec((ROOT/'tools/actions_v6_choreography.py').read_text(encoding='utf-8'))
# Restore the exact reference draw order at every transition into approved idle.
for name in ['cast_short','chant_cancel','attack_short','hit','get_up']:
    animations[name]['drawOrder'].append({'time':max(k[-1]['time'] for b in animations[name]['bones'].values() for k in b.values()),'offsets':[]})

