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
	for marker in find_children("FX_Light*", "", true, false):
		_add_lamp(marker as Node3D, 1.2, 7.0)
	for marker in find_children("FX_Beacon*", "", true, false):
		_add_lamp(marker as Node3D, 4.0, 32.0)
		(marker as Node3D).add_child(AmbientFx.beacon())
	for marker in find_children("FX_Smoke*", "", true, false):
		(marker as Node3D).add_child(AmbientFx.chimney_smoke())
	for marker in find_children("FX_Mist*", "", true, false):
		(marker as Node3D).add_child(AmbientFx.waterfall_mist())
	for marker in find_children("FX_Fire*", "", true, false):
		(marker as Node3D).add_child(AmbientFx.campfire())
	for flag in find_children("FLAG_*", "MeshInstance3D", true, false):
		AmbientFx.wave_flag(flag as MeshInstance3D)


func _add_lamp(marker: Node3D, energy: float, reach: float) -> void:
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.76, 0.46)
	light.light_energy = energy
	light.omni_range = reach
	light.shadow_enabled = false
	marker.add_child(light)


func set_delivery_active(active: bool) -> void:
	if hoop != null:
		hoop.set_active(active)


## The parcel just arrived here: the hoop pops and fades instead of vanishing.
func retire_delivery() -> void:
	if hoop != null:
		hoop.retire()


func delivery_position() -> Vector3:
	return hoop.global_position if hoop != null else global_position


func find_marker(marker_name: String) -> Node3D:
	return find_child(marker_name, true, false) as Node3D


func _on_hoop_passed() -> void:
	hoop_passed.emit(self)
