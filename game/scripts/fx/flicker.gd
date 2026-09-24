extends OmniLight3D
## Firelight: energy wanders on layered noise.

@export var base_energy := 1.6

var _noise := FastNoiseLite.new()
var _time := 0.0


func _ready() -> void:
	_noise.frequency = 3.0
	_noise.seed = randi()


func _process(delta: float) -> void:
	_time += delta
	light_energy = base_energy * (0.75 + 0.35 * _noise.get_noise_1d(_time * 12.0) + 0.1 * sin(_time * 23.0))
