extends SceneTree
var passed:=0
var failed:=0
var events:=0
var rig:MeguminRig
func check(condition:bool,description:String) -> void:
	if condition:passed+=1;print("PASS  ",description)
	else:failed+=1;push_error("FAIL  "+description)
func _initialize() -> void:call_deferred("run")
func tick(seconds:float) -> void:
	var steps:=ceili(seconds*120.)
	for i in range(steps):rig.player.advance(seconds/float(steps));rig._update_visuals()
	await process_frame
func run() -> void:
	rig=load("res://scenes/megumin.tscn").instantiate();root.add_child(rig)
	await process_frame
	rig.set_process(false)
	rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	rig.player.callback_mode_method=AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	rig.attack_impact.connect(func():events+=1)
	check(rig.casting_poses.size()==6,"Six separately authored casting silhouettes loaded")
	check(not rig.effects_enabled,"VFX are disabled by default")
	check(rig.player.get_animation_list().size()==6,"All six native animation resources remain available")
	check(rig.player.get_animation("Idle").loop_mode==Animation.LOOP_LINEAR,"Idle remains looping")
	check(not rig.play_animation("Unknown"),"Unknown animation is rejected")
	check(rig.play_animation("casting") and rig.current_state==&"Cast","Lowercase alias resolves to Cast")
	var anim:=rig.player.get_animation("Attack")
	var pose_track:=anim.find_track(NodePath(".:pose_index"),Animation.TYPE_VALUE)
	check(pose_track>=0 and anim.value_track_get_update_mode(pose_track)==Animation.UPDATE_DISCRETE,"Authored-pose switches are discrete native property keys")
	check(anim.length==3.5,"Full cast-to-exhaust sequence is 3.50 seconds")
	rig.auto_return_to_idle=false
	var sample_times:=[.16,.40,.98,1.60,2.25,2.77]
	var expected:=["coil","raise","chant","release","recover","exhaust"]
	var staff_length:=(CastingPoseMesh.SHARED_BOTTOM-CastingPoseMesh.SHARED_GRIP).length()*CastingPoseMesh.SHARED_STAFF_SCALE
	for i in range(sample_times.size()):
		rig.play_animation("Attack");rig.seek_pose(sample_times[i]);rig._update_visuals()
		var pose:=rig.active_pose
		check(pose!=null and pose.pose_id==expected[i],"Phase %d uses its own authored %s silhouette"%[i+1,expected[i]])
		check(pose.current_foot_left.distance_to(Vector2(-443,0))<.01,"%s left sole stays exactly on its anchor"%expected[i])
		check(pose.current_foot_right.distance_to(Vector2(443,-45))<.01,"%s right sole stays exactly on its anchor"%expected[i])
		var grip:=pose.shared_staff.position
		var tip:=pose.shared_staff.transform*((CastingPoseMesh.SHARED_BOTTOM-CastingPoseMesh.SHARED_GRIP)*CastingPoseMesh.SHARED_STAFF_SCALE)
		check(absf(grip.distance_to(tip)-staff_length)<.02,"%s uses the same rigid, unscaled staff length"%expected[i])
		check(grip.distance_to(pose.transformed_joint("grip"))<.05,"%s prop and palm share the same gripping point"%expected[i])
		var count:=0
		for other in rig.casting_poses:
			if other.visible:count+=1
		check(count==1 and pose.modulate.a==1.,"%s has one opaque pose, without crossfade ghosts"%expected[i])
	check(rig.casting_poses[1].common_pieces.size()==2 and rig.casting_poses[3].common_pieces.size()==2,"Chant and exhaustion reuse identical pinned leg cutouts")
	check(rig.casting_poses[2].common_pieces.is_empty(),"Release retains its newly drawn forward-load legs")
	check(rig.casting_poses[0].mesh.polygon.size()>3000,"Pose motion uses a dense native Polygon2D control mesh")
	check(rig.casting_poses[0].mesh.texture_filter==CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,"Pose textures use mipmapped linear minification")
	events=0;rig.play_animation("Attack")
	for seek_time in [1.55,.5,1.55,2.1,1.55]:rig.seek_pose(seek_time)
	await process_frame
	check(events==0,"Repeated visual seeks across the release cannot manufacture damage")
	rig.play_animation("Attack")
	await tick(1.53)
	check(events==0,"No damage marker before the full-body release")
	await tick(.04)
	check(events==1,"Exactly one damage marker crosses Attack=1.55s")
	await tick(2.1)
	check(events==1,"Holding exhaustion does not emit extra damage")
	rig.play_animation("Attack");await tick(.9);rig.play_animation("Hit")
	var interrupted:=events;await tick(1.1)
	check(events==interrupted,"Interrupted cast cannot leak a later damage signal")
	check(rig.pose_index==-1,"Legacy Hit clears any authored casting-pose index")
	rig.auto_return_to_idle=true
	for state in [&"Cast",&"Attack",&"Hit",&"Relaxed"]:
		rig.play_animation(state);await tick(rig.player.get_animation(state).length+.2)
		check(rig.current_state==&"Idle","%s preserves opt-in automatic return to Idle"%state)
	rig.play_animation("Dead");await tick(2.)
	check(rig.current_state==&"Dead" and rig.dead_amount>.99,"Dead reaches its dedicated terminal pose")
	check(not rig.play_animation("Idle"),"Dead prevents accidental animation restart")
	await tick(1.)
	check(rig.dead_amount>.99,"Dead remains terminal after extra elapsed time")
	rig.reset_character();await tick(.2)
	check(rig.current_state==&"Idle" and rig.pose_index==-1 and rig.dead_amount<.01,"Explicit reset restores a clean Idle")
	var normal:MeguminRig=load("res://scenes/megumin.tscn").instantiate()
	normal.auto_return_to_idle=false;root.add_child(normal);await process_frame
	normal.set_process(false);normal.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	normal.play_animation("Attack");normal.player.advance(1.53);await process_frame
	check(normal.impact_count==0,"Normal deferred playback has no impact before 1.55s")
	normal.player.advance(.04);await process_frame
	check(normal.impact_count==1,"Normal deferred playback emits exactly one release impact")
	normal.player.advance(2.);await process_frame
	check(normal.impact_count==1,"Normal deferred playback does not duplicate the release event")
	normal.queue_free()
	var result:={"engine":Engine.get_version_info().string,"passed":passed,"failed":failed,"impact_marker_seconds":1.55,"authored_poses":6,"common_leg_poses":["chant","exhaust"],"release_uses_new_legs":true,"effects_default":false,"graphics_validation":"Godot graphical capture unavailable: local Unix display socket blocked; native geometry checked with deterministic offline raster preview","scope":"standalone editable Godot project; not STS2 integration"}
	var file:=FileAccess.open("res://tests/results.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"))
	print("RESULT  ",passed," passed / ",failed," failed")
	rig.queue_free();await process_frame;quit(0 if failed==0 else 1)
