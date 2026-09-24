class_name World
extends Node3D
## The archipelago. Islands are instanced .glb files with island.gd attached, laid out
## in world.tscn; this script only answers questions about them.

const HUB_ID := "post_office"

@onready var _islands_root: Node3D = $Islands


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
