class_name MeguminRig
extends Node2D
## Source-texture cutout rig. All angles are degrees. Origin is the planted sole line.
signal animation_state_changed(state: StringName)
signal animation_completed(state: StringName)
signal attack_impact
signal marker_reached(marker: StringName)

const ORIGIN := Vector2(575, 1508)
const HIP := Vector2(619, 701)
const NECK := Vector2(583, 498)
const LEFT_SHOULDER := Vector2(484, 539)
const LEFT_ELBOW := Vector2(444, 631)
const RIGHT_SHOULDER := Vector2(674, 545)
const RIGHT_ELBOW := Vector2(740, 631)
const GRIP := Vector2(875, 588)
const STATES: Array[StringName] = [&"Idle", &"Cast", &"Attack", &"Hit", &"Relaxed", &"Dead"]
const STATE_ALIASES := {"idle":"Idle", "cast":"Cast", "casting":"Cast", "attack":"Attack", "hit":"Hit", "hurt":"Hit", "relaxed":"Relaxed", "exhausted":"Relaxed", "dead":"Dead", "death":"Dead"}
@export var effects_enabled := true
@export var beam_length := 690.0
@export var animation_speed := 1.0
@export var auto_return_to_idle := true
@export var breath := 0.0
@export var body_lean := 0.0
@export var head_tilt := 0.0
@export var left_upper := 0.0
@export var left_forearm := 0.0
@export var right_upper := 0.0
@export var right_forearm := 0.0
@export var grip_tilt := 0.0
@export var cape_strength := 1.0
@export var cast_power := 0.0
@export var blast_power := 0.0
@export var hit_flash := 0.0
@export var collapse := 0.0
@export var relaxed_amount := 0.0
@export var dead_amount := 0.0
var current_state: StringName = &"Idle"
var elapsed := 0.0
var player: AnimationPlayer
var pieces: Array[Dictionary] = []
var standing: Node2D
var relaxed: Sprite2D
var dead: Sprite2D
var impact_count := 0
var _dead_locked := false

func _ready() -> void:
	standing = Node2D.new()
	standing.name = "ArticulatedCutouts"
	standing.z_index = 10
	add_child(standing)
	var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/rig_geometry.json"))
	var master = load("res://assets/source/megumin_master.png")
	var staff = load("res://assets/source/megumin_staff_complete.png")
	var base = load("res://assets/source/megumin_occlusion_base.png")
	for data in geometry.parts:
		var polygon := Polygon2D.new()
		polygon.name = data.name
		polygon.texture = base if data.texture == "base" else (staff if data.texture == "staff" else master)
		polygon.z_index = int(data.z)
		polygon.antialiased = true
		var verts := PackedVector2Array()
		var uv := PackedVector2Array()
		for p in data.vertices: verts.append(Vector2(p[0], p[1]))
		for p in data.uv: uv.append(Vector2(p[0], p[1]))
		polygon.polygon = verts
		polygon.uv = uv
		if not data.triangles.is_empty():
			var polygons: Array[PackedInt32Array] = []
			for tri in data.triangles: polygons.append(PackedInt32Array(tri))
			polygon.polygons = polygons
		standing.add_child(polygon)
		pieces.append({"node":polygon, "rest":verts, "group":data.group})
	relaxed = _pose_sprite("res://assets/poses/megumin_relaxed.png", Vector2(900, 998), .94)
	relaxed.name = "RelaxedPose"
	dead = _pose_sprite("res://assets/poses/megumin_dead.png", Vector2(810, 790), .88)
	dead.name = "DeadPose"
	player = get_node_or_null("AnimationPlayer")
	if player == null:
		player = AnimationPlayer.new()
		player.name = "AnimationPlayer"
		add_child(player)
		var library := AnimationLibrary.new()
		for state in STATES:
			library.add_animation(state, load("res://animations/%s.tres" % state))
		player.add_animation_library("", library)
	player.animation_finished.connect(_animation_finished)
	play_animation(&"Idle")

func _pose_sprite(path: String, anchor: Vector2, factor: float) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.centered = false
	sprite.position = -anchor * factor
	sprite.scale = Vector2.ONE * factor
	sprite.z_index = 12
	sprite.set_meta("base_position",sprite.position)
	sprite.set_meta("base_scale",sprite.scale)
	add_child(sprite)
	return sprite

## Main integration surface. Invalid state returns false. Dead is terminal unless reset_character is called.
func play_animation(state: StringName) -> bool:
	var canonical := StringName(STATE_ALIASES.get(String(state).to_lower(), String(state)))
	if not STATES.has(canonical): return false
	if _dead_locked and canonical != &"Dead": return false
	current_state = canonical
	if canonical == &"Dead": _dead_locked = true
	player.speed_scale = animation_speed
	player.play(canonical, .12)
	animation_state_changed.emit(canonical)
	return true

func reset_character() -> void:
	_dead_locked = false
	play_animation(&"Idle")

func _animation_finished(state: StringName) -> void:
	animation_completed.emit(state)
	if state != &"Dead" and state != &"Idle" and auto_return_to_idle:
		play_animation(&"Idle")

