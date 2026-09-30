from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
props=['hip_x','hip_drop','pelvis_roll','torso_lean','head_tilt','R_shoulder','R_elbow','R_wrist','L_shoulder','L_elbow','L_wrist','cape_strength']
base={p:0 for p in props};base['cape_strength']=.35
keys=[(0.,{}),(.45,{}),
(.95,{'hip_x':-6,'hip_drop':20,'torso_lean':-3,'head_tilt':-1,'R_shoulder':8,'R_elbow':-5,'R_wrist':-5,'L_shoulder':-12,'L_elbow':-12,'L_wrist':-6,'cape_strength':.5}),
(1.95,{'hip_x':-8,'hip_drop':14,'torso_lean':-3,'head_tilt':-2,'R_shoulder':35,'R_elbow':12,'R_wrist':-40,'L_shoulder':-58,'L_elbow':-62,'L_wrist':-10,'cape_strength':.8}),
(2.65,{'hip_x':-5,'hip_drop':10,'torso_lean':-3,'head_tilt':-3,'R_shoulder':40,'R_elbow':15,'R_wrist':-42,'L_shoulder':-75,'L_elbow':-80,'L_wrist':0,'cape_strength':1.1}),
(3.1,{'hip_x':-5,'hip_drop':12,'torso_lean':-3,'head_tilt':-3,'R_shoulder':40,'R_elbow':15,'R_wrist':-42,'L_shoulder':-75,'L_elbow':-80,'L_wrist':0,'cape_strength':1.3}),
(3.5,{'hip_x':14,'hip_drop':30,'pelvis_roll':1,'torso_lean':7,'head_tilt':-1,'R_shoulder':40,'R_elbow':15,'R_wrist':-33,'L_shoulder':-70,'L_elbow':-10,'L_wrist':-18,'cape_strength':1.8}),
(3.8,{'hip_x':3,'hip_drop':35,'pelvis_roll':-1,'torso_lean':-7,'head_tilt':-4,'R_shoulder':36,'R_elbow':12,'R_wrist':-30,'L_shoulder':-56,'L_elbow':-15,'L_wrist':-18,'cape_strength':1.6}),
(4.6,{'hip_x':-20,'hip_drop':75,'pelvis_roll':-2,'torso_lean':7,'head_tilt':11,'R_shoulder':14,'R_elbow':-5,'R_wrist':-6,'L_shoulder':-12,'L_elbow':-22,'L_wrist':0,'cape_strength':.8}),
(5.55,{'hip_x':-18,'hip_drop':76,'pelvis_roll':-2,'torso_lean':8,'head_tilt':11,'R_shoulder':13,'R_elbow':-5,'R_wrist':-6,'L_shoulder':-10,'L_elbow':-20,'L_wrist':0,'cape_strength':.45}),
(6.65,{}),(7.2,{})]
# Leg-motion correction: stable caster stance and a shallow, same-direction knee yield.
# Shoulder/torso/head carry exhaustion instead of pressing the hips into a wide squat.
hip_map={20:.75,14:.6,10:.4,12:.6,30:1.,35:1.25,75:1.5,76:1.5}
for t,v in keys:
 if 'hip_drop' in v:v['hip_drop']=hip_map.get(v['hip_drop'],v['hip_drop'])
 if 'hip_x' in v:v['hip_x']*=.05
 if 'pelvis_roll' in v:v['pelvis_roll']=0.
 if t in [4.6,5.55]:v['torso_lean']=12;v['head_tilt']=17
dense=[]
for i in range(433):
 t=i/60
 for j in range(len(keys)-1):
  if t<=keys[j+1][0]+1e-8:break
 t0,a=keys[j];t1,b=keys[j+1];u=max(0,min(1,(t-t0)/(t1-t0)));s=u*u*u*(u*(u*6-15)+10)
 dense.append((t,{p:a.get(p,base[p])+(b.get(p,base[p])-a.get(p,base[p]))*s for p in props}))
text='[gd_resource type="Animation" format=3]\n\n[resource]\nresource_name = "MageCast"\nlength = 7.2\n'
for i,p in enumerate(props):
 text+=f'tracks/{i}/type = "value"\ntracks/{i}/path = NodePath(".:{p}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = false\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array({", ".join(f"{t:.7f}" for t,v in dense)}),\n"transitions": PackedFloat32Array({", ".join("1" for _ in dense)}),\n"update": 0,\n"values": [{", ".join(f"{v[p]:.7f}" for t,v in dense)}]\n}}\n'
(R/'animations/MageCast.tres').write_text(text);(R/'animations/art_directed_keys.json').write_text(json.dumps({'duration':7.2,'keys':keys,'properties':props,'note':'Staff stays upright. Free palm projects right on release; no horizontal staff sweep or melee swing.'},indent=2))
