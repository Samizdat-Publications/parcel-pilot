class_name LogoView
extends SubViewportContainer
## Renders the Blender-built 3D logo in its own little world (transparent background),
## gently bobbing, for the title screen.

const LOGO := preload("res://assets/models/logo.glb")

var _logo: Node3D
var _time := 0.0


func _ready() -> void:
	stretch = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var vp := SubViewport.new()
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_4X
	add_child(vp)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.92, 0.84, 0.95)
	env.environment.ambient_light_energy = 0.55
	env.environment.tonemap_mode = Environment.TONE_MAPPER_AGX
	vp.add_child(env)
	var key := DirectionalLight3D.new()
	key.rotation = Vector3(-0.55, 0.45, 0.0)
	key.light_color = Color(1.0, 0.86, 0.68)
	key.light_energy = 1.7
	vp.add_child(key)
	var rim := DirectionalLight3D.new()
	rim.rotation = Vector3(-0.3, 2.6, 0.0)
	rim.light_color = Color(0.7, 0.72, 1.0)
	rim.light_energy = 0.7
	vp.add_child(rim)
	var cam := Camera3D.new()
	cam.position = Vector3(0.0, 0.0, 9.2)
	cam.fov = 36.0
	vp.add_child(cam)
	cam.current = true
	_logo = LOGO.instantiate()
	vp.add_child(_logo)


func _process(delta: float) -> void:
	_time += delta
	_logo.rotation = Vector3(sin(_time * 0.8) * 0.05, sin(_time * 0.55) * 0.2, sin(_time * 0.7) * 0.02)
	_logo.position.y = sin(_time * 1.3) * 0.12
