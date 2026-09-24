class_name ParcelDrop
extends Node3D
## The delivery moment: a parcel on a striped parachute pops out of the hoop and
## drifts down onto the island, swaying, then shrinks away.

const CHUTE := preload("res://assets/models/parcel_chute.glb")

var _time := 0.0


static func spawn(parent: Node, at: Vector3) -> void:
	var drop := ParcelDrop.new()
	drop.position = at
	parent.add_child(drop)


func _ready() -> void:
	add_child(CHUTE.instantiate())
	scale = Vector3.ONE * 0.15
	var tw := create_tween()
	tw.tween_property(self, "scale", Vector3.ONE * 0.75, 0.45).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(self, "position:y", position.y - 11.0, 4.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(self, "scale", Vector3.ZERO, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_callback(queue_free)
	Audio.play("parachute", -4.0, 1.0, 0.08)


func _process(delta: float) -> void:
	_time += delta
	rotation = Vector3(sin(_time * 1.3) * 0.1, _time * 0.4, cos(_time * 1.1) * 0.1)
