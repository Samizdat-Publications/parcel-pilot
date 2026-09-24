class_name Popups
extends Control
## Floating callouts ("EXPRESS!", "+84", "+15s") that pop, rise and fade.


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func spawn(text: String, at: Vector2, size_px := 48, color := UiKit.CREAM, delay := 0.0,
		rise := 70.0, hold := 0.9) -> void:
	var l := UiKit.label(text, size_px, color)
	l.size = Vector2(900, size_px * 1.5)
	l.position = at - l.size * 0.5
	l.pivot_offset = l.size * 0.5
	l.modulate.a = 0.0
	add_child(l)
	var tw := l.create_tween()
	tw.tween_interval(delay)
	tw.tween_callback(func() -> void:
		l.modulate.a = 1.0
		l.scale = Vector2.ONE * 0.5)
	tw.tween_property(l, "scale", Vector2.ONE * 1.12, 0.16).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "scale", Vector2.ONE, 0.1)
	tw.tween_interval(hold)
	tw.tween_property(l, "position:y", l.position.y - rise, 0.5).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 0.5)
	tw.tween_callback(l.queue_free)
