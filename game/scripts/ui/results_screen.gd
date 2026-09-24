class_name ResultsScreen
extends CanvasLayer
## End-of-shift report: the score counts up, stats reveal one by one, the rank lands
## like a rubber stamp, and a new best gets a ribbon.

signal fly_again_requested
signal title_requested
signal rank_stamped

var _card: PanelContainer
var _score: Label
var _rows: VBoxContainer
var _stamp: PanelContainer
var _stamp_label: Label
var _ribbon: PanelContainer
var _buttons: HBoxContainer
var _fly: Button
var _tween: Tween


func _ready() -> void:
	layer = 10
	var root := UiKit.full_rect(Control.new())
	root.theme = UiKit.theme()
	add_child(root)
	var shade := UiKit.full_rect(ColorRect.new()) as ColorRect
	shade.color = Color(0.13, 0.09, 0.15, 0.5)
	root.add_child(shade)

	_card = UiKit.panel(UiKit.PAPER, 24, Vector2(44, 26))
	_card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_card.grow_vertical = Control.GROW_DIRECTION_BOTH
	_card.custom_minimum_size = Vector2(760, 0)
	root.add_child(_card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	_card.add_child(box)

	var header := UiKit.panel(UiKit.RED, 14, Vector2(20, 6))
	header.add_child(UiKit.label("SHIFT REPORT", 40, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 800))
	box.add_child(header)
	_score = UiKit.ink("0", 110, UiKit.INK, HORIZONTAL_ALIGNMENT_CENTER, 800)
	box.add_child(_score)
	box.add_child(UiKit.ink("points", 26, Color(UiKit.INK, 0.6), HORIZONTAL_ALIGNMENT_CENTER, 600))
	_rows = VBoxContainer.new()
	_rows.add_theme_constant_override("separation", 4)
	box.add_child(_rows)

	var badges := HBoxContainer.new()
	badges.alignment = BoxContainer.ALIGNMENT_CENTER
	badges.add_theme_constant_override("separation", 26)
	badges.custom_minimum_size = Vector2(0, 110)
	box.add_child(badges)
	_stamp = PanelContainer.new()
	var stamp_box := UiKit.box(Color(0, 0, 0, 0), UiKit.RED, 12, 6, false, Vector2(22, 6))
	stamp_box.draw_center = false
	_stamp.add_theme_stylebox_override("panel", stamp_box)
	_stamp_label = UiKit.ink("", 46, UiKit.RED, HORIZONTAL_ALIGNMENT_CENTER, 800)
	_stamp.add_child(_stamp_label)
	badges.add_child(_stamp)
	_ribbon = UiKit.pill(UiKit.GOLD)
	_ribbon.add_child(UiKit.ink("NEW BEST!", 34, UiKit.INK, HORIZONTAL_ALIGNMENT_CENTER, 800))
	badges.add_child(_ribbon)

	_buttons = HBoxContainer.new()
	_buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	_buttons.add_theme_constant_override("separation", 20)
	box.add_child(_buttons)
	_fly = _button("Fly again", func() -> void: fly_again_requested.emit())
	_button("Title screen", func() -> void: title_requested.emit())
	Game.shift_ended.connect(_on_shift_ended)


func _button(text: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(260, 64)
	b.pressed.connect(func() -> void:
		Audio.play("ui_click")
		action.call())
	b.focus_entered.connect(func() -> void: Audio.play("ui_move"))
	_buttons.add_child(b)
	return b


func _row(label: String, value: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	var l := UiKit.ink(label, 28, Color(UiKit.INK, 0.8), HORIZONTAL_ALIGNMENT_LEFT, 600)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	row.add_child(UiKit.ink(value, 30, UiKit.INK, HORIZONTAL_ALIGNMENT_RIGHT, 800))
	return row


func _on_shift_ended(new_best: bool) -> void:
	for child in _rows.get_children():
		child.queue_free()
	var stats := [
		["Parcels delivered", str(Game.deliveries)],
		["Stamps collected", str(Game.stamps)],
		["Best combo", "x%.2f" % DeliveryRules.combo_multiplier(Game.best_streak, Game.rules)],
		["Crashes", str(Game.crashes)],
		["Time flown", UiKit.format_clock(Game.shift_time)],
	]
	var rows: Array[Control] = []
	for s in stats:
		var r := _row(s[0], s[1])
		r.modulate.a = 0.0
		_rows.add_child(r)
		rows.append(r)
	_stamp_label.text = Game.rank().to_upper()
	_stamp.modulate.a = 0.0
	_ribbon.modulate.a = 0.0
	_buttons.modulate.a = 0.0
	_score.text = "0"

	if _tween != null:
		_tween.kill()
	_card.pivot_offset = _card.size * 0.5
	_card.scale = Vector2.ONE * 0.85
	_card.modulate.a = 0.0
	_tween = create_tween()
	_tween.tween_property(_card, "modulate:a", 1.0, 0.25)
	_tween.parallel().tween_property(_card, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_tween.tween_method(func(v: float) -> void: _score.text = str(roundi(v)), 0.0, float(Game.score), 0.8) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	for r in rows:
		_tween.tween_property(r, "modulate:a", 1.0, 0.08)
	_tween.tween_callback(func() -> void:
		_stamp.modulate.a = 1.0
		_stamp.pivot_offset = _stamp.size * 0.5
		_stamp.rotation = -0.14
		_stamp.scale = Vector2.ONE * 2.2
		rank_stamped.emit())
	_tween.tween_property(_stamp, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	if new_best:
		_tween.tween_callback(func() -> void:
			_ribbon.modulate.a = 1.0
			UiKit.pop(_ribbon, 0.3, 0.4))
	_tween.tween_interval(0.25)
	_tween.tween_property(_buttons, "modulate:a", 1.0, 0.2)
	_tween.tween_callback(func() -> void: _fly.grab_focus())
