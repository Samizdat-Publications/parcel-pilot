class_name MailPlane
extends CharacterBody3D
## Arcade flight model. Each physics tick it asks `input_source` for controls as a
## Vector3(turn, climb, boost), each in [-1, 1], so the player and the autopilot drive
## exactly the same code. The body yaws and pitches; only the Model child banks.

signal crashed(impact: float)
signal fell

@export var tuning: FlightTuning = preload("res://data/flight.tres")

## Any object with get_controls(plane: MailPlane) -> Vector3.
var input_source: Object
var speed := 0.0
var yaw := 0.0
var pitch := 0.0
var bank := 0.0
var boost := 0.6
var boosting := false
var frozen := false
var out_of_bounds := false
var controls := Vector3.ZERO

var _crash_cooldown := 0.0
var _propeller: Node3D

@onready var model: Node3D = $Model


func _ready() -> void:
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	speed = tuning.cruise_speed
	yaw = global_basis.get_euler().y
	_propeller = model.find_child("SPIN_Propeller", true, false) as Node3D
	# The Blender model decides where the parcel rides (MK_Parcel socket).
	var parcel := model.get_node_or_null("Parcel") as Node3D
	var socket := model.find_child("MK_Parcel", true, false) as Node3D
	if parcel != null and socket != null:
		parcel.reparent(socket, false)
		parcel.transform = Transform3D.IDENTITY


func forward() -> Vector3:
	return -global_basis.z


func reset_to(xform: Transform3D) -> void:
	global_position = xform.origin
	yaw = xform.basis.get_euler().y
	pitch = 0.0
	bank = 0.0
	speed = tuning.cruise_speed
	boost = maxf(boost, 0.6)
	_apply_orientation()
	velocity = forward() * speed
	reset_physics_interpolation()


## Turn to face a point horizontally (used at spawn).
func face(point: Vector3) -> void:
	var to := point - global_position
	yaw = atan2(-to.x, -to.z)
	pitch = 0.0
	_apply_orientation()
	reset_physics_interpolation()


func add_boost(amount: float) -> void:
	boost = minf(1.0, boost + amount)


## Storm-cloud jolt: bleeds speed and counts as a crash (subject to the cooldown).
func zap() -> void:
	speed = maxf(tuning.min_speed, speed * 0.6)
	if _crash_cooldown <= 0.0:
		_crash_cooldown = tuning.crash_cooldown
		crashed.emit(0.7)


func speed_ratio() -> float:
	return clampf(inverse_lerp(tuning.cruise_speed, tuning.boost_speed, speed), 0.0, 1.0)


func _physics_process(delta: float) -> void:
	_spin_propeller(delta)
	if frozen:
		return
	var c := Vector3.ZERO
	if input_source != null:
		c = input_source.get_controls(self)
	c = _apply_limits(c)
	controls = c
	var turn := clampf(c.x, -1.0, 1.0)
	var climb := clampf(c.y, -1.0, 1.0)

	yaw = wrapf(yaw - turn * tuning.turn_rate * delta, -PI, PI)
	var max_pitch := deg_to_rad(tuning.max_pitch_deg)
	if absf(climb) > 0.05:
		pitch = clampf(pitch + climb * tuning.pitch_rate * delta, -max_pitch, max_pitch)
	else:
		pitch = lerpf(pitch, 0.0, 1.0 - exp(-tuning.auto_level * delta))
	var target_bank := -turn * deg_to_rad(tuning.max_bank_deg)
	bank = lerpf(bank, target_bank, 1.0 - exp(-tuning.bank_response * delta))

	boosting = c.z > 0.5 and boost > 0.01
	if boosting:
		boost = maxf(0.0, boost - tuning.boost_drain * delta)
	else:
		boost = minf(1.0, boost + tuning.boost_refill * delta)
	var target_speed := tuning.boost_speed if boosting else tuning.cruise_speed
	var slope := sin(pitch)
	target_speed -= slope * (tuning.climb_speed_loss if slope > 0.0 else tuning.dive_speed_gain)
	speed = lerpf(speed, target_speed, 1.0 - exp(-tuning.speed_response * delta))
	speed = maxf(speed, tuning.min_speed)

	_apply_orientation()
	velocity = forward() * speed
	var hit := move_and_collide(velocity * delta)
	if hit != null:
		_bounce(hit)
	_crash_cooldown = maxf(0.0, _crash_cooldown - delta)
	if global_position.y < tuning.floor_y:
		fell.emit()


func _apply_orientation() -> void:
	global_basis = Basis.from_euler(Vector3(pitch, yaw, 0.0))
	model.rotation = Vector3(0.0, 0.0, bank)


## Soft world limits: the nose is pushed down above the ceiling and the plane is
## steered home beyond the boundary. Everything stays flyable; nothing kills you.
func _apply_limits(c: Vector3) -> Vector3:
	var p := global_position
	if p.y > tuning.ceiling:
		c.y = minf(c.y, -0.8)
	out_of_bounds = Vector2(p.x, p.z).length() > tuning.boundary_radius
	if out_of_bounds:
		var home_yaw := atan2(p.x, p.z)
		var err := wrapf(home_yaw - yaw, -PI, PI)
		c.x = clampf(-err * 2.0, -1.0, 1.0)
	return c


func _bounce(hit: KinematicCollision3D) -> void:
	var n := hit.get_normal()
	var impact := clampf(-velocity.normalized().dot(n), 0.0, 1.0)
	var v := velocity.bounce(n) * tuning.crash_bounce
	v += n * tuning.min_speed * 0.5
	if v.length() < tuning.min_speed:
		v = v.normalized() * tuning.min_speed
	var dir := v.normalized()
	yaw = atan2(-dir.x, -dir.z)
	var max_pitch := deg_to_rad(tuning.max_pitch_deg)
	pitch = clampf(asin(clampf(dir.y, -1.0, 1.0)), -max_pitch, max_pitch)
	speed = maxf(v.length(), tuning.min_speed)
	global_position += n * 0.4
	_apply_orientation()
	if impact >= tuning.crash_min_impact and _crash_cooldown <= 0.0:
		_crash_cooldown = tuning.crash_cooldown
		crashed.emit(impact)


func _spin_propeller(delta: float) -> void:
	if _propeller != null:
		_propeller.rotate_object_local(Vector3.BACK, delta * (18.0 + speed * 1.2))
