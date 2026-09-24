class_name StormCloud
extends Drifter
## A drifting thundercloud. Flying into it zaps the plane, which counts as a crash.

signal zapped(where: Vector3)

@onready var zone: Area3D = $Zone


func _ready() -> void:
	super._ready()
	zone.body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node3D) -> void:
	if body is MailPlane:
		(body as MailPlane).zap()
		zapped.emit(body.global_position)
