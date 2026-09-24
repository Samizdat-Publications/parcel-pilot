class_name Hoop
extends Area3D
## A delivery hoop. Only the active one is visible and armed; flying through it from
## either side emits `passed`. Its beam marks the destination from anywhere in the sky.
## While active it breathes; when its parcel arrives it pops and fades away.

signal passed

var active := false
var _time := 0.0
var _tween: Tween

@onready var model: Node3D = $Model
@onready var beam: Node3D = $Beam


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func set_active(on: bool) -> void:
	if _tween != null:
		_tween.kill()
	active = on
	visible = on
	scale = Vector3.ONE
	beam.visible = on
	set_deferred("monitoring", on)
	if on:
		scale = Vector3.ONE * 0.2
		_tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		_tween.tween_property(self, "scale", Vector3.ONE, 0.6)


## Delivered: stop listening, burst outward, then hide.
func retire() -> void:
	active = false
	set_deferred("monitoring", false)
	beam.visible = false
	if _tween != null:
		_tween.kill()
	_tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_tween.tween_property(self, "scale", Vector3.ONE * 1.6, 0.35)
	_tween.tween_callback(func() -> void:
		visible = false
		scale = Vector3.ONE)


func _process(delta: float) -> void:
	if active:
		_time += delta
		model.rotate_object_local(Vector3.FORWARD, delta * 0.6)
		model.scale = Vector3.ONE * (1.0 + 0.04 * sin(_time * 3.0))


func _on_body_entered(body: Node3D) -> void:
	if active and body is MailPlane:
		passed.emit()
