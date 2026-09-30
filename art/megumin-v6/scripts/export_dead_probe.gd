extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;root.add_child(rig);await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 rig.seek_pose(0.);rig.player.stop()
 var probes=[
  {"name":"kneeling_ground_contact","hip_x":311.00135321,"hip_drop":471.20049697,"torso_lean":22.,"head_tilt":35.,"R_shoulder":-8.,"R_elbow":-10.,"R_wrist":0.,"L_shoulder":-5.,"L_elbow":-20.,"L_wrist":-10.,"R_heel_raise":60.,"L_heel_raise":65.,"cape_collapse":1.,"staff_ground_contact":1.,"face_state":1},
  {"name":"folded_upper_body","hip_x":3.,"hip_drop":12.,"torso_lean":42.,"head_tilt":50.,"R_shoulder":-12.,"R_elbow":-10.,"R_wrist":0.,"L_shoulder":-5.,"L_elbow":-20.,"L_wrist":-10.,"R_heel_raise":0.,"L_heel_raise":0.,"cape_collapse":0.,"staff_ground_contact":1.,"face_state":1},
  {"name":"supported_loss_of_support","hip_x":8.,"hip_drop":5.,"torso_lean":32.,"head_tilt":50.,"R_shoulder":-50.,"R_elbow":-50.,"R_wrist":0.,"L_shoulder":-32.,"L_elbow":0.,"L_wrist":0.,"R_heel_raise":2.,"L_heel_raise":3.,"cape_collapse":0.,"staff_ground_contact":1.,"face_state":1}]
 var geometry={};var frames=[];var metrics=[]
 DirAccess.make_dir_recursive_absolute("res://preview/dead_probe")
 for fi in range(probes.size()):
  for prop in probes[fi]:
   if prop!="name":rig.set(prop,probes[fi][prop])
  rig.cape_strength=0.;rig.elapsed=0.;rig.update_pose()
  var nodes:Array[Polygon2D]=[]
  for p in rig.pieces:
   if p.node.visible:nodes.append(p.node)
  nodes.sort_custom(func(a,b):return a.z_index<b.z_index)
  var frame={"time":0.,"state":probes[fi].name,"parts":[]};var binary=FileAccess.open("res://preview/dead_probe/frame_%04d.bin"%fi,FileAccess.WRITE)
  for n in nodes:
   var key=String(n.name)
   if not geometry.has(key):
    var uv=[];var tris=[]
    for v in n.uv:uv.append([v.x,v.y])
    if n.polygons.is_empty():
     var ids=Geometry2D.triangulate_polygon(n.polygon)
     for i in range(0,ids.size(),3):tris.append([ids[i],ids[i+1],ids[i+2]])
    else:
     for t in n.polygons:tris.append([t[0],t[1],t[2]])
    geometry[key]={"texture":n.texture.resource_path,"uv":uv,"triangles":tris,"mask":{}}
   frame.parts.append({"key":key,"count":n.polygon.size()})
   for v in n.polygon:
    var q:Vector2=n.global_transform*v;binary.store_float(q.x);binary.store_float(q.y)
  binary.close();frames.append(frame);metrics.append(rig.metrics())
 var f=FileAccess.open("res://preview/dead_probe/native_geometry.json",FileAccess.WRITE);f.store_string(JSON.stringify({"engine":Engine.get_version_info().string,"fps":30,"geometry":geometry,"frames":frames}));f.close()
 f=FileAccess.open("res://preview/dead_probe/metrics.json",FileAccess.WRITE);f.store_string(JSON.stringify(metrics));f.close();print("DEAD_POSE_PROBES ready; visual decision required");quit()
