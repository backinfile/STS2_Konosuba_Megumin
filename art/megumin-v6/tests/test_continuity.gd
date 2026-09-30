extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;root.add_child(rig);await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var keys:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://animations/art_directed_keys.json"));var worst=0.;var tested=0
 for key in keys.keys:
  var t:float=key[0]
  if t<=0. or t>=7.2:continue
  rig.seek_pose(t-.0001);var before=[]
  for p in rig.pieces:
   for v in p.node.polygon:before.append(p.node.global_transform*v)
  rig.seek_pose(t+.0001);var i=0
  for p in rig.pieces:
   for v in p.node.polygon:
    worst=maxf(worst,before[i].distance_to(p.node.global_transform*v));i+=1
  tested+=1
 var report={"passed":worst<.1,"authored_boundaries_tested":tested,"max_vertex_delta_px_at_0_0002_seconds":worst}
 var f=FileAccess.open("res://tests/v6_continuity.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));print(JSON.stringify(report));quit(0 if report.passed else 1)
