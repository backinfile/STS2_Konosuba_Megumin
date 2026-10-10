"""Quartet A03 hand identity + authored 60 fps entry and prone recovery."""
plan=json.loads((ROOT/'chant-enter-plan/frame-plan.json').read_text(encoding='utf-8'))
def entry(t):
    frame=min(72,max(0,round(t*60)));q=plan['frames'][frame]
    return pose(body_x=q['root_x'],body_y=q['root_y'],body_r=q['lean'],head_r=-q['lean']*.65,
       turn=q['body_yaw']/50,headturn=q['head_yaw']/55,staff_x=q['wrist_r'][0]-P['grip_r'][0],staff_y=q['wrist_r'][1]-P['grip_r'][1],staff_r=q['staff_rotation'],
       left_x=q['wrist_l'][0]-P['grip_l'][0],left_y=q['wrist_l'][1]-P['grip_l'][1],limbs=min(1,t/.12),legs=min(1,t/.18),
       foot_lx=q['left_step_x'],foot_ly=q['left_step_y'],bendr=1 if q['fold_r']>=0 else -1,
       rearstaff=1 if q['staff_behind_head'] else 0,cape_l=q['cape'],cape_r=-q['cape']*.45,hat=q['hat'],hair=q['hair'])
CHANT=entry(1.2)
RELEASE=dict(CHANT,body_x=CHANT['body_x']+4,body_y=CHANT['body_y']-1.5,body_r=-11,head_r=6,
             staff_x=CHANT['staff_x']+7,staff_y=CHANT['staff_y']+1,staff_r=CHANT['staff_r']-6,hat=1.5,hair=2)
TIRED=dict(CHANT,body_x=6,body_y=-11,body_r=-16,chest_r=-2,head_r=10,staff_x=127,staff_y=2,staff_r=-87,left_x=-35,left_y=-6,hat=-1)
BRACE=pose(body_x=8,body_y=-49,body_r=-48,pelvis_r=-15,head_r=43,turn=1,headturn=.65,prone=.35,
           staff_x=148,staff_y=-79,staff_r=-105,left_x=45.55,left_y=-66.78,palm=1,limbs=1,legs=1,bendr=1,
           foot_rx=-12,foot_lx=-18,foot_ry=-5,foot_ly=-5,foot_rr=-35,foot_lr=-30)
DOWN=pose(body_x=8,body_y=-56,body_r=-88,pelvis_r=-85,head_r=82,turn=1,prone=1,
          staff_x=171,staff_y=-95,staff_r=-107.745,left_x=45.55,left_y=-66.78,palm=1,limbs=1,legs=1,bendr=1,
          foot_rx=-9,foot_lx=-31,foot_ry=-15,foot_ly=-15,foot_rr=-88,foot_lr=-88,hat=-1,hair=-1)
PUSH=dict(DOWN,body_y=-52,body_r=-73,pelvis_r=-60,head_r=67,prone=.85,
          left_x=45.55,foot_rx=-10,foot_lx=-25,foot_ry=-8,foot_ly=-8,foot_rr=-48,foot_lr=-42)
# Preserve the raw generated pixels; UV meshes turn the separate art islands
# into ordinary Spine attachments. Torso points are authored in the final pose.
def rotate2(v,a):
    r=math.radians(a);return(v[0]*math.cos(r)-v[1]*math.sin(r),v[0]*math.sin(r)+v[1]*math.cos(r))
end_p=(P['pelvis'][0]+DOWN['body_x'],P['pelvis'][1]+DOWN['body_y'])
end_h=tuple(end_p[i]+rotate2((P['head'][0]-P['pelvis'][0],P['head'][1]-P['pelvis'][1]),DOWN['body_r'])[i] for i in [0,1])
prone_map=axis_map((975,548),(1427,425),end_p,end_h,.145)
def torso_prone_point(x,y):
    w=prone_map(x,y);local=rotate2((w[0]-end_p[0],w[1]-end_p[1]),-DOWN['body_r'])
    return(P['pelvis'][0]+local[0],P['pelvis'][1]+local[1])
make_mesh('prone_body','prone_body','prone',box(775,305,1535,632),lambda x,y:{'torso':1},torso_prone_point,True,28)
make_mesh('prone_head','prone_head','prone',box(2,5,832,680),lambda x,y:{'head':1},hand_map((510,590),P['head'],.30),True,28)
for side,sy in [('r',722),('l',878)]:
    map_leg=axis_map((1328,sy),(1053,sy),P['hip_'+side],P['ankle_'+side],.098)
    def weights(x,y,s=side):
        if x<1095:return {'foot_'+s:1}
        k=smooth((1300-x)/160);return {'thigh_'+s:1-k,'shin_'+s:k}
    make_mesh('prone_leg_'+side,'prone_leg_'+side,'prone',box(821,sy-65,1385,sy+75),weights,map_leg,True,24)
for s in slots:
    if s['name'].startswith('prone_'):s['color']='ffffff00'
