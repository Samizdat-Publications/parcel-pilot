class_name BoostRing
extends Area3D
## Flying through tops up the boost meter. A short cooldown stops double counting.

signal boosted(where: Vector3)

var _cooldown := 0.0

@onready var model: Node3D = $Model


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	_cooldown = maxf(0.0, _cooldown - delta)
	model.rotate_object_local(Vector3.FORWARD, delta * 1.5)


func _on_body_entered(body: Node3D) -> void:
	if body is MailPlane and _cooldown <= 0.0:
		_cooldown = 2.0
		(body as MailPlane).add_boost(Game.rules.ring_boost)
		boosted.emit(global_position)
