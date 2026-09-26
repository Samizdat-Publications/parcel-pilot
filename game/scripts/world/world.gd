class_name World
extends Node3D
## The archipelago. Islands are instanced .glb files with island.gd attached, laid out
## in world.tscn; this script only answers questions about them.

const HUB_ID := "post_office"
## The Compatibility renderer (the web build) fogs and lights the cloud sea brighter than
## Forward+, so there the sea is deepened and the height fog dropped. Matched side by
## side against the desktop look with tools/lookdev.py.
const COMPAT_SEA_TOP := Color(0.68, 0.6, 0.72)
## In a browser every draw call is expensive and the sun's shadow cascades were over half
## of them, so the web build uses two cascades over a shorter range.
const COMPAT_SHADOW_DISTANCE := 300.0

@onready var _islands_root: Node3D = $Islands


func _ready() -> void:
	if RenderingServer.get_current_rendering_method() == "gl_compatibility":
		($Environment as WorldEnvironment).environment.fog_height_density = 0.0
		var sea := ($CloudSea as MeshInstance3D).mesh.surface_get_material(0) as ShaderMaterial
		sea.set_shader_parameter("top_color", COMPAT_SEA_TOP)
		sea.set_shader_parameter("backlight_strength", 0.0)
		var sun := $Sun as DirectionalLight3D
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
		sun.directional_shadow_max_distance = COMPAT_SHADOW_DISTANCE


func islands() -> Array[Island]:
	var out: Array[Island] = []
	for child in _islands_root.get_children():
		if child is Island:
			out.append(child)
	return out


func hub() -> Island:
	for island in islands():
		if island.island_id == HUB_ID:
			return island
	return islands()[0]


func spawn_transform() -> Transform3D:
	var marker := hub().find_marker("MK_Spawn")
	if marker != null:
		return marker.global_transform.orthonormalized()
	return Transform3D(Basis(), hub().global_position + Vector3(0.0, 30.0, 70.0))
