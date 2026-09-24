class_name ResultsScreen
extends CanvasLayer
## End-of-shift summary.

var _lines: VBoxContainer


func _ready() -> void:
	layer = 10
	var root := UiKit.full_rect(Control.new())
	add_child(root)
	var shade := ColorRect.new()
	shade.color = Color(0.1, 0.07, 0.12, 0.45)
	UiKit.full_rect(shade)
	root.add_child(shade)
	_lines = VBoxContainer.new()
	_lines.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_lines.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_lines.grow_vertical = Control.GROW_DIRECTION_BOTH
	_lines.alignment = BoxContainer.ALIGNMENT_CENTER
	_lines.add_theme_constant_override("separation", 10)
	root.add_child(_lines)
	Game.shift_ended.connect(_on_shift_ended)


func _on_shift_ended(new_best: bool) -> void:
	for child in _lines.get_children():
		child.queue_free()
	_lines.add_child(UiKit.label("SHIFT OVER", 96, UiKit.CREAM))
	_lines.add_child(UiKit.label("%d points" % Game.score, 64, UiKit.GOLD))
	if new_best:
		_lines.add_child(UiKit.label("New best!", 40, UiKit.RED))
	_lines.add_child(UiKit.label("Rank: %s" % Game.rank(), 44))
	_lines.add_child(UiKit.label("%s delivered     %s     best combo x%.2f" % [
		_count(Game.deliveries, "parcel"), _count(Game.stamps, "stamp"),
		DeliveryRules.combo_multiplier(Game.best_streak, Game.rules)], 30, UiKit.PAPER))
	_lines.add_child(UiKit.label("Best shift: %d" % Save.best_score, 30, UiKit.PAPER))
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 40)
	_lines.add_child(spacer)
	_lines.add_child(UiKit.label("Space: fly again      Esc: title", 34))


static func _count(n: int, noun: String) -> String:
	return "%d %s%s" % [n, noun, "" if n == 1 else "s"]
