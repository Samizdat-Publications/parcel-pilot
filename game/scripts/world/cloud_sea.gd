class_name CloudSea
extends MeshInstance3D
## Keeps the cloud-sea mesh centered under the active camera, snapped to its own
## vertex spacing so the world-space displacement in cloud_sea.gdshader never swims.

@export var grid := 12.5


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		var p := cam.global_position
		global_position = Vector3(snappedf(p.x, grid), global_position.y, snappedf(p.z, grid))
