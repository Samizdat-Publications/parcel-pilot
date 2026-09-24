class_name Spinner
extends Node
## Spins a SPIN_* part from a Blender model around its local forward axis
## (Blender +Y, Godot -Z).

const SPEEDS := {"Sails": 0.9, "Propeller": 30.0, "Fan": 4.0, "Beacon": 1.2, "Vane": 0.4, "Orrery": 0.6}

var target: Node3D
var speed := 1.0


static func speed_for(part_name: String) -> float:
	for key: String in SPEEDS:
		if part_name.contains(key):
			return SPEEDS[key]
	return 1.0


func _process(delta: float) -> void:
	if target != null:
		target.rotate_object_local(Vector3.FORWARD, speed * delta)
