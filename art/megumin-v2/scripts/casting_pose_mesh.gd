class_name CastingPoseMesh
extends Node2D
## A hand-authored pose is the silhouette source. This mesh only adds secondary
## motion; it never scales a limb or synthesizes a new pose by extreme warping.
## Staff vertices use one rigid transform shared with the gripping hand.
var pose_id := ""
var source_data: Dictionary = {}
var mesh: Polygon2D
var foreground_mesh: Polygon2D
var vertices := PackedVector2Array()
var mesh_points := PackedVector2Array()
var texture_scale := 1.0
var registration := Transform2D.IDENTITY
var joints: Dictionary = {}
var controls: Dictionary = {}
var source_foot_left := Vector2.ZERO
var source_foot_right := Vector2.ZERO
var current_foot_left := Vector2.ZERO
var current_foot_right := Vector2.ZERO
var _phase := 0.0
var shared_staff: Node2D
var staff_base_angle := 0.0
const SHARED_GRIP := Vector2(579,700)
const SHARED_ORB := Vector2(681,280)
const SHARED_BOTTOM := Vector2(338,1508)
const SHARED_STAFF_SCALE := .80
var _regions: Dictionary = {}
var _rig = null
var influence_data: Array = []
var common_pieces: Array[Dictionary] = []

func setup(data: Dictionary, rig: Node2D) -> void:
	_rig = rig
	source_data = data
	pose_id = data.id
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	var texture: Texture2D = load(data.texture)
	mesh = Polygon2D.new()
	mesh.name = "%s_Mesh" % pose_id
	mesh.texture = texture
	mesh.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	mesh.antialiased = true
	add_child(mesh)
	var left := _vec(data.joints.foot_left)
	var right := _vec(data.joints.foot_right)
	source_foot_left = left
	source_foot_right = right
	var target_left := _vec(data.get("target_foot_left", [-284, 0]))
	var target_right := _vec(data.get("target_foot_right", [284, -8]))
	var scale_factor := target_left.distance_to(target_right) / left.distance_to(right)
	var angle := (target_right - target_left).angle() - (right - left).angle()
	registration = Transform2D(angle, Vector2.ONE * scale_factor, 0.0, Vector2.ZERO)
	registration.origin = target_left - registration * left
	if data.has("registration"):
		scale_factor = float(data.registration.scale)
		registration = Transform2D(0.0, Vector2.ONE*scale_factor, 0.0, Vector2.ZERO)
		registration.origin = _vec(data.registration.target_anchor) - registration * _vec(data.registration.source_anchor)
	texture_scale = scale_factor
	for key in data.joints: joints[key] = registration * _vec(data.joints[key])
	if data.get("common_lower",false):
		joints.foot_left = Vector2(-443,0)
		joints.foot_right = Vector2(443,-45)
		joints.knee_left = Vector2(459,855)-Vector2(679,1225)
		joints.knee_right = Vector2(970,895)-Vector2(679,1225)
	for key in data.get("regions", {}):
		var points := PackedVector2Array()
		for point in data.regions[key]: points.append(registration * _vec(point))
		_regions[key] = points
	_build_shared_staff(data, texture)
	if data.get("common_lower",false): _build_common_lower()
	var source_points := PackedVector2Array()
	var columns := ceili(texture.get_width() / 20.0) + 1
	var rows := ceili(texture.get_height() / 20.0) + 1
	for y in range(rows):
		for x in range(columns):
			var p := Vector2(float(x) / (columns-1) * texture.get_width(), float(y) / (rows-1) * texture.get_height())
			source_points.append(p)
			vertices.append(registration * p)
	var triangles: Array[PackedInt32Array] = []
	for y in range(rows - 1):
		for x in range(columns - 1):
			var a := y * columns + x
			triangles.append(PackedInt32Array([a, a+1, a+columns]))
			triangles.append(PackedInt32Array([a+1, a+columns+1, a+columns]))
	mesh.polygon = vertices
	mesh.uv = source_points
	mesh.polygons = triangles
	if data.get("upper_only",false):
		mesh.z_index=-3
		foreground_mesh=Polygon2D.new()
		foreground_mesh.name="ForegroundSkirtAndHands"
		foreground_mesh.texture=texture
		foreground_mesh.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		foreground_mesh.antialiased=true;foreground_mesh.uv=source_points
		foreground_mesh.polygon=vertices;foreground_mesh.polygons=triangles
		foreground_mesh.z_index=2
		var foreground_material: ShaderMaterial=mesh.material.duplicate()
		foreground_material.set_shader_parameter("front_only",true)
		_set_shader_polygon(foreground_material,"front_polygon","front_count",data.front_polygon,64)
		foreground_mesh.material=foreground_material
		add_child(foreground_mesh)
	for p in vertices: influence_data.append(_weights(p))
	update_mesh(0.0)

