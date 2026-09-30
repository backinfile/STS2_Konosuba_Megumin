"""Build editable native AnimationPlayer resources for the v2 authored-pose rig.
No pixels are painted, cleaned, synthesized or resized by this script.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
legacy_props=['breath','body_lean','head_tilt','left_upper','left_forearm','right_upper','right_forearm','grip_tilt','cape_strength','cast_power','blast_power','hit_flash','collapse','relaxed_amount','dead_amount']
pose_props=['pose_index','hip_shift','knee_load','torso_pitch','head_pitch','staff_upper','staff_forearm','staff_wrist','free_arm_angle','cape_lag']
base={p:0.0 for p in legacy_props+pose_props};base['cape_strength']=1.;base['pose_index']=-1
# Angles are deliberately small. Real bent knees and shoulder/hip turns exist in
# the new drawings. Grid animation supplies anticipation, overlap and recovery.
prep={'pose_index':0,'hip_shift':-12,'knee_load':8,'torso_pitch':-1.5,'head_pitch':2,'staff_upper':-2,'staff_forearm':3,'free_arm_angle':2,'cape_lag':-.2}
chant={'pose_index':1,'hip_shift':-7,'knee_load':-4,'torso_pitch':-1.5,'head_pitch':-2,'staff_upper':-1.2,'staff_forearm':1.5,'cast_power':1.,'cape_strength':1.35}
release={'pose_index':2,'hip_shift':10,'knee_load':7,'torso_pitch':2,'head_pitch':-1,'staff_upper':-1.4,'staff_forearm':2.0,'free_arm_angle':-3,'cape_lag':1.,'cape_strength':1.8}
exhausted={'pose_index':3,'hip_shift':2,'knee_load':10,'torso_pitch':1.3,'head_pitch':3,'staff_upper':2,'staff_forearm':1,'staff_wrist':30,'free_arm_angle':2,'cape_strength':.6}
def mix(p,**v): return p|v
states={
'Cast':(1.55,False,[
(0.,mix(prep,hip_shift=0,knee_load=0,torso_pitch=0,staff_upper=0,staff_forearm=0)),
(.16,mix(prep,knee_load=12,hip_shift=-15)),
(.34,mix(prep,knee_load=8,hip_shift=-8,staff_upper=-4,staff_forearm=4,head_pitch=-1)),
(.35,mix(chant,torso_pitch=1.4,staff_upper=3,staff_forearm=-2,head_pitch=1,knee_load=7)),
(.62,mix(chant,torso_pitch=-.5,staff_upper=.4,staff_forearm=.3,head_pitch=-1,knee_load=-2)),
(1.15,chant),
(1.35,mix(chant,staff_upper=-1.5,staff_forearm=1.2,head_pitch=-2.1)),
(1.55,mix(chant,staff_upper=-1.5,staff_forearm=1.2,head_pitch=-2.1))]),
'Attack':(3.50,False,[
(0.,mix(prep,hip_shift=0,knee_load=0,torso_pitch=0,staff_upper=0,staff_forearm=0)),
(.16,mix(prep,knee_load=12,hip_shift=-15)),
(.34,mix(prep,knee_load=8,hip_shift=-8,staff_upper=-4,staff_forearm=4,head_pitch=-1)),
(.35,mix(chant,torso_pitch=1.4,staff_upper=3,staff_forearm=-2,head_pitch=1,knee_load=7)),
(.62,mix(chant,torso_pitch=-.5,staff_upper=.4,staff_forearm=.3,head_pitch=-1,knee_load=-2)),
(1.15,chant),
(1.35,mix(chant,staff_upper=-1.5,staff_forearm=1.2,head_pitch=-2.1)),
(1.39,mix(chant,hip_shift=1,knee_load=4,torso_pitch=2.5,staff_upper=4,staff_forearm=-3,head_pitch=0,cape_lag=-.2)),
(1.40,mix(release,hip_shift=-8,knee_load=2,torso_pitch=-2.2,staff_upper=2.5,staff_forearm=-2,head_pitch=0,cape_lag=-.45,cast_power=.4)),
(1.55,mix(release,hip_shift=14,knee_load=10,torso_pitch=2.8,staff_upper=-1.8,staff_forearm=2.4,blast_power=1)),
(1.68,mix(release,hip_shift=10,knee_load=7,torso_pitch=2,blast_power=.3)),
(1.94,mix(release,hip_shift=9,knee_load=7,torso_pitch=1.8,cape_lag=.6)),
(2.18,mix(release,hip_shift=7,knee_load=12,torso_pitch=3.2,head_pitch=3.4,staff_upper=3.8,staff_forearm=3.5,free_arm_angle=3.5,cape_lag=.1)),
(2.20,mix(exhausted,knee_load=0,torso_pitch=-1.5,head_pitch=-2,staff_upper=-1.5,staff_forearm=-1,free_arm_angle=-2)),
(2.53,mix(exhausted,knee_load=13,torso_pitch=1.8,head_pitch=4,staff_upper=2.5,staff_forearm=1.2)),
(2.92,exhausted),
(3.50,mix(exhausted,knee_load=9,head_pitch=2.4))]),
'Relaxed':(4.8,False,[
(0.,mix(exhausted,knee_load=1,torso_pitch=-1.5,head_pitch=-2,staff_upper=-1.5)),
(.4,mix(exhausted,knee_load=13,torso_pitch=1.8,head_pitch=4)),
(1.5,exhausted),(2.5,mix(exhausted,knee_load=8,head_pitch=2.3)),
(3.5,mix(exhausted,knee_load=11,head_pitch=3.2)),(4.8,exhausted)])}
# Two additional authored in-betweens keep large silhouettes from jumping directly.
raised={'pose_index':4,'hip_shift':-3,'knee_load':3,'torso_pitch':-1,'head_pitch':-1,'staff_upper':-3,'staff_forearm':2,'free_arm_angle':-1,'cape_lag':-.25,'cast_power':.45}
recover={'pose_index':5,'hip_shift':4,'knee_load':9,'torso_pitch':1.0,'head_pitch':1.5,'staff_upper':2,'staff_forearm':1,'free_arm_angle':3,'cape_lag':.3,'cape_strength':.85}
for state in ['Cast','Attack']:
 length,loop,keys=states[state]
 keys=[(t,v) for t,v in keys if t<=.16 or t>=1.15]
 keys += [(.23,mix(prep,hip_shift=-8,knee_load=10,staff_upper=-12,staff_forearm=9,head_pitch=-1)),
          (.24,mix(raised,staff_upper=10,staff_forearm=-5,torso_pitch=1.5,head_pitch=1)),
          (.40,raised),
          (.59,mix(raised,staff_upper=-10,staff_forearm=-1,torso_pitch=-2,head_pitch=-2)),
          (.60,mix(chant,staff_upper=7,staff_forearm=-4,torso_pitch=1.5,head_pitch=1,knee_load=6)),
          (.93,chant)]
 if state=='Attack':
  keys=[(t,v) for t,v in keys if t<2.18 or t>=2.92]
  keys += [(2.04,mix(release,hip_shift=7,knee_load=11,torso_pitch=2.5,head_pitch=2,staff_upper=4,staff_forearm=3,free_arm_angle=2,cape_lag=.1)),
           (2.05,mix(recover,hip_shift=8,knee_load=4,torso_pitch=-2,head_pitch=-1,staff_upper=-4,staff_forearm=-2,free_arm_angle=-3)),
           (2.25,mix(recover,knee_load=12,torso_pitch=2,head_pitch=3,staff_upper=5,staff_forearm=3,free_arm_angle=6)),
           (2.42,mix(recover,knee_load=14,torso_pitch=3,head_pitch=4,staff_upper=7,staff_forearm=4,free_arm_angle=8)),
           (2.43,mix(exhausted,knee_load=4,torso_pitch=-1,head_pitch=-1,staff_upper=-2,staff_forearm=-1,free_arm_angle=-1)),
           (2.73,mix(exhausted,knee_load=13,torso_pitch=1.8,head_pitch=4,staff_upper=2.5,staff_forearm=1.2))]
 states[state]=(length,loop,sorted(keys))
for name,(length,loop,keys) in states.items():
 txt=f'[gd_resource type="Animation" format=3]\n\n[resource]\nresource_name = "{name}"\nlength = {length}\n'
 if loop:txt+='loop_mode = 1\n'
 for i,p in enumerate(legacy_props+pose_props):
  vals=[v.get(p,base[p]) for _,v in keys]
  txt+=f'tracks/{i}/type = "value"\ntracks/{i}/path = NodePath(".:{p}")\ntracks/{i}/interp = {0 if p=="pose_index" else 1}\ntracks/{i}/loop_wrap = true\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array({", ".join(str(t) for t,_ in keys)}),\n"transitions": PackedFloat32Array({", ".join("1" for _ in keys)}),\n"update": {1 if p=="pose_index" else 0},\n"values": [{", ".join(str(int(x)) if p=="pose_index" else str(float(x)) for x in vals)}]\n}}\n'
 if name=='Attack':
  i=len(legacy_props+pose_props)
  txt+=f'tracks/{i}/type = "method"\ntracks/{i}/path = NodePath(".")\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array(1.55),\n"transitions": PackedFloat32Array(1),\n"values": [{{"method": &"_emit_attack_impact", "args": []}}]\n}}\n'
 (ROOT/'animations'/f'{name}.tres').write_text(txt)
# The legacy Idle, Hit and Dead retain their original drawing/behavior and reset
# every new channel, so interruptions cannot leak an old pose into another state.
for name in ['Idle','Hit','Dead']:
 p=ROOT/'animations'/f'{name}.tres';txt=p.read_text();i=15
 # idempotent regeneration of only added tracks
 if '\ntracks/15/type' in txt:txt=txt[:txt.index('\ntracks/15/type')]+ '\n'
 for prop in pose_props:
  val=-1 if prop=='pose_index' else 0.0
  txt+=f'tracks/{i}/type = "value"\ntracks/{i}/path = NodePath(".:{prop}")\ntracks/{i}/interp = 0\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array(0),\n"transitions": PackedFloat32Array(1),\n"update": 1,\n"values": [{val}]\n}}\n';i+=1
 p.write_text(txt)
print('Built v2 Cast/Attack/Relaxed with explicit four-pose tracks; legacy reset tracks appended.')
