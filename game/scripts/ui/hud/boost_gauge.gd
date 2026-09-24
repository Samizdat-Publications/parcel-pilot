class_name BoostGauge
extends Control
## A round boost gauge: an arc that fills with the meter and glows while boosting.

var value := 0.0:
	set(v):
		value = clampf(v, 0.0, 1.0)
		queue_redraw()
var active := false:
	set(v):
		active = v
		queue_redraw()


func _ready() -> void:
	custom_minimum_size = Vector2(128, 128)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var caption := UiKit.label("BOOST", 22, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0)
	UiKit.full_rect(caption)
	add_child(caption)


func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5 - 4.0
	draw_circle(c, r, Color(UiKit.INK, 0.82))
	draw_arc(c, r - 12.0, 0.0, TAU, 64, Color(UiKit.CREAM, 0.14), 11.0, true)
	if value > 0.001:
		var color := UiKit.CREAM if active else UiKit.SKY
		draw_arc(c, r - 12.0, -PI * 0.5, -PI * 0.5 + TAU * value, 64, color, 11.0, true)
	draw_arc(c, r, 0.0, TAU, 64, Color(UiKit.CREAM, 0.35), 2.0, true)
