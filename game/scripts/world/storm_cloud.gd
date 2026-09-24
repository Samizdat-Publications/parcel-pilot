class_name StormCloud
extends Drifter
## A drifting thundercloud. It flashes its Blender-made BOLT_ mesh now and then, and
## flying into it zaps the plane, which counts as a crash.

signal zapped(where: Vector3)
signal flashed(where: Vector3)

const THUNDER := preload("res://assets/audio/thunder.wav")

var _bolts: Array[Node3D] = []
var _flash: OmniLight3D
var _thunder: AudioStreamPlayer3D
var _next_flash := 0.0
var _flash_left := 0.0

@onready var zone: Area3D = $Zone


func _ready() -> void:
	super._ready()
	zone.body_entered.connect(_on_body_entered)
	for node in find_children("BOLT_*", "", true, false):
		_bolts.append(node as Node3D)
		(node as Node3D).visible = false
	_flash = OmniLight3D.new()
	_flash.light_color = Color(0.85, 0.9, 1.0)
	_flash.omni_range = 70.0
	_flash.light_energy = 0.0
	add_child(_flash)
	_thunder = AudioStreamPlayer3D.new()
	_thunder.stream = THUNDER
	_thunder.bus = "SFX"
	_thunder.unit_size = 60.0
	_thunder.max_distance = 900.0
	_thunder.volume_db = 6.0
	_thunder.add_to_group("audio_players")
	add_child(_thunder)
	_next_flash = randf_range(1.5, 5.0)


func _process(delta: float) -> void:
	_next_flash -= delta
	if _next_flash <= 0.0:
		_next_flash = randf_range(2.5, 6.5)
		_flash_left = 0.18
		for bolt in _bolts:
			bolt.visible = true
			bolt.rotation.y = randf() * TAU
		_thunder.pitch_scale = randf_range(0.85, 1.1)
		_thunder.play()
		flashed.emit(global_position)
	if _flash_left > 0.0:
		_flash_left -= delta
		_flash.light_energy = 9.0 * clampf(_flash_left / 0.18, 0.0, 1.0)
		if _flash_left <= 0.0:
			for bolt in _bolts:
				bolt.visible = false


func _on_body_entered(body: Node3D) -> void:
	if body is MailPlane:
		(body as MailPlane).zap()
		zapped.emit(body.global_position)
