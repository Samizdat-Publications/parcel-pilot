@tool
extends EditorScenePostImport
## Runs on every Blender-built .glb at import time (wired in project.godot through
## [importer_defaults]). Blender stays the source of truth for geometry and palette
## colors; this only applies engine-side material settings, keyed by palette name.

## Palette materials that glow, and how strongly (emission energy multiplier).
const EMISSION_ENERGY := {
	"window": 2.5,
	"lamp": 5.0,
	"crystal": 3.0,
	"boost": 4.0,
	"beacon": 5.0,
	"gold": 0.35,
}


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
	for child in node.get_children():
		_visit(child)


func _tweak(mat: StandardMaterial3D) -> void:
	var key := mat.resource_name
	if EMISSION_ENERGY.has(key):
		mat.emission_enabled = true
		mat.emission_energy_multiplier = EMISSION_ENERGY[key]
