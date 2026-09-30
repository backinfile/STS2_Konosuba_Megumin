extends Node2D
const RIG = preload("res://scenes/megumin.tscn")
var hero: MeguminRig
var game: MeguminRig
var timeline := 0.0
var last_index := -1
var auto_demo := true
var impact_pulse := 0.0
var state_text: Label
var marker_text: Label
var progress: ProgressBar
var shots: Dictionary = {}
const DEMO = [[0.0,"Idle"],[3.2,"Cast"],[6.7,"Attack"],[9.6,"Hit"],[11.0,"Relaxed"],[16.8,"Dead"]]
const SHOTS = {"Idle":1.2,"Cast":4.6,"Attack":7.45,"Hit":9.72,"Relaxed":13.2,"Dead":19.0}
func label_at(text: String, pos: Vector2, size: int, color: Color) -> Label:
	var node := Label.new()
	node.text = text
	node.position = pos
	node.add_theme_font_size_override("font_size",size)
	node.add_theme_color_override("font_color",color)
	add_child(node)
	return node
func _ready() -> void:
	hero = RIG.instantiate()
	hero.beam_length=480.0
	hero.position = Vector2(400,770)
	hero.scale = Vector2.ONE*.425
	add_child(hero)
	game = RIG.instantiate()
	game.beam_length=480.0
	game.position = Vector2(1130,720)
	game.scale = Vector2.ONE*(320./1482.)
	add_child(game)
	hero.attack_impact.connect(_impact)
	label_at("MEGUMIN",Vector2(54,35),32,Color("f6d394"))
	label_at("EXPLOSION  /  ARTICULATED ANIMATION STUDY",Vector2(56,79),14,Color("8297b9"))
	label_at("01  CHARACTER STAGE",Vector2(54,122),13,Color("687f9e"))
	label_at("02  GAME-SCALE CHECK",Vector2(962,122),13,Color("687f9e"))
	label_at("320 px character height",Vector2(962,151),16,Color("cfdef1"))
	label_at("1× playback  ·  planted feet  ·  independent cape",Vector2(56,800),14,Color("8297b9"))
	label_at("Godot 4.6  /  Standalone preview",Vector2(962,800),14,Color("8297b9"))
	state_text = label_at("IDLE",Vector2(962,219),29,Color("f6d394"))
	marker_text = label_at("Loop / breathing + cape",Vector2(962,263),15,Color("b8c9df"))
	var names = ["Idle","Cast","Attack","Hit","Relaxed","Dead"]
	for i in range(names.size()):
		var button := Button.new()
		button.text = "%d  %s" % [i+1,names[i]]
		button.position = Vector2(54+i*136,847)
		button.size = Vector2(124,32)
		button.pressed.connect(_manual.bind(names[i]))
		add_child(button)
	var reset := Button.new()
	reset.text = "Replay demo  [Space]"
	reset.position = Vector2(1015,847)
	reset.size = Vector2(330,32)
	reset.pressed.connect(_restart)
	add_child(reset)
	progress = ProgressBar.new()
	progress.position = Vector2(55,827)
	progress.size = Vector2(1290,3)
	progress.show_percentage = false
	progress.max_value = 21.0
	add_child(progress)
func _manual(state: String) -> void:
	auto_demo=false
	hero.reset_character(); game.reset_character()
	hero.play_animation(state);game.play_animation(state)
	_update_description(state)
func _restart() -> void:
	hero.reset_character();game.reset_character()
	timeline=0.;last_index=-1;auto_demo=true
func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode>=KEY_1 and event.keycode<=KEY_6: _manual(["Idle","Cast","Attack","Hit","Relaxed","Dead"][event.keycode-KEY_1])
		elif event.keycode==KEY_SPACE: _restart()
func _impact() -> void:
	impact_pulse=1.0
	print("MARKER attack_impact at Attack=1.55s")
func _update_description(state: String) -> void:
	state_text.text = state.to_upper()
	var descriptions={"Idle":"3.0 s loop / breath + cape", "Cast":"1.55 s / crouch, elbow lift, chant", "Attack":"3.50 s / full cast; impact at 1.55 s", "Hit":"0.66 s / recoil + recovery", "Relaxed":"4.8 s / authored exhausted hold", "Dead":"1.6 s / dedicated pose, terminal hold"}
	marker_text.text=descriptions[state]
func _process(delta: float) -> void:
	timeline+=delta
	impact_pulse=maxf(0,impact_pulse-delta*3.)
	if auto_demo:
		var index=0
		for i in range(DEMO.size()):
			if timeline>=DEMO[i][0]:index=i
		if index!=last_index:
			last_index=index
			hero.play_animation(DEMO[index][1]);game.play_animation(DEMO[index][1])
			_update_description(DEMO[index][1])
	progress.value=fmod(timeline,21.)
	for state in SHOTS:
		if timeline>=SHOTS[state] and not shots.has(state) and "--capture" in OS.get_cmdline_user_args():
			shots[state]=true
			_capture.call_deferred(state)
	if timeline>21.1 and "--capture" in OS.get_cmdline_user_args(): get_tree().quit()
	queue_redraw()
func _capture(state: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://preview/key_%s.png"%state)
func _draw() -> void:
	draw_rect(Rect2(0,0,1440,900),Color("080d16"))
	draw_rect(Rect2(34,108,874,692),Color("0d1726"))
	draw_rect(Rect2(932,108,474,692),Color("101b2c"))
	for x in range(54,904,50):draw_line(Vector2(x,160),Vector2(x,770),Color(.24,.35,.5,.055),1.)
	for y in range(170,771,50):draw_line(Vector2(54,y),Vector2(886,y),Color(.24,.35,.5,.055),1.)
	draw_line(Vector2(54,773),Vector2(886,773),Color("314660"),1.)
	draw_line(Vector2(955,723),Vector2(1385,723),Color("314660"),1.)
	draw_set_transform(Vector2(400,768),0,Vector2(1,.2))
	draw_circle(Vector2.ZERO,155,Color(0,0,0,.3))
	draw_set_transform(Vector2(1130,721),0,Vector2(1,.2))
	draw_circle(Vector2.ZERO,79,Color(0,0,0,.3))
	draw_set_transform(Vector2.ZERO)
	if impact_pulse>0:
		draw_rect(Rect2(932,300,474,3),Color(1,.45,.12,impact_pulse))
