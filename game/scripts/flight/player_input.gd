class_name PlayerInput
extends RefCounted
## Keyboard and gamepad controls for the plane.

var invert_pitch := false


func get_controls(_plane: MailPlane) -> Vector3:
	var turn := Input.get_axis("turn_left", "turn_right")
	var climb := Input.get_axis("dive", "climb")
	if invert_pitch:
		climb = -climb
	var boost := 1.0 if Input.is_action_pressed("boost") else 0.0
	return Vector3(turn, climb, boost)
