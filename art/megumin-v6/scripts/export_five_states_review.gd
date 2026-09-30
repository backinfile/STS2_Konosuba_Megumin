extends SceneTree
## Native Godot Polygon2D export only. The review movie is an offline raster,
## never an engine-window recording. This exporter does not edit the rig/assets.
const OUT="res://preview/five_states"
const ORDER=[&"Idle",&"Cast",&"Attack",&"Hit",&"Relaxed"]
const KEY_TIMES={"Idle":[0.,1.35,3.],"Cast":[.65,2.2,2.95,4.8],"Attack":[.95,2.65,3.5,3.8,4.6,7.2],"Hit":[.08,.22,.42,.95],"Relaxed":[.32,.95,1.5,2.55,3.4]}
var rig
var geometry={}
var nodes:Array[Polygon2D]=[]
var segments=[]
var frames=[]
var metrics=[]
var qa_frames=[]
var boundaries=[]
func _initialize()->void:call_deferred("run")
func pose(segment:Dictionary,local_time:float)->void:
 rig.seek_state(segment.state,local_time)
 rig.elapsed=segment.start+local_time
 rig.cloth_offset_a=segment.phase_a-segment.start*segment.frequency_a
 rig.cloth_offset_b=segment.phase_b-segment.start*segment.frequency_b
 rig.update_pose()
func vertices()->Array:
 var result=[]
 for node in nodes:
  if not node.visible:continue
  for v in node.polygon:
   var q:Vector2=node.global_transform*v
   result.append(q)
 return result
func export_frame(segment:Dictionary,local_time:float,file_name:String)->Dictionary:
 pose(segment,local_time)
 var frame={"state":String(segment.state),"state_time":local_time,"state_duration":segment.duration,"time":segment.start+local_time,"file":file_name,"parts":[]}
 var binary=FileAccess.open(OUT+"/"+file_name,FileAccess.WRITE)
 for node in nodes:
  if not node.visible:continue
  var key=String(node.name)
  if not geometry.has(key):
   var uv=[];var tris=[]
   for v in node.uv:uv.append([v.x,v.y])
   if node.polygons.is_empty():
    var indices=Geometry2D.triangulate_polygon(node.polygon)
    for i in range(0,indices.size(),3):tris.append([indices[i],indices[i+1],indices[i+2]])
   else:
    for tri in node.polygons:tris.append([tri[0],tri[1],tri[2]])
   geometry[key]={"texture":node.texture.resource_path,"texture_sha256":FileAccess.get_sha256(node.texture.resource_path),"uv":uv,"triangles":tris,"mask":{}}
  var xf:Transform2D=node.global_transform
  frame.parts.append({"key":key,"count":node.polygon.size(),"z_index":node.z_index,"transform":[xf.x.x,xf.x.y,xf.y.x,xf.y.y,xf.origin.x,xf.origin.y]})
  for v in node.polygon:
   var q:Vector2=xf*v;binary.store_float(q.x);binary.store_float(q.y)
 binary.close()
 var m:Dictionary=rig.metrics()
 m.state=String(segment.state);m.state_time=local_time
 m.parameters={"hip_x":rig.hip_x,"hip_drop":rig.hip_drop,"pelvis_roll":rig.pelvis_roll,"staff_ground_contact":rig.staff_ground_contact,"face_state":rig.face_state,"R_heel_raise":rig.R_heel_raise,"L_heel_raise":rig.L_heel_raise,"cape_collapse":rig.cape_collapse}
 frame["metrics_index"]=metrics.size();metrics.append(m)
 return frame
func write_json(path:String,data)->void:
 var file=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(data));file.close()
func run()->void:
 DirAccess.make_dir_recursive_absolute(OUT)
 rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;rig.auto_return_to_idle=false
 root.add_child(rig);await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var total=0.;var phase_a=0.;var phase_b=0.;var provenance={}
 for state in ORDER:
  if not rig.player.has_animation(state):push_error("Missing animation "+state);quit(1);return
  var duration=roundf(rig.player.get_animation(state).length*60.)/60.
  var wa=TAU/3. if state==&"Idle" else 2.3
  var wb=TAU*2./3. if state==&"Idle" else 2.1
  segments.append({"state":state,"start":total,"duration":duration,"phase_a":phase_a,"phase_b":phase_b,"frequency_a":wa,"frequency_b":wb})
  total+=duration;phase_a+=duration*wa;phase_b+=duration*wb
  provenance["res://animations/%s.tres"%state]=FileAccess.get_sha256("res://animations/%s.tres"%state)
 for file in ["res://scripts/megumin_rig.gd","res://assets/rig_geometry.json"]:provenance[file]=FileAccess.get_sha256(file)
 for p in rig.pieces:nodes.append(p.node)
 nodes.sort_custom(func(a,b):return a.z_index<b.z_index)
 var segment_index=0
 # Exactly 30 fps at original speed. Only the terminal duration is rounded up by
 # at most one video frame; no clip retiming and no duplicate boundary frames.
 for f in range(int(ceil(total*30.))):
  var time=float(f)/30.
  while segment_index<segments.size()-1 and time>=segments[segment_index+1].start-0.0000001:segment_index+=1
  var segment:Dictionary=segments[segment_index]
  frames.append(export_frame(segment,time-segment.start,"frame_%04d.bin"%f))
 for segment in segments:
  var label=String(segment.state)
  var times:Array=KEY_TIMES[label]
  for i in range(times.size()):
   var f=export_frame(segment,times[i],"key_%s_%02d.bin"%[label.to_lower(),i])
   f["label"]="%s / %.2f s"%[label,times[i]];qa_frames.append(f)
 for i in range(segments.size()-1):
  var before:Dictionary=segments[i];var after:Dictionary=segments[i+1]
  pose(before,before.duration);var a=vertices()
  pose(after,0.);var b=vertices();var worst=0.
  for j in range(a.size()):worst=maxf(worst,a[j].distance_to(b[j]))
  boundaries.append({"from":String(before.state),"to":String(after.state),"max_vertex_delta_px":worst})
 pose(segments[0],0.);var idle_a=vertices()
 pose(segments[0],3.);var idle_b=vertices();var idle_delta=0.
 for j in range(idle_a.size()):idle_delta=maxf(idle_delta,idle_a[j].distance_to(idle_b[j]))
 var unchanged=true
 for file in provenance:
  if FileAccess.get_sha256(file)!=provenance[file]:unchanged=false
 write_json(OUT+"/native_geometry.json",{"engine":Engine.get_version_info().string,"fps":30,"duration":total,"video_duration":frames.size()/30.,"segments":segments,"geometry":geometry,"frames":frames,"qa_frames":qa_frames,"boundaries":boundaries,"idle_loop_max_vertex_delta_px":idle_delta,"source_hashes":provenance,"source_unchanged_during_export":unchanged,"scope":"Native Godot Polygon2D vertices, transforms, UVs and triangles. Offline raster, not a Godot window recording."})
 write_json("res://tests/five_states_frame_metrics.json",metrics)
 print("FIVE_STATE_NATIVE_EXPORT ",frames.size()," movie frames + ",qa_frames.size()," exact key frames / ",geometry.size()," visible parts / ",total," seconds")
 print("CONTINUITY ",JSON.stringify(boundaries)," IDLE_LOOP ",idle_delta," SOURCE_UNCHANGED ",unchanged)
 quit(0 if unchanged else 1)
