extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;root.add_child(rig);await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var geometry={};var frames=[];var metrics=[];var nodes:Array[Polygon2D]=[]
 DirAccess.make_dir_recursive_absolute("res://preview/software")
 for p in rig.pieces:nodes.append(p.node)
 nodes.sort_custom(func(a,b):return a.z_index<b.z_index)
 for f in range(217):
  var t=float(f)/30.;rig.seek_pose(t);var frame={"time":t,"parts":[]}
  var binary=FileAccess.open("res://preview/software/frame_%04d.bin"%f,FileAccess.WRITE)
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
    geometry[key]={"texture":node.texture.resource_path,"uv":uv,"triangles":tris,"mask":{}}
   frame.parts.append({"key":key,"count":node.polygon.size()})
   for v in node.polygon:
    var q:Vector2=node.global_transform*v;binary.store_float(q.x);binary.store_float(q.y)
  binary.close();frames.append(frame);metrics.append(rig.metrics())
 var file=FileAccess.open("res://preview/software/native_geometry.json",FileAccess.WRITE);file.store_string(JSON.stringify({"engine":Engine.get_version_info().string,"fps":30,"geometry":geometry,"frames":frames}));file.close()
 file=FileAccess.open("res://tests/frame_metrics.json",FileAccess.WRITE);file.store_string(JSON.stringify(metrics));file.close()
 print("V6_NATIVE_EXPORT ",frames.size()," frames / ",geometry.size()," parts")
 quit()
