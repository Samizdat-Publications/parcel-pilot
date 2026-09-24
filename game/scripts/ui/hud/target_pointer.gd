class_name TargetPointer
extends Control
## Points at the destination hoop: a pulsing diamond over it when it is on screen, an
## arrow on the screen edge when it is not. Shows the distance either way.

var on_screen := false
var angle := 0.0
var distance := 0.0
var _time := 0.0
var _label: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label = UiKit.label("", 24, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 6)
	_label.size = Vector2(160, 30)
	add_child(_label)


func _process(delta: float) -> void:
	_time += delta
	_label.text = "%d m" % roundi(distance)
	if on_screen:
		_label.position = Vector2(-80, -64)
	else:
		_label.position = Vector2(-80, 0) - Vector2.from_angle(angle) * 52.0 - Vector2(0, 15)
	queue_redraw()


func _draw() -> void:
	if on_screen:
		var s := 15.0
		var diamond := PackedVector2Array([Vector2(0, -s), Vector2(s, 0), Vector2(0, s), Vector2(-s, 0)])
		var ring := fmod(_time * 1.2, 1.0)
		draw_arc(Vector2.ZERO, 20.0 + ring * 14.0, 0.0, TAU, 32, Color(UiKit.GOLD, 1.0 - ring), 3.0, true)
		draw_colored_polygon(diamond, UiKit.GOLD)
		draw_polyline(diamond + PackedVector2Array([diamond[0]]), UiKit.INK, 3.0, true)
		return
	var arrow := PackedVector2Array([Vector2(30, 0), Vector2(-12, -22), Vector2(-3, 0), Vector2(-12, 22)])
	var rotated := PackedVector2Array()
	for p in arrow:
		rotated.append(p.rotated(angle))
	draw_colored_polygon(rotated, UiKit.GOLD)
	draw_polyline(rotated + PackedVector2Array([rotated[0]]), UiKit.INK, 4.0, true)
