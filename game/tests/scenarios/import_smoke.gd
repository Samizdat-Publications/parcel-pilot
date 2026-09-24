extends RefCounted
## Import smoke test: import a Blender-built .glb, dump its node tree, capture a frame.


func run(dev: Node) -> void:
	var root: Node = dev.get_tree().current_scene
	var packed: PackedScene = load("res://assets/models/plane.glb")
	dev.check(packed != null, "plane.glb loads as a PackedScene")
	var plane: Node3D = packed.instantiate()
	root.add_child(plane)
	_dump(plane, 0)
	dev.check(plane.find_child("SPIN_Propeller", true, false) != null, "propeller node survives export")
	dev.check(plane.find_child("MK_Parcel", true, false) != null, "marker empties survive export")

	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_SKY
	env.environment.sky = Sky.new()
	env.environment.sky.sky_material = ProceduralSkyMaterial.new()
	root.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.shadow_enabled = true
	root.add_child(sun)
	sun.look_at_from_position(Vector3(4, 8, 6), Vector3.ZERO)
	var cam := Camera3D.new()
	root.add_child(cam)
	cam.look_at_from_position(Vector3(7, 3.5, 9), Vector3(0, 0, 0))
	cam.current = true
	await dev.wait(0.5)
	await dev.capture("import_smoke")


func _dump(node: Node, depth: int) -> void:
	print("  ".repeat(depth), node.name, " <", node.get_class(), ">")
	for child in node.get_children():
		_dump(child, depth + 1)
