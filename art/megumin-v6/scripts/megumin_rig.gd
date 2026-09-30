@tool
class_name MeguminV6Rig
extends Node2D
## Anatomical right is the staff / white-bandage side (screen-left at rest).
const ORIGIN=Vector2(608,1510)
signal animation_completed(state:StringName)
signal attack_impact
signal state_changed(state:StringName)
const STATES=[&"Idle",&"Cast",&"Attack",&"Hit",&"Relaxed",&"Dead"]
@export var hip_x:=0.0
@export var hip_drop:=0.0
@export var pelvis_roll:=0.0
@export var torso_lean:=0.0
@export var head_tilt:=0.0
@export var R_shoulder:=0.0
@export var R_elbow:=0.0
@export var R_wrist:=0.0
@export var L_shoulder:=0.0
@export var L_elbow:=0.0
@export var L_wrist:=0.0
@export var cape_strength:=0.35
@export var autoplay:=true
@export var cape_collapse:=0.0
@export var R_heel_raise:=0.0
@export var L_heel_raise:=0.0
@export var staff_ground_contact:=0.0
@export var face_state:=0
@export var auto_return_to_idle:=true
var current_state:StringName=&"MageCast"
var dead_locked:=false
var cloth_offset_a:=0.0
var cloth_offset_b:=0.0
var impact_count:=0
var landmarks:Dictionary={}
var bones:Dictionary={}
var pieces:Array[Dictionary]=[]
var ik:Dictionary={}
var player:AnimationPlayer
var elapsed:=0.0
func _ready()->void:
 bones.clear();pieces.clear()
 if get_node_or_null("Anatomy")!=null:get_node("Anatomy").free()
 var art=Node2D.new();art.name="Anatomy";add_child(art)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/rig_geometry.json"))
 for key in data.landmarks:landmarks[key]=Vector2(data.landmarks[key][0],data.landmarks[key][1])
 _bone("pelvis",art,landmarks.pelvis-ORIGIN)
 _bone("torso",bones.pelvis,landmarks.waist-landmarks.pelvis)
 _bone("head",bones.torso,landmarks.neck-landmarks.waist)
 for side in ["R","L"]:
  _bone(side+"_upper",bones.torso,landmarks[side+"_shoulder"]-landmarks.waist)
  _bone(side+"_forearm",bones[side+"_upper"],landmarks[side+"_elbow"]-landmarks[side+"_shoulder"])
  _bone(side+"_hand",bones[side+"_forearm"],landmarks[side+"_wrist"]-landmarks[side+"_elbow"])
  _bone(side+"_thigh",art,landmarks[side+"_hip"]-ORIGIN)
  _bone(side+"_shin",art,landmarks[side+"_knee"]-ORIGIN)
  _bone(side+"_foot",art,landmarks[side+"_ankle"]-ORIGIN)
  _bone(side+"_leg",art,Vector2.ZERO)
 _bone("R_arm_cloth",art,Vector2.ZERO)
 _bone("cape",art,Vector2.ZERO)
 var texture_paths={"master":"res://assets/source/megumin_master_v6.png","backing":"res://assets/source/megumin_backing_v6_raw.png","staff_raw":"res://assets/source/megumin_staff_v6_raw.png","unstaffed":"res://assets/source/megumin_unstaffed_v6_raw.png","free_arm":"res://assets/source/megumin_free_arm_v6_raw.png","cape_raw":"res://assets/source/megumin_cape_v6_raw.png","closed_face":"res://assets/source/megumin_closedeyes_v6_raw.png"}
 for p in data.parts:
  var node=Polygon2D.new();node.name=p.name;node.texture=load(texture_paths[p.texture]);node.z_as_relative=false;node.z_index=p.z;node.antialiased=true
  var rest=PackedVector2Array();var uv=PackedVector2Array()
  for v in p.vertices:rest.append(Vector2(v[0],v[1]))
  for v in p.uv:uv.append(Vector2(v[0],v[1]))
  var pivot=_rest_pivot(p.bone);var local=PackedVector2Array()
  for v in rest:local.append(v-pivot)
  node.polygon=local;node.uv=uv
  if not p.triangles.is_empty():
   var tris:Array[PackedInt32Array]=[]
   for tri in p.triangles:tris.append(PackedInt32Array(tri))
   node.polygons=tris
  bones[p.bone].add_child(node)
  pieces.append({"node":node,"rest":rest,"bone":p.bone,"knee_weights":p.get("knee_weights",[]),"hip_weights":p.get("hip_weights",[]),"ankle_weights":p.get("ankle_weights",[]),"elbow_weights":p.get("elbow_weights",[])})
 player=get_node("AnimationPlayer")
 for state in STATES:
  if FileAccess.file_exists("res://animations/%s.tres"%state) and not player.has_animation(state):player.get_animation_library("").add_animation(state,load("res://animations/%s.tres"%state))
 player.animation_finished.connect(_animation_finished)
 update_pose()
 if autoplay and not Engine.is_editor_hint():player.play("MageCast")
