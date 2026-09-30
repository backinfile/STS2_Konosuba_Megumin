extends Node2D
func _ready() -> void:
	var view := SubViewport.new()
	view.size = Vector2i(1600,1760)
	view.transparent_bg = true
	view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(view)
	var rig: MeguminRig = load("res://scenes/megumin.tscn").instantiate()
	rig.effects_enabled=false
	rig.position=Vector2(760,1640)
	view.add_child(rig)
	rig.set_process(false)
	rig.player.pause()
	rig.player.seek(0.,true)
	rig.elapsed=0.
	rig._update_visuals()
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://assets/runtime")
	var output := view.get_texture().get_image()
	var error := output.save_png("res://assets/runtime/megumin_idle_neutral.png")
	print("RUNTIME_PNG export=",error," size=",output.get_size()," ground_anchor=(760,1640)")
	get_tree().quit(error)
