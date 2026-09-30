extends SceneTree
## Exercise public runtime state API, completion callbacks and attack event.
## No preview renderer, manual seek montage or unapproved Dead is used here.
var checks:Array=[]
var completed:Array=[]
var impact_signals:=0
var rig
func _initialize()->void:call_deferred("run")
func check(label:String,passed:bool,value=null)->void:checks.append({"name":label,"passed":passed,"value":value})
func vertices()->PackedVector2Array:
 var out=PackedVector2Array()
 for p in rig.pieces:
  if p.node.visible:
   for v in p.node.polygon:out.append(p.node.global_transform*v)
 return out
func advance(dt:float)->void:
 rig.elapsed+=dt;rig.player.advance(dt);rig.update_pose()
func run()->void:
 rig=load("res://scenes/megumin.tscn").instantiate();rig.autoplay=false;root.add_child(rig)
 await process_frame;rig.set_process(false)
 rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 rig.player.callback_mode_method=AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
 rig.animation_completed.connect(func(state):completed.append(String(state)))
 rig.attack_impact.connect(func():impact_signals+=1)
 check("Dead exact resource absent",not FileAccess.file_exists("res://animations/Dead.tres"))
 check("Dead not present in native AnimationPlayer",not rig.player.has_animation("Dead"))
 check("Dead request rejected without locking",not rig.play_state(&"Dead") and not rig.dead_locked)
 check("invalid state rejected",not rig.play_state(&"NotAState"))
 for state in [&"Idle",&"Cast",&"Attack",&"Hit",&"Relaxed"]:check(String(state)+" loaded",rig.player.has_animation(state))
 rig.reset_character();advance(.2)
 check("reset selects Idle and clears death controls",rig.current_state==&"Idle" and not rig.dead_locked and rig.face_state==0 and rig.staff_ground_contact==0 and rig.R_heel_raise==0 and rig.L_heel_raise==0 and rig.cape_collapse==0)
 for state in [&"Cast",&"Attack",&"Hit",&"Relaxed"]:
  rig.seek_state(&"Idle",0.);rig.player.stop();rig.play_state(&"Idle");advance(.2)
  completed.clear();var count_before:int=rig.impact_count;var signals_before=impact_signals
  var accepted:bool=rig.play_state(state);check(String(state)+" entry accepted from Idle",accepted)
  var duration:float=rig.player.get_animation(state).length
  var max_step=0.;var max_foot=0.;var scale_error=0.;var return_seen=false;var return_step=0.;var pre=vertices()
  var Rfoot:Vector2=rig.bones.R_foot.position;var Lfoot:Vector2=rig.bones.L_foot.position
  for i in range(int(ceil((duration+.3)*120.))):
   var old:StringName=rig.current_state;advance(1./120.);var now=vertices();var step=0.
   for j in range(pre.size()):step=maxf(step,pre[j].distance_to(now[j]))
   max_step=maxf(max_step,step)
   if old==state and rig.current_state==&"Idle":return_seen=true;return_step=step
   pre=now
   max_foot=maxf(max_foot,rig.bones.R_foot.position.distance_to(Rfoot));max_foot=maxf(max_foot,rig.bones.L_foot.position.distance_to(Lfoot))
   for bone in rig.bones.values():scale_error=maxf(scale_error,maxf(absf(bone.scale.x-1.),absf(bone.scale.y-1.)))
  check(String(state)+" naturally completes once",completed==[String(state)],completed.duplicate())
  check(String(state)+" automatically returns Idle",return_seen and rig.current_state==&"Idle",String(rig.current_state))
  check(String(state)+" return seam subpixel at 120 Hz",return_step<1.,return_step)
  check(String(state)+" feet remain fixed through native playback",max_foot<.00001,max_foot)
  check(String(state)+" bones retain unit scale through native playback",scale_error<.00001,scale_error)
  var expected=1 if state==&"Attack" else 0
  check(String(state)+" expected impact method and signal count",rig.impact_count-count_before==expected and impact_signals-signals_before==expected,{"method_calls":rig.impact_count-count_before,"signals":impact_signals-signals_before})
  check(String(state)+" playback finite and continuous",is_finite(max_step) and max_step<150.,{"max_vertex_step_px_at_120fps":max_step})
 rig.seek_state(&"Idle",0.);rig.play_state(&"Idle");completed.clear()
 for i in range(800):advance(1./120.)
 check("Idle remains looping after more than two cycles",rig.current_state==&"Idle" and rig.player.is_playing() and completed.is_empty())
 check("Dead stays unavailable after all state plays",not rig.player.has_animation("Dead") and not rig.play_state(&"Dead") and not rig.dead_locked)
 var passed=true
 for c in checks:passed=passed and c.passed
 var report={"passed":passed,"checks":checks,"runtime":"Godot headless AnimationPlayer manual advance at 120 Hz; native completion and method callbacks; no graphic-window claim","states":["Idle","Cast","Attack","Hit","Relaxed"],"Dead":"not loaded; play_state rejected; artwork/animation unfinished"}
 var f=FileAccess.open("res://tests/runtime_states_validation.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
 print(JSON.stringify({"passed":passed,"checks":checks.size()}));quit(0 if passed else 1)