func _rest_pivot(id:String)->Vector2:
 if id=="pelvis":return landmarks.pelvis
 if id=="torso":return landmarks.waist
 if id=="head":return landmarks.neck
 for side in ["R","L"]:
  if id==side+"_upper":return landmarks[side+"_shoulder"]
  if id==side+"_forearm":return landmarks[side+"_elbow"]
  if id==side+"_hand":return landmarks[side+"_wrist"]
  if id==side+"_foot":return landmarks[side+"_ankle"]
 return ORIGIN
func _bone(id:String,parent:Node2D,at:Vector2)->void:
 var n=Node2D.new();n.name=id;n.position=at;parent.add_child(n);bones[id]=n
func seek_pose(t:float)->void:
 current_state=&"MageCast";cloth_offset_a=0.;cloth_offset_b=0.
 player.play("MageCast");player.seek(clampf(t,0.,7.2),true);elapsed=t;update_pose()
func _process(dt:float)->void:
 if bones.is_empty():return
 elapsed+=dt;update_pose()
func update_pose()->void:
 bones.pelvis.position=landmarks.pelvis-ORIGIN+Vector2(hip_x,hip_drop)
 bones.pelvis.rotation=deg_to_rad(pelvis_roll)
 bones.torso.rotation=deg_to_rad(torso_lean)
 bones.head.rotation=deg_to_rad(head_tilt-torso_lean-pelvis_roll)
 for side in ["R","L"]:
  bones[side+"_upper"].rotation=deg_to_rad(get(side+"_shoulder"))
  bones[side+"_forearm"].rotation=deg_to_rad(get(side+"_elbow"))
  bones[side+"_hand"].rotation=deg_to_rad(get(side+"_wrist"))
  _solve_leg(side)
 _ground_staff()
 for p in pieces:
  if p.node.name=="closed_eyes_face":p.node.visible=face_state==1
  if p.bone.ends_with("_leg"):_skin_leg(p)
  elif p.bone=="R_arm_cloth":_arm_cloth(p)
  elif p.bone=="cape":_cape(p)
func _solve_leg(side:String)->void:
 var h0:Vector2=landmarks[side+"_hip"];var k0:Vector2=landmarks[side+"_knee"];var a0:Vector2=landmarks[side+"_ankle"]
 var h:Vector2=bones.pelvis.transform*(h0-landmarks.pelvis)
 var toe=Vector2(465,1510) if side=="R" else Vector2(818,1445)
 var foot_angle=deg_to_rad(get(side+"_heel_raise"))
 var a=toe+(a0-toe).rotated(foot_angle)-ORIGIN
 var u=h0.distance_to(k0);var l=k0.distance_to(a0);var d=h.distance_to(a)
 var reach=clampf(d,absf(u-l)+.001,u+l-.001);var v=(a-h).normalized()
 var along=(u*u-l*l+reach*reach)/(2.*reach);var height=sqrt(maxf(0.,u*u-along*along))
 # Preserve the original mother's knee bend side; never switch IK branch mid-action.
 var cross=(a0-h0).cross(k0-h0);var branch=1. if cross>=0. else -1.
 var k=h+v*along+Vector2(-v.y,v.x)*height*branch
 bones[side+"_thigh"].position=h;bones[side+"_thigh"].rotation=(k-h).angle()-(k0-h0).angle()
 bones[side+"_shin"].position=k;bones[side+"_shin"].rotation=(a-k).angle()-(a0-k0).angle()
 bones[side+"_foot"].position=a;bones[side+"_foot"].rotation=foot_angle
 ik[side]={"hip":h,"knee":k,"ankle":a,"upper":u,"lower":l,"reach_error":absf(d-reach)}
func _skin_leg(p:Dictionary)->void:
 var side:String=p.bone.left(1);var h0:Vector2=landmarks[side+"_hip"];var k0:Vector2=landmarks[side+"_knee"];var a0:Vector2=landmarks[side+"_ankle"]
 var h:Vector2=ik[side].hip;var k:Vector2=ik[side].knee;var a:Vector2=ik[side].ankle
 var u:float=bones[side+"_thigh"].rotation;var l:float=bones[side+"_shin"].rotation;var posed=PackedVector2Array()
 for i in range(p.rest.size()):
  var v:Vector2=p.rest[i];var q=k+(v-k0).rotated(lerp_angle(u,l,p.knee_weights[i]))
  if p.hip_weights[i]<1.:q=h+(v-h0).rotated(lerp_angle(bones.pelvis.rotation,u,p.hip_weights[i]))
  if p.ankle_weights[i]>0.:q=a+(v-a0).rotated(lerp_angle(l,bones[side+"_foot"].rotation,p.ankle_weights[i]))
  posed.append(q)
 p.node.polygon=posed
