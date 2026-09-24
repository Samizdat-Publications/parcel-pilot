class_name TitleScreen
extends CanvasLayer
## Title card over the attract-mode flight: the 3D logo, a pulsing start prompt,
## the best shift, and a controls card.

var _prompt: PanelContainer
var _best: PanelContainer
var _best_label: Label
var _time := 0.0


func _ready() -> void:
	layer = 10
	var root := UiKit.full_rect(Control.new())
	root.theme = UiKit.theme()
	add_child(root)

	var shade := TextureRect.new()
	var grad := Gradient.new()
	grad.set_color(0, Color(UiKit.INK, 0.45))
	grad.set_color(1, Color(UiKit.INK, 0.0))
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill_from = Vector2(0.5, 0.0)
	tex.fill_to = Vector2(0.5, 1.0)
	shade.texture = tex
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	shade.offset_bottom = 560
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(shade)

	var logo := LogoView.new()
	logo.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	logo.offset_left = -620
	logo.offset_right = 620
	logo.offset_top = 10
	logo.offset_bottom = 470
	root.add_child(logo)

	var tagline := UiKit.label("special delivery, by air", 40, UiKit.GOLD, HORIZONTAL_ALIGNMENT_CENTER, 10, 700)
	tagline.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	tagline.offset_top = 440
	tagline.grow_horizontal = Control.GROW_DIRECTION_BOTH
	root.add_child(tagline)

	_prompt = UiKit.pill()
	_prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_prompt.offset_top = 130
	_prompt.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_prompt.add_child(UiKit.label("Press SPACE to start your shift", 40, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 700))
	root.add_child(_prompt)

	_best = UiKit.pill(Color(UiKit.RED, 0.92))
	_best.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_best.offset_top = 220
	_best.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_best_label = UiKit.label("", 30, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 700)
	_best.add_child(_best_label)
	root.add_child(_best)

	var card := UiKit.panel(UiKit.PAPER, 18, Vector2(26, 12))
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	card.offset_bottom = -32
	card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	card.grow_vertical = Control.GROW_DIRECTION_BEGIN
	root.add_child(card)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 34)
	card.add_child(row)
	for entry in [[["W", "S"], "climb, dive"], [["A", "D"], "turn"], [["SHIFT"], "boost"], [["ESC"], "pause"]]:
		row.add_child(_control_hint(entry[0], entry[1]))

	visibility_changed.connect(_refresh)
	_refresh()


func _control_hint(keys: Array, action: String) -> HBoxContainer:
	var box := HBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	for key: String in keys:
		var cap := PanelContainer.new()
		cap.add_theme_stylebox_override("panel", UiKit.box(UiKit.CREAM, UiKit.INK, 8, 3, false, Vector2(10, 2)))
		cap.add_child(UiKit.ink(key, 22, UiKit.INK, HORIZONTAL_ALIGNMENT_CENTER, 800))
		box.add_child(cap)
	var l := UiKit.ink(action, 24, Color(UiKit.INK, 0.8), HORIZONTAL_ALIGNMENT_LEFT, 600)
	box.add_child(l)
	return box


func _refresh() -> void:
	_best.visible = Save.best_score > 0
	_best_label.text = "Best shift  %d" % Save.best_score


func _process(delta: float) -> void:
	if not visible:
		return
	_time += delta
	_prompt.modulate.a = 0.65 + 0.35 * sin(_time * 3.2)
