class_name RibbonTrail
extends MeshInstance3D
## A fading ribbon streaming from a moving point (wingtip contrails). Rebuilt every
## frame from the emitter's recent positions, turned to face the camera.

@export var points := 14
@export var width := 0.16
@export var color := Color(1.0, 1.0, 1.0, 0.5)
@export var min_step := 0.6

var emitter: Node3D
## 0..1, how visible the trail is; eased toward `target`.
var intensity := 0.0
var target := 0.0

var _history: Array[Vector3] = []
var _mesh := ImmediateMesh.new()


func _ready() -> void:
	top_level = true
	global_transform = Transform3D.IDENTITY
	mesh = _mesh
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.vertex_color_use_as_albedo = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	material_override = m


func reset() -> void:
	_history.clear()


func _process(delta: float) -> void:
	intensity = move_toward(intensity, target, delta * 2.5)
	if emitter == null:
		return
	var p := emitter.global_position
	if _history.is_empty() or _history[0].distance_to(p) > min_step:
		_history.push_front(p)
		if _history.size() > points:
			_history.pop_back()
	else:
		_history[0] = p
	_mesh.clear_surfaces()
	if intensity <= 0.01 or _history.size() < 3:
		return
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	_mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	var n := _history.size()
	for i in n:
		var a := _history[maxi(i - 1, 0)]
		var b := _history[mini(i + 1, n - 1)]
		var dir := (b - a).normalized()
		var to_cam := (cam.global_position - _history[i]).normalized()
		var side := dir.cross(to_cam).normalized()
		var t := 1.0 - float(i) / float(n - 1)
		var w := width * t
		var c := Color(color, color.a * intensity * t * t)
		_mesh.surface_set_color(c)
		_mesh.surface_add_vertex(_history[i] + side * w)
		_mesh.surface_set_color(c)
		_mesh.surface_add_vertex(_history[i] - side * w)
	_mesh.surface_end()
