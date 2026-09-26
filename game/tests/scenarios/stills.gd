extends RefCounted
## Transparent renders for the landing page, made by the game from its own Blender-built
## models: the 3D logo exactly as the title screen lights it, and the biplane under the
## same studio lights. Writes <out>/logo.png and <out>/plane.png.

const PLANE := preload("res://assets/models/plane.glb")


func run(dev: Node) -> void:
	var logo := LogoView.new()
	dev.get_tree().root.add_child(logo)
	logo.set_process(false)
	logo.stretch = false
	var logo_vp: SubViewport = logo.get_child(0)
	logo_vp.size = Vector2i(2560, 960)
	await _save(dev, logo_vp, "logo")
	logo.queue_free()

	var vp := SubViewport.new()
	vp.size = Vector2i(1600, 1000)
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_8X
	dev.get_tree().root.add_child(vp)
	# The logo's studio lights, so the page's art matches.
	for node in logo_vp.get_children():
		if node is WorldEnvironment or node is DirectionalLight3D:
			vp.add_child(node.duplicate())
	var plane: Node3D = PLANE.instantiate()
	vp.add_child(plane)
	var cam := Camera3D.new()
	cam.fov = 30.0
	vp.add_child(cam)
	cam.position = Vector3(-7.4, 3.1, -8.6)
	cam.look_at(Vector3(0.0, 0.2, -0.3))
	cam.current = true
	await _save(dev, vp, "plane")
	vp.queue_free()


func _save(dev: Node, vp: SubViewport, shot_name: String) -> void:
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	for i in 4:
		await RenderingServer.frame_post_draw
	var img := vp.get_texture().get_image()
	var dir := String(dev.out_dir)
	DirAccess.make_dir_recursive_absolute(dir)
	var path := dir.path_join(shot_name + ".png")
	img.save_png(path)
	print("[capture] %s (%dx%d)" % [path, img.get_width(), img.get_height()])