# Head/cape and limbs have stable identities. The far right shoulder passes
# behind the original chest; the left hand never becomes the staff owner.
names=[s['name'] for s in slots]
for name,before in [('prone_leg_r','body'),('prone_leg_l','body'),('prone_body','head_repair'),('prone_head','eye')]:
    item=next(s for s in slots if s['name']==name);slots.remove(item);slots.insert(next(i for i,s in enumerate(slots) if s['name']==before),item)
focus=[{'time':0,'name':'face_focus'}];closed=[{'time':0,'name':'eye_tired'}];shout=[{'time':0,'name':'face_release'}]
sampled('chant_enter',1.2,entry,blink=[{'time':0,'name':None},{'time':.15,'name':'face_focus'}])
sampled('chant_loop',2,lambda t:dict(CHANT,body_y=CHANT['body_y']+.18*math.sin(t*math.pi)**2,cape_l=.25*math.sin(t*math.pi)**2),blink=focus)
sampled('chant_cancel',1.2,lambda t:entry(1.2-t),blink=[{'time':0,'name':'face_focus'},{'time':1.06,'name':None}])
sampled('chant_ack',.5,lambda t:dict(CHANT,head_r=CHANT['head_r']-2*math.sin(t/.5*math.pi)**2),blink=focus)
wind=dict(CHANT,staff_x=CHANT['staff_x']-3,body_r=-5,hat=-1)
sampled('explosion_release',.68,lambda t:through([(0,CHANT),(.28,wind),(.46,RELEASE),(.68,RELEASE)],t),blink=[{'time':0,'name':'face_focus'},{'time':.34,'name':'face_release'}],events=[{'time':.46,'name':'release','string':'explosion'}])
sampled('explosion_hold',.6,lambda t:dict(RELEASE,cape_l=RELEASE['cape_l']+.25*math.sin(t/.6*math.pi)**2),blink=shout)
sampled('explosion_exit',.65,lambda t:through([(0,RELEASE),(.65,TIRED)],t),blink=[{'time':0,'name':'face_release'},{'time':.18,'name':'eye_tired'}])
recoil=dict(CHANT,body_x=CHANT['body_x']-2,body_r=CHANT['body_r']+4,head_r=8,hat=-2)
sampled('hit_chant',.44,lambda t:through([(0,CHANT),(.10,recoil),(.44,CHANT)],t),blink=[{'time':0,'name':'face_focus'},{'time':.035,'name':'face_hit'},{'time':.31,'name':'face_focus'}])
sampled('relaxed_fall',1.3,lambda t:through([(0,TIRED),(.48,BRACE),(.75,dict(BRACE,head_r=39)),(1.16,DOWN),(1.3,DOWN)],t),blink=closed)
sampled('relaxed_loop',3,lambda t:dict(DOWN,chest_r=.10*math.sin(t/3*math.pi)**2),blink=closed)
KNEEL=pose(body_x=6,body_y=-32,body_r=-22,head_r=18,turn=.5,prone=0,staff_x=126,staff_y=-26,staff_r=-65,
            left_x=5,left_y=-20,limbs=1,legs=1,bendr=1,foot_rx=-8,foot_lx=-12,foot_rr=-15,foot_lr=-15)
UPRIGHT=dict(CHANT,body_x=3,body_y=-13,body_r=-9,turn=.7,left_x=-15,left_y=-5,foot_lx=3)
def stand_from_prone(t):
    if t<=1.9:return through([(0,DOWN),(.38,PUSH),(.78,BRACE),(1.03,dict(BRACE,palm=0,left_y=-35)),(1.42,KNEEL),(1.9,CHANT)],t)
    return entry(3.1-t)
sampled('get_up',3.1,stand_from_prone,blink=[{'time':0,'name':'eye_tired'},{'time':1.1,'name':'face_focus'},{'time':2.99,'name':None}])
sampled('hit_down',.3,lambda t:dict(DOWN,head_r=DOWN['head_r']+1.2*math.sin(t/.3*math.pi)**2),blink=closed)
DEAD=dict(DOWN,head_r=DOWN['head_r']-3,body_x=DOWN['body_x']+1)
def collapse(t):
    if t<=.65:return entry(t/.65*.52)
    if t<=1.05:return through([(.65,entry(.52)),(1.05,BRACE)],t)
    return through([(1.05,BRACE),(1.68,DEAD),(1.8,DEAD)],t)
sampled('dead',1.8,collapse,blink=[{'time':0,'name':None},{'time':.05,'name':'face_hit'},{'time':.32,'name':'eye_tired'}])
sampled('dead_from_down',.45,lambda t:through([(0,DOWN),(.45,DEAD)],t),blink=closed)
# The short attack follows the same owner/turning route, played more quickly.
def short_attack(t):
    if t<=.62:return entry(t/.62*1.2)
    if t<=.76:return dict(CHANT)
    return entry((1.38-t)/.62*1.2)
sampled('attack_short',1.38,short_attack,blink=[{'time':0,'name':None},{'time':.1,'name':'face_focus'},{'time':1.29,'name':None}],events=[{'time':.68,'name':'impact','string':'ordinary'}])
(OUT/'authoring-poses.json').write_text(json.dumps(pose_samples,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
