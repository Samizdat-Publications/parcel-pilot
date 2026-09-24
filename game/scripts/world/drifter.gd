class_name Drifter
extends Node3D
## Slowly circles its starting point and bobs up and down. Used for clouds, balloons
## and storm clouds so the sky never sits perfectly still.

@export var orbit_radius := 0.0
@export var orbit_speed := 0.02
@export var bob_height := 1.5
@export var bob_speed := 0.35
@export var face_travel := false

var _center := Vector3.ZERO
var _phase := 0.0


func _ready() -> void:
	_center = position
	_phase = fposmod(position.x * 0.013 + position.z * 0.007, TAU)


func _physics_process(delta: float) -> void:
	_phase += delta
	var angle := _phase * orbit_speed
	var offset := Vector3(cos(angle), 0.0, sin(angle)) * orbit_radius - Vector3(orbit_radius, 0.0, 0.0)
	offset.y = sin(_phase * bob_speed) * bob_height
	position = _center + offset
	if face_travel and orbit_radius > 0.0:
		rotation.y = -angle
