class_name PlaneFx
extends Node
## The plane's own effects, hung on its Blender sockets: exhaust puffs at FX_Exhaust,
## contrails from FX_WingTipL/R when boosting or turning hard, and the boost cue.

var plane: MailPlane
var _exhaust: CPUParticles3D
var _trails: Array[RibbonTrail] = []
var _was_boosting := false


func setup(p: MailPlane) -> void:
	plane = p
	var socket := plane.model.find_child("FX_Exhaust", true, false) as Node3D
	if socket != null:
		_exhaust = Fx.particles("puff", 26, 1.0, 0.7)
		_exhaust.direction = Vector3(0.35, -0.45, 1.0)
		_exhaust.spread = 14.0
		_exhaust.initial_velocity_min = 3.0
		_exhaust.initial_velocity_max = 5.0
		_exhaust.scale_amount_curve = Fx.grow_curve(0.3)
		_exhaust.color_ramp = Fx.fade_ramp(Color(0.8, 0.78, 0.8), 0.5)
		_exhaust.local_coords = false
		socket.add_child(_exhaust)
		_exhaust.emitting = true
	for tip in ["FX_WingTipL", "FX_WingTipR"]:
		var s := plane.model.find_child(tip, true, false) as Node3D
		if s != null:
			var trail := RibbonTrail.new()
			trail.emitter = s
			add_child(trail)
			_trails.append(trail)


## After a teleport (respawn, new shift) so the trails do not draw across the sky.
func reset() -> void:
	for t in _trails:
		t.reset()
		t.intensity = 0.0


func _process(_delta: float) -> void:
	if plane == null:
		return
	var hard_turn := absf(plane.bank) > deg_to_rad(30.0)
	var goal := 1.0 if plane.boosting else (0.5 if hard_turn else 0.0)
	for t in _trails:
		t.target = goal
	if _exhaust != null:
		_exhaust.speed_scale = 0.8 + plane.speed_ratio()
	if plane.boosting and not _was_boosting:
		Audio.play("boost", -5.0, 1.0, 0.05)
	_was_boosting = plane.boosting