func _vec(value: Array) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))

func _distance_to_segment(p: Vector2, a: Vector2, b: Vector2) -> float:
	return p.distance_to(Geometry2D.get_closest_point_to_segment(p, a, b))

func _weights(p: Vector2) -> Dictionary:
	var hip: Vector2 = joints.hip
	var neck: Vector2 = joints.neck
	var grip: Vector2 = joints.grip
	var shoulder: Vector2 = joints.staff_shoulder
	var elbow: Vector2 = joints.staff_elbow
	var feet_y := minf(joints.foot_left.y, joints.foot_right.y)
	var boot_pin := 1.0 - smoothstep(feet_y-160.0, feet_y-48.0, p.y)
	var body := clampf((feet_y - 135.0 - p.y) / maxf(1.0, feet_y - 135.0 - hip.y), 0.0, 1.0)
	var above_hip := clampf((hip.y-p.y)/maxf(1.0, hip.y-neck.y), 0.0, 1.0)
	var staff := 0.0
	if _regions.has("staff") and Geometry2D.is_point_in_polygon(p, _regions.staff): staff = 1.0
	else:
		var d := _distance_to_segment(p, joints.staff_tip, joints.staff_bottom)
		staff = 1.0-smoothstep(14.0, 35.0, d)
	var hand := 1.0 - smoothstep(22., 68., p.distance_to(grip))
	staff = hand # Only the palm is skinned here; the whole staff is a separate rigid layer.
	var head := 0.0
	if _regions.has("head") and Geometry2D.is_point_in_polygon(p, _regions.head): head = 1.0
	elif p.y < neck.y - 30.0: head = (1.0-smoothstep(180.,300.,absf(p.x-neck.x))) * (1.0-staff)
	var arm := 1.0-smoothstep(35.,75.,_distance_to_segment(p, shoulder, elbow))
	var forearm := 1.0-smoothstep(28.,65.,_distance_to_segment(p, elbow, grip))
	var free_hand := 1.0 - smoothstep(20.,85.,p.distance_to(joints.free_hand))
	var free_arm := 1.0-smoothstep(30.,80.,_distance_to_segment(p,joints.free_elbow,joints.free_hand))
	var cape := 0.0
	if _regions.has("cape") and Geometry2D.is_point_in_polygon(p, _regions.cape): cape=1.0
	var knee_left := 1.0 - smoothstep(32.,145.,p.distance_to(joints.knee_left))
	var knee_right := 1.0 - smoothstep(32.,145.,p.distance_to(joints.knee_right))
	return {"pin":maxf(boot_pin,staff),"body":body,"above":above_hip,"staff":staff,"head":head,"arm":arm,"forearm":forearm,"free_hand":free_hand,"free_arm":free_arm,"cape":cape,"knee_left":knee_left,"knee_right":knee_right}

func _rotate(point: Vector2, pivot: Vector2, degrees: float) -> Vector2:
	return pivot + (point - pivot).rotated(deg_to_rad(degrees))

func deform(p: Vector2, weights: Dictionary) -> Vector2:
	var hip: Vector2 = joints.hip
	var neck: Vector2 = joints.neck
	var shoulder: Vector2 = joints.staff_shoulder
	var elbow: Vector2 = joints.staff_elbow
	var grip: Vector2 = joints.grip
	var hip_offset := Vector2(_rig.hip_shift, _rig.knee_load)
	var torso_p := _rotate(p, hip, _rig.torso_pitch) + hip_offset
	var p_body := p.lerp(torso_p, weights.body)
	# The boot sole and its immediate silhouette are exactly pinned in local space.
	if weights.pin < 0.001: return p
	var head_point := _rotate(_rotate(p, neck, _rig.head_pitch), hip, _rig.torso_pitch) + hip_offset
	p_body = p_body.lerp(head_point, weights.head)
	var upper_point := _rotate(_rotate(p, shoulder, _rig.staff_upper), hip, _rig.torso_pitch) + hip_offset
	var lower_point := _rotate(_rotate(_rotate(p, elbow, _rig.staff_forearm), shoulder, _rig.staff_upper), hip, _rig.torso_pitch) + hip_offset
	p_body = p_body.lerp(upper_point, weights.arm * (1.-weights.head))
	p_body = p_body.lerp(lower_point, weights.forearm * (1.-weights.head))
	var prop_point := _rotate(_rotate(_rotate(_rotate(p,grip,_rig.staff_wrist),elbow,_rig.staff_forearm),shoulder,_rig.staff_upper),hip,_rig.torso_pitch)+hip_offset
	p_body = p_body.lerp(prop_point, weights.staff)
	var free_point := _rotate(_rotate(p,joints.free_elbow,_rig.free_arm_angle),hip,_rig.torso_pitch)+hip_offset
	p_body = p_body.lerp(free_point,maxf(weights.free_hand,weights.free_arm)* (1.-weights.staff))
	var knee_offset := Vector2(_rig.knee_load * .2, _rig.knee_load * .16)
	p_body += knee_offset * weights.knee_left * (1.-weights.staff)
	p_body += Vector2(-knee_offset.x,knee_offset.y) * weights.knee_right * (1.-weights.staff)
	if weights.cape > 0.0:
		var loose := smoothstep(neck.y, hip.y+210., p.y)
		var wave := sin(_phase * 3.1 + p.y*.011 + p.x*.008)
		var follow: float = _rig.cape_lag * loose
		p_body += Vector2(-follow * 13. + wave * 3.5, wave * 5.0) * weights.cape * _rig.cape_strength * (1.-weights.staff)
	return p.lerp(p_body,weights.pin)

