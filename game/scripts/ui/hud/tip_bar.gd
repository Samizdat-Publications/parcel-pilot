class_name TipBar
extends Control
## The draining tip meter: gold while the parcel is fresh, reddening as the tip falls.

var value := 1.0:
	set(v):
		value = clampf(v, 0.0, 1.0)
		queue_redraw()


func _ready() -> void:
	custom_minimum_size = Vector2(460, 16)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	var track := UiKit.box(Color(UiKit.INK, 0.28), Color(0, 0, 0, 0), 8, 0, false)
	draw_style_box(track, Rect2(Vector2.ZERO, size))
	if value <= 0.001:
		return
	var fill := UiKit.box(UiKit.RED.lerp(UiKit.GOLD, value), UiKit.INK, 8, 2, false)
	draw_style_box(fill, Rect2(Vector2.ZERO, Vector2(maxf(size.x * value, 16.0), size.y)))
