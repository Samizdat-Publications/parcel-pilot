class_name Flock
extends Node3D
## A few gulls circling a point, bobbing, and flapping their Blender-built wings
## (the WingL / WingR children of bird.glb).

const BIRD := preload("res://assets/models/bird.glb")

@export var count := 7
@export var radius := 26.0
@export var speed := 0.3
@export var spread := 5.0

var _birds: Array[Dictionary] = []
var _time := 0.0


func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(String(name))
	for i in count:
		var bird: Node3D = BIRD.instantiate()
		add_child(bird)
		bird.scale = Vector3.ONE * rng.randf_range(0.9, 1.3)
		_birds.append({
			"node": bird,
			"phase": i * 0.24 + rng.randf() * 0.1,
			"r": radius + rng.randf_range(-spread, spread),
			"h": rng.randf_range(-2.5, 2.5),
			"flap": rng.randf() * TAU,
			"wl": bird.find_child("WingL", true, false),
			"wr": bird.find_child("WingR", true, false),
		})


func _process(delta: float) -> void:
	_time += delta
	for b in _birds:
		var a: float = _time * speed + b["phase"]
		var local := Vector3(cos(a) * b["r"], b["h"] + sin(_time * 0.7 + b["phase"] * 3.0) * 1.2, sin(a) * b["r"])
		var ahead := local + Vector3(-sin(a), 0.0, cos(a)) * signf(speed)
		var node: Node3D = b["node"]
		node.position = local
		node.look_at(to_global(ahead), Vector3.UP)
		var flap := sin(_time * 9.0 + b["flap"]) * 0.55
		if b["wl"] != null:
			(b["wl"] as Node3D).rotation.z = -flap
		if b["wr"] != null:
			(b["wr"] as Node3D).rotation.z = flap