func _arm_cloth(p:Dictionary)->void:
 var k0:Vector2=landmarks.R_elbow
 var k:Vector2=bones.pelvis.transform*bones.torso.transform*bones.R_upper.transform*(k0-landmarks.R_shoulder)
 var u:float=bones.pelvis.rotation+bones.torso.rotation+bones.R_upper.rotation
 var l:float=u+bones.R_forearm.rotation;var posed=PackedVector2Array()
 for i in range(p.rest.size()):posed.append(k+(p.rest[i]-k0).rotated(lerp_angle(u,l,p.elbow_weights[i])))
 p.node.polygon=posed

func _cape(p:Dictionary)->void:
 var posed=PackedVector2Array()
 for v in p.rest:
  var pin=clampf((v.y-440.)/730.,0.,1.);var follow=1.-smoothstep(440.,1130.,v.y)
  var rigid=bones.pelvis.transform*bones.torso.transform*(v-landmarks.waist)+ORIGIN
  var wa=TAU/3. if current_state==&"Idle" else 2.3
  var wb=TAU*2./3. if current_state==&"Idle" else 2.1
  var q=v.lerp(rigid,follow)+Vector2(sin(elapsed*wa+cloth_offset_a+v.y*.006)*10.,sin(elapsed*wb+cloth_offset_b-v.x*.009)*7.)*pin*cape_strength
  if cape_collapse>0.:
   var settle=smoothstep(560.,1120.,v.y)
   q+=Vector2(hip_x*.45,hip_drop*.82)*settle*cape_collapse
   q.y=minf(q.y,1510.)
  posed.append(q-ORIGIN)
 p.node.polygon=posed
func _ground_staff()->void:
 if staff_ground_contact<=0.:return
 var chain:Transform2D=bones.pelvis.transform*bones.torso.transform*bones.R_upper.transform*bones.R_forearm.transform
 var wrist:Vector2=chain*(landmarks.R_wrist-landmarks.R_elbow)
 var tip=Vector2(650,1460)-landmarks.R_wrist
 var needed=-wrist.y
 if absf(needed)>=tip.length():return
 var parent_angle:float=bones.pelvis.rotation+bones.torso.rotation+bones.R_upper.rotation+bones.R_forearm.rotation
 var desired=asin(needed/tip.length())-tip.angle()
 bones.R_hand.rotation=lerp_angle(bones.R_hand.rotation,desired-parent_angle,clampf(staff_ground_contact,0.,1.))
func play_state(state:StringName)->bool:
 if not STATES.has(state) or not player.has_animation(state) or (dead_locked and state!=&"Dead"):return false
 var old_a=TAU/3. if current_state==&"Idle" else 2.3
 var old_b=TAU*2./3. if current_state==&"Idle" else 2.1
 var new_a=TAU/3. if state==&"Idle" else 2.3
 var new_b=TAU*2./3. if state==&"Idle" else 2.1
 cloth_offset_a+=elapsed*(old_a-new_a);cloth_offset_b+=elapsed*(old_b-new_b)
 current_state=state
 if state==&"Dead":dead_locked=true
 player.play(state,.1);state_changed.emit(state);return true
func seek_state(state:StringName,t:float)->void:
 current_state=state;cloth_offset_a=0.;cloth_offset_b=0.;player.play(state)
 player.seek(clampf(t,0.,player.get_animation(state).length),true);elapsed=t;update_pose()
func reset_character()->void:
 dead_locked=false;face_state=0;staff_ground_contact=0.;R_heel_raise=0.;L_heel_raise=0.;cape_collapse=0.;play_state(&"Idle")
func _animation_finished(state:StringName)->void:
 animation_completed.emit(state)
 if auto_return_to_idle and state!=&"Dead" and state!=&"Idle" and STATES.has(state):play_state(&"Idle")
func _emit_attack_impact()->void:
 impact_count+=1;attack_impact.emit()

func metrics()->Dictionary:
 var m={"time":elapsed,"bones":{},"ik":{}}
 for id in bones:
  var n:Node2D=bones[id];m.bones[id]={"position":[n.global_position.x,n.global_position.y],"rotation":n.global_rotation,"scale":[n.global_scale.x,n.global_scale.y]}
 for side in ["R","L"]:
  var a:Dictionary=ik[side];m.ik[side]={"hip":[a.hip.x,a.hip.y],"knee":[a.knee.x,a.knee.y],"ankle":[a.ankle.x,a.ankle.y],"upper":a.hip.distance_to(a.knee),"lower":a.knee.distance_to(a.ankle),"reach_error":a.reach_error}
 return m
