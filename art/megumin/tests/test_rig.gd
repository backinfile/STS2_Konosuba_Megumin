extends SceneTree
var passed := 0
var failed := 0
var events := 0
var rig: MeguminRig
func check(condition: bool, description: String) -> void:
	if condition:
		passed += 1
		print("PASS  ",description)
	else:
		failed += 1
		push_error("FAIL  " + description)
func _initialize() -> void:
	call_deferred("run")
func tick(seconds: float) -> void:
	var steps := ceili(seconds*120.)
	for i in range(steps):
		rig.player.advance(seconds/float(steps))
		rig._update_visuals()
	await process_frame
func run() -> void:
	rig = load("res://scenes/megumin.tscn").instantiate()
	root.add_child(rig)
	await process_frame
	rig.set_process(false)
	rig.player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	rig.attack_impact.connect(func(): events += 1)
	check(rig.pieces.size()==16, "16 independent source-texture pieces constructed")
	check(rig.player.has_animation("Idle"), "Native Animation library loaded")
	check(rig.player.get_animation("Idle").loop_mode==Animation.LOOP_LINEAR, "Idle loops")
	check(not rig.play_animation("Unknown"), "Invalid state rejected")
	for state in [&"Cast",&"Hit",&"Relaxed"]:
		rig.play_animation(state)
		await tick(rig.player.get_animation(state).length+.3)
		check(rig.current_state==&"Idle", "%s automatically returns to Idle"%state)
	rig.play_animation("Attack")
	await tick(.70)
	check(events==0, "No damage signal before the Attack impact frame")
	await tick(.04)
	check(events==1, "Exactly one damage signal at Attack=0.72s")
	await tick(1.5)
	check(events==1 and rig.current_state==&"Idle", "Attack completes once and returns to Idle")
	var soles := [Vector2(280,1508),Vector2(860,1473)]
	for state in [&"Idle",&"Cast",&"Attack",&"Hit"]:
		rig.play_animation(state)
		await tick(minf(.5,rig.player.get_animation(state).length*.5))
		for sole in soles:check(rig._map(sole,"legs").is_equal_approx(sole), "%s sole remains planted"%state)
	rig.play_animation("Cast")
	await tick(1.)
	check(absf(rig.left_upper)>20 and absf(rig.left_forearm)>45, "Cast articulates upper arm and forearm independently")
	check(rig._map(rig.GRIP,"grip").is_equal_approx(rig._map(rig.GRIP,"right_forearm")), "Staff and palm share a non-sliding wrist pivot")
	var cape_point := Vector2(80,840)
	rig.elapsed=0.
	var c0 := rig._map(cape_point,"cape")
	rig.elapsed=.75
	check(c0.distance_to(rig._map(cape_point,"cape"))>5., "Cape has independent mesh movement")
	rig.play_animation("Attack")
	await tick(.2)
	rig.play_animation("Hit")
	var interrupted_events := events
	await tick(1.)
	check(events==interrupted_events, "Interrupted Attack does not leak an impact signal")
	rig.play_animation("Dead")
	await tick(2.)
	check(rig.current_state==&"Dead" and is_equal_approx(rig.dead_amount,1.), "Dead reaches dedicated terminal pose")
	check(not rig.play_animation("Idle"), "Dead blocks accidental return to Idle")
	await tick(3.)
	check(rig.current_state==&"Dead" and is_equal_approx(rig.dead_amount,1.), "Dead holds its terminal state")
	rig.reset_character()
	await tick(.3)
	check(rig.current_state==&"Idle" and rig.dead_amount<.01, "Explicit reset restores Idle")
	var result := {"engine":Engine.get_version_info().string,"passed":passed,"failed":failed,"impact_marker_seconds":0.72,"pieces":rig.pieces.size(),"origin":[575,1508],"scope":"standalone Godot project; not STS2 integration"}
	var file := FileAccess.open("res://tests/results.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"\t"))
	print("RESULT  ",passed," passed / ",failed," failed")
	rig.queue_free()
	await process_frame
	quit(0 if failed==0 else 1)
