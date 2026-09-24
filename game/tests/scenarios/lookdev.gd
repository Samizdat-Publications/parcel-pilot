extends RefCounted
## Look development: freezes one gameplay moment and re-renders it under several
## lighting variants, one capture each, for side-by-side comparison
## (tools/lookdev.py composes the sheet). Keys: "env.<prop>" for the Environment,
## "sun.<prop>" for the DirectionalLight3D, "sky.<param>" / "sea.<param>" for the
## sky and cloud-sea shader uniforms.

const VARIANTS_PATH := "res://../build/lookdev_variants.json"


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	var variants: Array = JSON.parse_string(FileAccess.get_file_as_string(VARIANTS_PATH))
	dev.args["autopilot"] = "true"
	main.start_shift()
	await dev.wait(float(dev.args.get("at", "9.0")))
	dev.get_tree().paused = true
	var targets := {
		"env": main.get_node("World/Environment").environment,
		"sun": main.get_node("World/Sun"),
		"sky": (main.get_node("World/Environment").environment as Environment).sky.sky_material,
		"sea": (main.get_node("World/CloudSea") as MeshInstance3D).mesh.surface_get_material(0),
	}
	var originals := {}
	for variant: Dictionary in variants:
		for key: String in originals:
			_apply(targets, key, originals[key])
		for key: String in variant:
			if key == "name":
				continue
			if not originals.has(key):
				originals[key] = _read(targets, key)
			_apply(targets, key, _parse(key, variant[key]))
		for i in 4:
			await dev.get_tree().process_frame
		await dev.capture(String(variant["name"]))
	dev.get_tree().paused = false


func _read(targets: Dictionary, key: String) -> Variant:
	var parts := key.split(".", true, 1)
	var target: Object = targets[parts[0]]
	if target is ShaderMaterial:
		return (target as ShaderMaterial).get_shader_parameter(parts[1])
	return target.get(parts[1])


func _apply(targets: Dictionary, key: String, value: Variant) -> void:
	var parts := key.split(".", true, 1)
	var target: Object = targets[parts[0]]
	if target is ShaderMaterial:
		(target as ShaderMaterial).set_shader_parameter(parts[1], value)
	else:
		target.set(parts[1], value)


## JSON has no colors or vectors: a 3-element array becomes a Vector3 for transform
## keys (rotation, position) and a Color for everything else.
func _parse(key: String, value: Variant) -> Variant:
	if value is Array and (value as Array).size() == 3:
		if key.ends_with("rotation") or key.ends_with("position"):
			return Vector3(value[0], value[1], value[2])
		return Color(value[0], value[1], value[2])
	return value
