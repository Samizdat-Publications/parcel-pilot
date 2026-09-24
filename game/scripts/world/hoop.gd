class_name Hoop
extends Area3D
## A delivery hoop. Only the active one is visible and armed; flying through it from
## either side emits `passed`. Its beam marks the destination from anywhere in the sky.

signal passed

var active := false

@onready var model: Node3D = $Model
@onready var beam: Node3D = $Beam


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func set_active(on: bool) -> void:
	active = on
	visible = on
	set_deferred("monitoring", on)


func _process(delta: float) -> void:
	if active:
		model.rotate_object_local(Vector3.FORWARD, delta * 0.6)


func _on_body_entered(body: Node3D) -> void:
	if active and body is MailPlane:
		passed.emit()