func _emit_attack_impact() -> void:
	impact_count += 1
	attack_impact.emit()
	marker_reached.emit(&"damage")

func _rotate(v: Vector2, pivot: Vector2, angle: float) -> Vector2:
	return pivot + (v - pivot).rotated(deg_to_rad(angle))

func _upper(v: Vector2) -> Vector2:
	return _rotate(v, HIP, body_lean) + Vector2(0, -4.0 * breath + collapse * 90.0)

func _map(v: Vector2, group: String) -> Vector2:
	match group:
		"head": return _upper(_rotate(v, NECK, head_tilt))
		"torso": return _upper(v)
		"left_upper": return _upper(_rotate(v, LEFT_SHOULDER, left_upper))
		"left_forearm": return _upper(_rotate(_rotate(v, LEFT_ELBOW, left_forearm), LEFT_SHOULDER, left_upper))
		"right_upper": return _upper(_rotate(v, RIGHT_SHOULDER, right_upper))
		"right_forearm": return _upper(_rotate(_rotate(v, RIGHT_ELBOW, right_forearm), RIGHT_SHOULDER, right_upper))
		"grip": return _upper(_rotate(_rotate(_rotate(v, GRIP, grip_tilt), RIGHT_ELBOW, right_forearm), RIGHT_SHOULDER, right_upper))
		"skirt":
			var weight := clampf((910.0-v.y)/225.0,0.,1.)
			return v.lerp(_upper(v), weight * .75)
		"cape":
			var pin := clampf((v.y - 485.0)/500.0, 0., 1.)
			var edge := clampf((520.0 - v.x)/490.0, .15, 1.)
			var wave := sin(elapsed * TAU / 3.0 - v.x * .007 + v.y * .003)
			var wave2 := sin(elapsed * TAU / 2.1 + v.x * .011)
			var top_follow := 1.0 - smoothstep(490., 1020., v.y)
			return v.lerp(_upper(v), top_follow) + Vector2((wave*10.0+wave2*4.0)*pin*edge, (wave*17.0+wave2*4.0)*edge*pin) * cape_strength
	return v

func _process(delta: float) -> void:
	elapsed += delta * animation_speed
	_update_visuals()

func _update_visuals() -> void:
	if not is_instance_valid(standing): return
	var pose_alpha := maxf(relaxed_amount, dead_amount)
	standing.modulate = Color(1.0+hit_flash*.5,1.0-hit_flash*.55,1.0-hit_flash*.6, 1.0-pose_alpha)
	for piece in pieces:
		var posed := PackedVector2Array()
		for vertex in piece.rest: posed.append(_map(vertex, piece.group) - ORIGIN)
		piece.node.polygon = posed
	relaxed.modulate.a = relaxed_amount
	dead.modulate.a = dead_amount
	var factor := 1.0 + sin(elapsed*2.1)*.003
	relaxed.scale = relaxed.get_meta("base_scale") * Vector2(1.0,factor)
	relaxed.position = relaxed.get_meta("base_position") * Vector2(1.0,factor)
	queue_redraw()

func _draw() -> void:
	if not effects_enabled: return
	if cast_power > .01 and dead_amount < .5:
		var center := Vector2(0,-20)
		var c := Color(1.,.38,.12,cast_power*.7)
		for n in range(2):
			var pts := PackedVector2Array()
			for i in range(65):
				var a := float(i)/64.*TAU
				pts.append(center+Vector2(cos(a)*(230.+n*24.),sin(a)*(48.+n*5.)))
			draw_polyline(pts,c,3.,true)
		for i in range(8):
			var a := elapsed*.5+float(i)*TAU/8.
			var p := center+Vector2(cos(a)*238.,sin(a)*50.)
			draw_line(p+Vector2(-8,0),p+Vector2(8,0),c,4.,true)
		var orb := _map(Vector2(939,244),"grip")-ORIGIN
		draw_arc(orb,62.+sin(elapsed*6.)*8.,0.,TAU,64,Color(1,.42,.12,cast_power*.8),5.,true)
		for i in range(9):
			var a := float(i)*TAU/9.+elapsed
			draw_circle(orb+Vector2.from_angle(a)*(82.+sin(elapsed*4.+i)*10.),3.+cast_power*2.,Color(1.,.72,.25,cast_power))
	if blast_power > .01:
		var orb := _map(Vector2(939,244),"grip")-ORIGIN
		var endpoint := orb+Vector2(beam_length,15.)
		draw_line(orb,endpoint,Color(1.,.15,.035,blast_power*.22),80.*blast_power,true)
		draw_line(orb,endpoint,Color(1.,.4,.04,blast_power*.66),34.*blast_power,true)
		draw_line(orb,endpoint,Color(1.,.94,.65,blast_power),10.*blast_power,true)
		for i in range(8):
			var a := float(i)*TAU/8.+elapsed
			draw_line(orb+Vector2.from_angle(a)*30.,orb+Vector2.from_angle(a)*(80.+blast_power*100.),Color(1.,.6,.1,blast_power),4.,true)
