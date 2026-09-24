class_name Stamp
extends Area3D
## A collectible postage stamp: bobs and spins, pays out during a shift, then
## respawns after a while.

var _home := Vector3.ZERO
var _time := 0.0
var _hidden_for := 0.0

@onready var model: Node3D = $Model


func _ready() -> void:
	_home = position
	_time = randf() * TAU
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	if _hidden_for > 0.0:
		_hidden_for -= delta
		if _hidden_for <= 0.0:
			visible = true
			set_deferred("monitoring", true)
		return
	_time += delta
	model.rotation.y = _time * 1.8
	position = _home + Vector3.UP * sin(_time * 2.0) * 0.4


func _on_body_entered(body: Node3D) -> void:
	if body is MailPlane and visible and Game.is_playing():
		Game.collect_stamp(global_position)
		visible = false
		set_deferred("monitoring", false)
		_hidden_for = Game.rules.stamp_respawn
