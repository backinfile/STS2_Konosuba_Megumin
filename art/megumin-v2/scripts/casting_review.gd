extends Node2D
## Deterministic, VFX-free acceptance reel. One complete sequence at original speed.
const RIG = preload("res://scenes/megumin.tscn")
const PHASES = ["01   COIL + BEND", "02   ELBOW LIFT + OPEN", "03   RAISE + CHANT", "04   FULL-BODY RELEASE", "05   RELEASE FOLLOW-THROUGH", "06   EXHAUST + SETTLE"]
var hero: MeguminRig
var mini: MeguminRig
var timeline := 0.0
var state_label: Label
var time_label: Label
var shots: Dictionary = {}
const SNAPSHOTS = {"01_coil":.18,"02_raise":.40,"03_chant":.97,"04_hold":1.27,"05_release":1.59,"06_recover":2.27,"07_exhaust":2.78}
func text_at(value: String,pos: Vector2,size: int,color: Color) -> Label:
	var label := Label.new()
	label.text=value;label.position=pos
	label.add_theme_font_size_override("font_size",size)
	label.add_theme_color_override("font_color",color)
	add_child(label);return label
func _ready() -> void:
	hero=RIG.instantiate();hero.position=Vector2(442,753);hero.scale=Vector2.ONE*.42
	hero.auto_return_to_idle=false;hero.effects_enabled=false;add_child(hero)
	mini=RIG.instantiate();mini.position=Vector2(1138,725);mini.scale=Vector2.ONE*(320./1100.)
	mini.auto_return_to_idle=false;mini.effects_enabled=false;add_child(mini)
	hero.play_animation("Attack");mini.play_animation("Attack")
	text_at("MEGUMIN   /   CASTING v2",Vector2(52,31),29,Color("f1d5a0"))
	text_at("AUTHORED SILHOUETTES  +  EDITABLE GODOT TIMELINES",Vector2(53,73),13,Color("869cba"))
	text_at("LARGE MOTION REVIEW",Vector2(54,118),14,Color("8aa5c4"))
	text_at("320 px CHARACTER REFERENCE",Vector2(966,118),14,Color("8aa5c4"))
	text_at("ALL VFX OFF  /  1x SPEED",Vector2(966,151),17,Color("e2ce9e"))
	state_label=text_at(PHASES[0],Vector2(53,804),23,Color("f4ddae"))
	time_label=text_at("0.00 s",Vector2(1195,808),20,Color("cedbeb"))
	text_at("Pinned soles   /   No limb scaling   /   No pose crossfade",Vector2(54,849),14,Color("849cbb"))
	text_at("Native AnimationPlayer  ·  Standalone study",Vector2(966,849),13,Color("849cbb"))
func _process(delta:float) -> void:
	timeline+=delta
	var phase=0
	if timeline>=.24:phase=1
	if timeline>=.60:phase=2
	if timeline>=1.40:phase=3
	if timeline>=2.05:phase=4
	if timeline>=2.43:phase=5
	state_label.text=PHASES[phase]
	if timeline>=1.15 and timeline<1.40:state_label.text="03   FULL CHARGE / HOLD"
	time_label.text="%.2f s" % minf(timeline,3.5)
	for key in SNAPSHOTS:
		if timeline>=SNAPSHOTS[key] and not shots.has(key) and "--capture" in OS.get_cmdline_user_args():
			shots[key]=true;capture.call_deferred(key)
	if timeline>4.2 and "--capture" in OS.get_cmdline_user_args():get_tree().quit()
	queue_redraw()
func capture(key:String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://preview/review")
	get_viewport().get_texture().get_image().save_png("res://preview/review/%s.png" % key)
func _draw() -> void:
	draw_rect(Rect2(0,0,1440,900),Color("090e18"))
	draw_rect(Rect2(32,108,880,685),Color("101b2b"))
	draw_rect(Rect2(938,108,470,685),Color("142133"))
	for y in range(180,748,80):draw_line(Vector2(54,y),Vector2(887,y),Color(.32,.42,.55,.08),1.)
	draw_line(Vector2(54,754),Vector2(886,754),Color("3a5067"),1.)
	draw_line(Vector2(958,726),Vector2(1386,726),Color("40586f"),1.)
	for p in [Vector2(442-443*.42,753),Vector2(442+443*.42,753-45*.42)]:
		draw_line(p+Vector2(0,-1),p+Vector2(0,10),Color("849cab"),2.)
	for p in [Vector2(1138-443*(320./1100.),725),Vector2(1138+443*(320./1100.),725-45*(320./1100.))]:
		draw_line(p+Vector2(0,-1),p+Vector2(0,10),Color("849cab"),2.)
	draw_rect(Rect2(53,782,1332*minf(timeline/3.5,1.),3),Color("d8b780"))

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_SPACE:
		timeline=0.;hero.play_animation("Attack");mini.play_animation("Attack")