func update_mesh(phase: float) -> void:
	_phase = phase
	if mesh == null: return
	mesh_points.resize(vertices.size())
	for i in range(vertices.size()): mesh_points[i] = deform(vertices[i], influence_data[i])
	mesh.polygon = mesh_points
	if foreground_mesh != null: foreground_mesh.polygon=mesh_points
	for part in common_pieces:
		var points := PackedVector2Array()
		for i in range(part.rest.size()): points.append(deform(part.rest[i],part.weights[i]))
		part.node.polygon = points
	if shared_staff != null:
		shared_staff.position = _rig._rotate(_rig._rotate(_rig._rotate(joints.grip,joints.staff_elbow,_rig.staff_forearm),joints.staff_shoulder,_rig.staff_upper),joints.hip,_rig.torso_pitch)+Vector2(_rig.hip_shift,_rig.knee_load)
		shared_staff.rotation = staff_base_angle + deg_to_rad(_rig.staff_wrist+_rig.staff_forearm+_rig.staff_upper+_rig.torso_pitch)
	current_foot_left = deform(joints.foot_left,_weights(joints.foot_left))
	current_foot_right = deform(joints.foot_right,_weights(joints.foot_right))

func transformed_joint(key: String) -> Vector2:
	if key == "orb" and shared_staff != null: return shared_staff.transform * ((SHARED_ORB-SHARED_GRIP)*SHARED_STAFF_SCALE)
	return deform(joints[key],_weights(joints[key]))

func _build_shared_staff(data: Dictionary, texture: Texture2D) -> void:
	if not data.has("prop_cut"): return
	var material := ShaderMaterial.new()
	material.shader = load("res://scripts/remove_authored_staff.gdshader")
	material.set_shader_parameter("source_size",Vector2(texture.get_size()))
	var prop_points := PackedVector2Array()
	for point in data.prop_cut: prop_points.append(_vec(point))
	material.set_shader_parameter("prop_count",prop_points.size())
	while prop_points.size()<64: prop_points.append(Vector2.ZERO)
	material.set_shader_parameter("prop_polygon",prop_points)
	var hand_points := PackedVector2Array()
	for point in data.hand_keep: hand_points.append(_vec(point))
	material.set_shader_parameter("hand_count",hand_points.size())
	while hand_points.size()<32:hand_points.append(Vector2.ZERO)
	material.set_shader_parameter("hand_polygon",hand_points)
	if data.has("leg_cut_left"):
		_set_shader_polygon(material,"leg_left","leg_left_count",data.leg_cut_left,64)
		_set_shader_polygon(material,"leg_right","leg_right_count",data.leg_cut_right,64)
		material.set_shader_parameter("lower_clip_y",float(data.lower_clip_y))
		if data.has("lower_keep"): _set_shader_polygon(material,"lower_keep","lower_keep_count",data.lower_keep,32)
	if data.has("prop_keep_head"):_set_shader_polygon(material,"keep_head","keep_head_count",data.prop_keep_head,32)
	if data.has("prop_keep_leg"):_set_shader_polygon(material,"keep_leg","keep_leg_count",data.prop_keep_leg,32)
	mesh.material = material
	shared_staff = Node2D.new()
	shared_staff.name = "SharedRigidStaff"
	shared_staff.z_index = -1
	add_child(shared_staff)
	staff_base_angle=(joints.staff_bottom-joints.grip).angle()-(SHARED_BOTTOM-SHARED_GRIP).angle()
	var staff_texture: Texture2D = load("res://assets/source/megumin_staff_complete.png")
	var outline := PackedVector2Array([Vector2(704,22),Vector2(718,26),Vector2(718,120),Vector2(747,150),Vector2(771,198),Vector2(785,255),Vector2(792,309),Vector2(783,341),Vector2(761,372),Vector2(740,399),Vector2(721,413),Vector2(699,434),Vector2(676,448),Vector2(663,475),Vector2(645,512),Vector2(627,562),Vector2(600,667),Vector2(569,777),Vector2(540,891),Vector2(506,1006),Vector2(460,1159),Vector2(413,1312),Vector2(377,1438),Vector2(338,1518),Vector2(332,1470),Vector2(336,1431),Vector2(371,1311),Vector2(415,1176),Vector2(450,1047),Vector2(482,933),Vector2(506,849),Vector2(540,732),Vector2(570,628),Vector2(602,539),Vector2(612,501),Vector2(620,470),Vector2(622,427),Vector2(615,392),Vector2(621,381),Vector2(652,367),Vector2(688,353),Vector2(720,336),Vector2(742,315),Vector2(753,290),Vector2(753,259),Vector2(745,220),Vector2(731,188),Vector2(714,170),Vector2(700,168),Vector2(684,177),Vector2(661,194),Vector2(656,195),Vector2(641,176),Vector2(629,147),Vector2(623,121),Vector2(630,87),Vector2(650,59),Vector2(680,34)])
	_add_staff_piece("WoodAndShaft",outline,staff_texture)
	var orb := PackedVector2Array()
	for i in range(64):orb.append(SHARED_ORB+Vector2.from_angle(float(i)/64.*TAU)*65.)
	_add_staff_piece("Orb",orb,staff_texture)

