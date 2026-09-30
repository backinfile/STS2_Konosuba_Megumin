extends SceneTree
## Portable no-window fallback. Dumps the actual native AnimationPlayer/Polygon2D
## output. The companion software renderer never changes the authored PNG files.
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var rig: MeguminRig = load("res://scenes/megumin.tscn").instantiate()
	rig.auto_return_to_idle=false;rig.effects_enabled=false
	root.add_child(rig)
	await process_frame
	rig.set_process(false)
	rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	rig.play_animation("Attack")
	var geometry: Dictionary = {}
	var frames: Array = []
	DirAccess.make_dir_recursive_absolute("res://preview/software")
	for f in range(127):
		var time := minf(float(f)/30.,3.5)
		rig.seek_pose(time)
		rig.elapsed=time;rig._update_visuals()
		var pose := rig.active_pose
		var nodes: Array[Polygon2D] = []
		if pose.foreground_mesh != null:nodes.append(pose.mesh)
		for part in pose.common_pieces:nodes.append(part.node)
		for child in pose.shared_staff.get_children():nodes.append(child)
		if pose.foreground_mesh == null:nodes.append(pose.mesh)
		else:nodes.append(pose.foreground_mesh)
		var frame := {"time":float(f)/30.,"pose":pose.pose_id,"parts":[]}
		var binary := FileAccess.open("res://preview/software/frame_%04d.bin"%f,FileAccess.WRITE)
		for node in nodes:
			var key := "%s/%s"%[pose.pose_id,node.name]
			if not geometry.has(key):
				var uv:Array=[]
				for point in node.uv:uv.append([point.x,point.y])
				var triangles:Array=[]
				if node.polygons.is_empty():
					var indices:=Geometry2D.triangulate_polygon(node.polygon)
					for i in range(0,indices.size(),3):triangles.append([indices[i],indices[i+1],indices[i+2]])
				else:
					for tri in node.polygons:triangles.append([tri[0],tri[1],tri[2]])
				var mask: Dictionary = pose.source_data.duplicate(true) if node==pose.mesh or node==pose.foreground_mesh else {}
				if node==pose.foreground_mesh:mask["front_only"]=true
				geometry[key]={"texture":node.texture.resource_path,"uv":uv,"triangles":triangles,"mask":mask}
			frame.parts.append({"key":key,"count":node.polygon.size()})
			for vertex in node.polygon:
				var p:Vector2=node.global_transform*vertex
				binary.store_float(p.x);binary.store_float(p.y)
		binary.close()
		frames.append(frame)
	var file:=FileAccess.open("res://preview/software/native_geometry.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine":Engine.get_version_info().string,"fps":30,"geometry":geometry,"frames":frames}))
	print("NATIVE_MESH_EXPORT ",frames.size()," frames / ",geometry.size()," mesh parts / VFX off")
	quit()
