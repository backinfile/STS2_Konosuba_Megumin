@tool
class_name MeguminContinuousRig
extends Node2D
## One source anatomy, fixed-length FK arms and planted two-segment leg IK.
## All bone scales stay Vector2.ONE. Only narrow knee blend bands and cloth deform.
const ORIGIN = Vector2(575,1508)
const HIP = Vector2(619,701)
const PELVIS = Vector2(614,852)
const REST = {
 "pelvis":Vector2(614,852),"torso":Vector2(619,701),"head":Vector2(583,485),
 "left_cuff":Vector2(415,631),"left_upper":Vector2(484,539),"left_forearm":Vector2(415,631),"left_hand":Vector2(495,607),
 "right_upper":Vector2(674,545),"right_forearm":Vector2(740,631),"right_hand":Vector2(829,609),
 "knee_left":Vector2(463,1053),"knee_right":Vector2(720,1059),"thigh_left":Vector2(548,848),"shin_left":Vector2(463,1053),"boot_left":Vector2(348,1243),
 "thigh_right":Vector2(681,857),"shin_right":Vector2(720,1059),"boot_right":Vector2(779,1241)}
const BOOT_SHIFT = {"left":Vector2(65,0),"right":Vector2(-35,0)}
@export var hip_x := 0.0
@export var hip_drop := -16.6879351
@export var pelvis_tilt := 8.53055893
@export var torso_lean := -8.53055893
@export var head_tilt := 0.0
@export var left_shoulder := 0.0
@export var left_elbow := 0.0
@export var left_wrist := 0.0
@export var right_shoulder := 0.0
@export var right_elbow := 0.0
@export var right_wrist := 0.0
@export var cape_strength := 0.5
@export var autoplay := true
var bones: Dictionary = {}
var pieces: Array[Dictionary] = []
var player: AnimationPlayer
var elapsed := 0.0
var ik_metrics: Dictionary = {}

func _ready() -> void:
 bones.clear();pieces.clear()
 if get_node_or_null("Anatomy") != null:get_node("Anatomy").free()
 var anatomy = Node2D.new();anatomy.name="Anatomy";add_child(anatomy)
 _bone("pelvis",anatomy,REST.pelvis-ORIGIN)
 _bone("torso",bones.pelvis,HIP-PELVIS)
 _bone("head",bones.torso,REST.head-REST.torso)
 for side in ["left","right"]:
  _bone(side+"_upper",bones.torso,REST[side+"_upper"]-HIP)
  _bone(side+"_forearm",bones[side+"_upper"],REST[side+"_forearm"]-REST[side+"_upper"])
  _bone(side+"_hand",bones[side+"_forearm"],REST[side+"_hand"]-REST[side+"_forearm"])
  for part in ["thigh_","shin_","boot_","knee_"]:_bone(part+side,anatomy,REST[part+side]-ORIGIN)
  _bone("leg_"+side,anatomy,Vector2.ZERO)
 _bone("left_cuff",bones.left_upper,REST.left_cuff-REST.left_upper)
 _bone("cape",anatomy,Vector2.ZERO)
 var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/rig_geometry.json"))
 var textures={"master":load("res://assets/source/megumin_master.png"),"base":load("res://assets/source/megumin_occlusion_base.png"),"staff":load("res://assets/source/megumin_staff_complete.png"),"body_v3":load("res://assets/source/megumin_body_occlusion_v3.png"),"cape_v3":load("res://assets/source/megumin_cape_complete_v3.png")}
 for data in geometry.parts:
  var node=Polygon2D.new();node.name=data.name;node.texture=textures[data.texture]
  node.z_as_relative=false;node.z_index=int(data.z);node.antialiased=true
  var vertices=PackedVector2Array();var uv=PackedVector2Array()
  for p in data.vertices:vertices.append(Vector2(p[0],p[1]))
  for p in data.uv:uv.append(Vector2(p[0],p[1]))
  var local=PackedVector2Array()
  for v in vertices:local.append(v-REST.get(data.bone,ORIGIN))
  node.polygon=local;node.uv=uv
  if not data.triangles.is_empty():
   var tris:Array[PackedInt32Array]=[]
   for tri in data.triangles:tris.append(PackedInt32Array(tri))
   node.polygons=tris
  bones[data.bone].add_child(node)
  pieces.append({"node":node,"rest":vertices,"local":local,"bone":data.bone,"skin_weights":data.get("skin_weights",[]),"hip_weights":data.get("hip_weights",[])})
 player=get_node("AnimationPlayer")
 update_pose()
 if autoplay and not Engine.is_editor_hint():player.play("ContinuousCast")

func _bone(id:String,parent:Node2D,point:Vector2) -> void:
 var n=Node2D.new();n.name=id;parent.add_child(n);n.position=point;bones[id]=n

func seek_pose(time:float) -> void:
 player.play("ContinuousCast");player.seek(clampf(time,0.,5.4),true)
 elapsed=time;update_pose()

