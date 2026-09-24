extends Node3D
## Turns the lighthouse beam around the vertical axis.

@export var speed := 0.9


func _process(delta: float) -> void:
	rotate_y(speed * delta)
