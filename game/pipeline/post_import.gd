@tool
extends EditorScenePostImport
## Runs on every Blender-built .glb at import time (wired in project.godot through
## [importer_defaults]). Blender stays the source of truth for geometry and palette
## colors; this only applies engine-side material settings, keyed by palette name.

## Palette materials that glow, and how strongly (emission energy multiplier).
const EMISSION_ENERGY := {
	"window": 2.2,
	"lamp": 4.0,
	"crystal": 3.0,
	"boost": 4.0,
	"beacon": 5.0,
	"bolt": 12.0,
	"nav_red": 3.0,
	"nav_green": 3.0,
	"gold": 0.25,
}
## Soft, matte, wrap-lit materials (cloud puffs read as volume instead of plastic).
const SOFT := ["cloud", "cloud_shade", "storm", "storm_dark"]


func _post_import(scene: Node) -> Object:
	_visit(scene)
	return scene


func _visit(node: Node) -> void:
	var mesh_instance := node as MeshInstance3D
	if mesh_instance != null and mesh_instance.mesh != null:
		for i in mesh_instance.mesh.get_surface_count():
			var mat := mesh_instance.mesh.surface_get_material(i) as StandardMaterial3D
			if mat != null:
				_tweak(mat)
		if mesh_instance.name.begins_with("BOLT_") or mesh_instance.name == "Roots":
			mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for child in node.get_children():
		_visit(child)


func _tweak(mat: StandardMaterial3D) -> void:
	var key := mat.resource_name
	if EMISSION_ENERGY.has(key):
		mat.emission_enabled = true
		mat.emission_energy_multiplier = EMISSION_ENERGY[key]
	if key in SOFT:
		mat.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
		mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
		mat.roughness = 1.0
		mat.rim_enabled = true
		mat.rim = 0.35
		mat.rim_tint = 0.6
	match key:
		"water":
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			mat.albedo_color.a = 0.82
			mat.roughness = 0.08
			mat.emission_enabled = true
			mat.emission = Color(0.25, 0.55, 0.62)
			mat.emission_energy_multiplier = 0.35
		"glass":
			mat.roughness = 0.05
			mat.metallic = 0.4
			mat.metallic_specular = 0.9
		"bolt":
			mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