func _process(delta:float) -> void:
 if bones.is_empty():return
 elapsed+=delta
 update_pose()

func update_pose() -> void:
 bones.pelvis.position=PELVIS-ORIGIN+Vector2(hip_x,hip_drop)
 bones.pelvis.rotation=deg_to_rad(pelvis_tilt)
 bones.torso.rotation=deg_to_rad(torso_lean)
 # Head direction is authored in world orientation, compensating waist/shoulder lean.
 bones.head.rotation=deg_to_rad(head_tilt-pelvis_tilt-torso_lean)
 for side in ["left","right"]:
  bones[side+"_upper"].rotation=deg_to_rad(get(side+"_shoulder"))
  bones[side+"_forearm"].rotation=deg_to_rad(get(side+"_elbow"))
  bones[side+"_hand"].rotation=deg_to_rad(get(side+"_wrist"))
  _solve_leg(side)
 bones.left_cuff.rotation=deg_to_rad(-.65*(pelvis_tilt+torso_lean+left_shoulder))
 for piece in pieces:
  if piece.bone.begins_with("leg_"):
   _skin_leg(piece)
   continue
  if piece.bone!="cape":continue
  var posed=PackedVector2Array()
  for v in piece.rest:
   var follow=1.-smoothstep(520.,1130.,v.y)
   var rigid=bones.pelvis.transform*bones.torso.transform*(v-HIP)+ORIGIN
   var q=v.lerp(rigid,follow)
   var pin=clampf((v.y-520.)/550.,0.,1.)
   q+=Vector2(sin(elapsed*2.3+v.y*.006)*9.,sin(elapsed*2.1-v.x*.009)*10.)*pin*cape_strength
   posed.append(q-ORIGIN)
  piece.node.polygon=posed

func _skin_leg(piece:Dictionary) -> void:
 var side:String=piece.bone.trim_prefix("leg_")
 var k0:Vector2=REST["shin_"+side];var k:Vector2=ik_metrics[side].knee
 var upper_angle:float=bones["thigh_"+side].rotation
 var lower_angle:float=bones["shin_"+side].rotation
 var posed=PackedVector2Array()
 for i in range(piece.rest.size()):
  var v:Vector2=piece.rest[i]
  # Rotation blending about one exact knee center keeps joint radii; no LBS squash.
  var angle=lerp_angle(upper_angle,lower_angle,piece.skin_weights[i])
  var q=k+(v-k0).rotated(angle)
  if piece.hip_weights[i]<1.:
   var h:Vector2=ik_metrics[side].hip;var h0:Vector2=REST["thigh_"+side]
   var hip_angle=lerp_angle(bones.pelvis.rotation,upper_angle,piece.hip_weights[i])
   q=h+(v-h0).rotated(hip_angle)
  posed.append(q)
 piece.node.polygon=posed

func _solve_leg(side:String) -> void:
 var h0:Vector2=REST["thigh_"+side];var k0:Vector2=REST["shin_"+side];var a0:Vector2=REST["boot_"+side]
 var h:Vector2=bones.pelvis.transform*(h0-PELVIS)
 var a:Vector2=a0-ORIGIN+BOOT_SHIFT[side]
 var upper=h0.distance_to(k0);var lower=k0.distance_to(a0)
 var d=h.distance_to(a);var safe=clampf(d,absf(upper-lower)+.001,upper+lower-.001)
 var direction=(a-h).normalized();var along=(upper*upper-lower*lower+safe*safe)/(2.*safe)
 var height=sqrt(maxf(0.,upper*upper-along*along))
 var branch=-1.
 var k=h+direction*along+Vector2(-direction.y,direction.x)*height*branch
 bones["thigh_"+side].position=h;bones["thigh_"+side].rotation=(k-h).angle()-(k0-h0).angle()
 bones["shin_"+side].position=k;bones["shin_"+side].rotation=(a-k).angle()-(a0-k0).angle()
 bones["knee_"+side].position=k;bones["knee_"+side].rotation=(bones["thigh_"+side].rotation+bones["shin_"+side].rotation)*.5
 bones["boot_"+side].position=a;bones["boot_"+side].rotation=0.
 ik_metrics[side]={"hip":h,"knee":k,"ankle":a,"upper":upper,"lower":lower,"reach_error":absf(safe-d)}

func anatomy_metrics() -> Dictionary:
 var out:Dictionary={"time":elapsed,"ik":{},"bones":{},"hand_staff_grip_error":0.0}
 for side in ["left","right"]:
  var m:Dictionary=ik_metrics[side]
  out.ik[side]={"upper_length":m.hip.distance_to(m.knee),"lower_length":m.knee.distance_to(m.ankle),"reach_error":m.reach_error,"ankle":[m.ankle.x,m.ankle.y],"knee":[m.knee.x,m.knee.y]}
 for id in bones:
  var n:Node2D=bones[id];var p:Vector2=n.global_position
  out.bones[id]={"position":[p.x,p.y],"rotation":n.global_rotation,"scale":[n.global_scale.x,n.global_scale.y]}
 return out