func _add_staff_piece(piece_name: String, uv: PackedVector2Array, texture: Texture2D) -> void:
	var piece := Polygon2D.new()
	piece.name=piece_name;piece.texture=texture
	piece.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	piece.antialiased=true
	piece.uv=uv
	var points:=PackedVector2Array()
	for p in uv:points.append((p-SHARED_GRIP)*SHARED_STAFF_SCALE)
	piece.polygon=points
	shared_staff.add_child(piece)

func _set_shader_polygon(material: ShaderMaterial, key: String, count_key: String, points: Array, count: int) -> void:
	var vertices := PackedVector2Array()
	for point in points: vertices.append(_vec(point))
	material.set_shader_parameter(count_key,vertices.size())
	while vertices.size()<count:vertices.append(Vector2.ZERO)
	material.set_shader_parameter(key,vertices)

func _build_common_lower() -> void:
	var texture: Texture2D=load("res://assets/poses/v2/coil.png")
	var definitions := [
		["CloakBacking",[[30,690],[350,650],[530,665],[577,720],[650,743],[735,773],[838,770],[908,840],[972,945],[944,1012],[846,977],[745,960],[630,970],[565,934],[401,956],[266,920],[170,856],[83,824],[42,770]]],
		["PinnedLeftLeg",[[528,715],[617,748],[620,783],[594,820],[553,864],[510,915],[461,966],[415,1002],[413,1023],[387,1044],[364,1048],[346,1090],[332,1134],[305,1181],[291,1207],[290,1235],[233,1240],[189,1231],[181,1211],[207,1171],[233,1124],[263,1077],[277,1041],[273,1010],[263,985],[291,965],[311,943],[334,938],[381,886],[432,842],[465,803],[488,757]]],
		["PinnedRightLeg",[[845,793],[884,809],[928,839],[982,884],[1008,927],[1026,959],[1057,950],[1081,973],[1086,1018],[1088,1057],[1133,1096],[1167,1122],[1188,1153],[1186,1192],[1136,1198],[1084,1186],[1046,1156],[1025,1149],[1025,1108],[1000,1073],[985,1046],[966,1057],[942,1030],[944,1005],[932,975],[918,948],[894,915],[857,890],[815,883],[789,871],[790,833],[802,808]]]
	]
	for def in definitions:
		if def[0]=="CloakBacking": continue
		var node := Polygon2D.new()
		node.name=def[0];node.texture=texture
		node.z_index=-2
		node.antialiased=true
		node.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var uv:=PackedVector2Array();var rest:=PackedVector2Array();var weights:Array=[]
		for coord in def[1]:
			var v:=_vec(coord)
			uv.append(v);rest.append(v-Vector2(679,1225))
			var leg_weights := _weights(v-Vector2(679,1225))
			for key in ["staff","head","arm","forearm","free_hand","free_arm","cape"]:leg_weights[key]=0.0
			weights.append(leg_weights)
		node.uv=uv;node.polygon=rest
		add_child(node)
		common_pieces.append({"node":node,"rest":rest,"weights":weights})
