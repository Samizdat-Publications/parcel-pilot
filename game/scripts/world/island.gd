class_name Island
extends Node3D
## Attached to an instanced island .glb in world.tscn. Reads the Blender node contract:
## MK_Delivery gets a hoop, MK_Stamp* get stamps, SPIN_* parts get spinners.

signal hoop_passed(island: Island)

const HOOP_SCENE := preload("res://scenes/actors/hoop.tscn")
const STAMP_SCENE := preload("res://scenes/actors/stamp.tscn")

@export var island_id := ""
@export var display_name := ""
@export var is_destination := true

var hoop: Hoop


func _ready() -> void:
	# Children get their local transform before add_child, because their _ready
	# may record where they start.
	var to_local_xf := global_transform.affine_inverse()
	var socket := find_child("MK_Delivery", true, false) as Node3D
	if is_destination and socket != null:
		hoop = HOOP_SCENE.instantiate()
		hoop.transform = (to_local_xf * socket.global_transform).orthonormalized()
		add_child(hoop)
		hoop.passed.connect(_on_hoop_passed)
		hoop.set_active(false)
	for marker in find_children("MK_Stamp*", "", true, false):
		var stamp: Node3D = STAMP_SCENE.instantiate()
		stamp.position = to_local_xf * (marker as Node3D).global_position
		add_child(stamp)
	for part in find_children("SPIN_*", "", true, false):
		var spinner := Spinner.new()
		spinner.target = part as Node3D
		spinner.speed = Spinner.speed_for(part.name)
		add_child(spinner)


func set_delivery_active(active: bool) -> void:
	if hoop != null:
		hoop.set_active(active)


func delivery_position() -> Vector3:
	return hoop.global_position if hoop != null else global_position


func find_marker(marker_name: String) -> Node3D:
	return find_child(marker_name, true, false) as Node3D


func _on_hoop_passed() -> void:
	hoop_passed.emit(self)
