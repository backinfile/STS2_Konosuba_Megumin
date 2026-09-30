extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;root.add_child(rig);await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var worst=0.;var failures:Array=[]
 # Check position continuity directly around every authored segment boundary.
 for t in [.45,1.2,2.,2.65,3.,3.35,4.15,4.7]:
  rig.seek_pose(t-.0001);var before:Array=[]
  for piece in rig.pieces:
   for v in piece.node.polygon:before.append(piece.node.global_transform*v)
  rig.seek_pose(t+.0001);var i=0
  for piece in rig.pieces:
   for v in piece.node.polygon:
    var error:float=before[i].distance_to(piece.node.global_transform*v);worst=maxf(worst,error);i+=1
  if worst>1.:failures.append("discontinuity near %.2f"%t)
 var anim:Animation=rig.player.get_animation("ContinuousCast")
 var non_numeric=false
 for i in range(anim.get_track_count()):
  if anim.track_get_type(i)!=Animation.TYPE_VALUE:non_numeric=true
 if non_numeric:failures.append("non-numeric pose track")
 var report={"passed":failures.is_empty(),"segment_boundary_tests":8,"epsilon_seconds":.0001,"max_boundary_vertex_delta_px":worst,"track_count":anim.get_track_count(),"failures":failures}
 var f=FileAccess.open("res://tests/timeline_continuity.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
 print("TIMELINE_CONTINUITY ",JSON.stringify(report));quit(0 if failures.is_empty() else 1)
