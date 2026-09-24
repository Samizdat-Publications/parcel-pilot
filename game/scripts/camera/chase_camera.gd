class_name ChaseCamera
extends Camera3D
## Third-person chase camera. Runs per rendered frame on the plane's interpolated
## transform (physics runs at 60 Hz), follows with exponential smoothing, looks ahead,
## widens FOV with speed, rolls a little with the bank, and shakes on trauma.

@export var distance := 11.5
@export var height := 3.4
@export var look_ahead := 16.0
@export var follow_sharpness := 7.0
@export var base_fov := 70.0
@export var boost_fov := 86.0
@export var roll_follow := 0.3
@export var shake_max_angle := 0.06
@export var shake_max_offset := 0.6
@export var trauma_decay := 1.3

var target: MailPlane
var trauma := 0.0
var _fov_kick := 0.0

var _noise := FastNoiseLite.new()
var _time := 0.0


func _ready() -> void:
	top_level = true
	physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_OFF
	_noise.frequency = 2.2
	fov = base_fov


func add_trauma(amount: float) -> void:
	trauma = clampf(trauma + amount, 0.0, 1.0)


## A brief widening of the view (deliveries, boost rings) that eases back.
func kick_fov(degrees: float) -> void:
	_fov_kick = minf(_fov_kick + degrees, 14.0)


## Jump straight to the resting position (after spawns and respawns).
func snap() -> void:
	if target == null:
		return
	var xf := target.global_transform
	global_position = _desired_position(xf)
	_look(xf, 0.0)


func _process(delta: float) -> void:
	if target == null:
		return
	_time += delta
	var xf := target.get_global_transform_interpolated()
	var desired := _desired_position(xf)
	global_position = global_position.lerp(desired, 1.0 - exp(-follow_sharpness * delta))
	_avoid_terrain(xf.origin)
	_look(xf, delta)
	_fov_kick = move_toward(_fov_kick, 0.0, delta * 12.0)
	var fov_goal := lerpf(base_fov, boost_fov, target.speed_ratio()) + _fov_kick
	fov = lerpf(fov, fov_goal, 1.0 - exp(-3.0 * delta))
	trauma = maxf(0.0, trauma - trauma_decay * delta)


func _desired_position(xf: Transform3D) -> Vector3:
	var fwd := -xf.basis.z
	var flat := Vector3(fwd.x, 0.0, fwd.z)
	flat = flat.normalized() if flat.length() > 0.01 else Vector3.FORWARD
	var back := (fwd * 0.55 + flat * 0.45).normalized()
	return xf.origin - back * distance + Vector3.UP * height


func _look(xf: Transform3D, _delta: float) -> void:
	var fwd := -xf.basis.z
	var up := Vector3.UP.rotated(-fwd.normalized(), target.bank * roll_follow)
	var aim := xf.origin + fwd * look_ahead
	if global_position.distance_to(aim) < 0.1:
		return
	look_at(aim, up)
	if trauma > 0.0:
		var shake := trauma * trauma
		rotate_object_local(Vector3.RIGHT, shake_max_angle * shake * _noise.get_noise_2d(_time * 60.0, 1.0))
		rotate_object_local(Vector3.UP, shake_max_angle * shake * _noise.get_noise_2d(_time * 60.0, 2.0))
		rotate_object_local(Vector3.BACK, shake_max_angle * shake * _noise.get_noise_2d(_time * 60.0, 3.0))
		global_position += global_basis.x * shake_max_offset * shake * _noise.get_noise_2d(_time * 60.0, 4.0)


## Keep the camera from sinking into cliffs behind the plane.
func _avoid_terrain(plane_pos: Vector3) -> void:
	var space := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(plane_pos, global_position, 1, [target.get_rid()])
	var hit := space.intersect_ray(query)
	if not hit.is_empty():
		global_position = (hit["position"] as Vector3) + (hit["normal"] as Vector3) * 0.6
