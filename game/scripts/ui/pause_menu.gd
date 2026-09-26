class_name PauseMenu
extends CanvasLayer
## Pause card: resume, restart, title, quit, plus volume sliders and toggles.
## Runs while the tree is paused.

signal restart_requested
signal title_requested

var _first_button: Button
var _invert: CheckButton
var _fullscreen: CheckButton
var _music: HSlider
var _sfx: HSlider


func _ready() -> void:
	layer = 20
	process_mode = Node.PROCESS_MODE_ALWAYS
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.theme = UiKit.theme()
	add_child(root)
	var shade := UiKit.full_rect(ColorRect.new()) as ColorRect
	shade.color = Color(0.13, 0.09, 0.15, 0.55)
	root.add_child(shade)

	var card := UiKit.panel(UiKit.PAPER, 24, Vector2(40, 24))
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	card.grow_vertical = Control.GROW_DIRECTION_BOTH
	card.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	card.add_child(box)
	box.add_child(UiKit.ink("PAUSED", 64, UiKit.INK, HORIZONTAL_ALIGNMENT_CENTER, 800))
	_first_button = _button(box, "Resume", Game.resume)
	_button(box, "Restart shift", func() -> void: restart_requested.emit())
	_button(box, "Title screen", func() -> void: title_requested.emit())
	if not OS.has_feature("web"):
		# A browser tab cannot quit itself.
		_button(box, "Quit", func() -> void: get_tree().quit())

	var sep := HSeparator.new()
	sep.add_theme_constant_override("separation", 14)
	box.add_child(sep)
	_music = _slider(box, "Music", "music_volume")
	_sfx = _slider(box, "Sound", "sfx_volume")
	_invert = _toggle(box, "Invert pitch", "invert_pitch")
	_fullscreen = _toggle(box, "Fullscreen", "fullscreen")
	_fullscreen.toggled.connect(func(on: bool) -> void:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if on else DisplayServer.WINDOW_MODE_WINDOWED))
	visibility_changed.connect(_on_visibility_changed)


func _button(parent: Control, text: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(420, 60)
	b.pressed.connect(func() -> void:
		Audio.play("ui_click")
		action.call())
	b.focus_entered.connect(func() -> void: Audio.play("ui_move"))
	parent.add_child(b)
	return b


func _slider(parent: Control, text: String, key: String) -> HSlider:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	parent.add_child(row)
	var l := UiKit.ink(text, 26, UiKit.INK, HORIZONTAL_ALIGNMENT_LEFT, 700)
	l.custom_minimum_size = Vector2(120, 0)
	row.add_child(l)
	var s := HSlider.new()
	s.min_value = 0.0
	s.max_value = 1.0
	s.step = 0.05
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	s.value = float(Save.settings[key])
	s.value_changed.connect(func(v: float) -> void: Save.set_setting(key, v))
	s.focus_entered.connect(func() -> void: Audio.play("ui_move"))
	row.add_child(s)
	return s


func _toggle(parent: Control, text: String, key: String) -> CheckButton:
	var c := CheckButton.new()
	c.text = text
	c.add_theme_font_size_override("font_size", 26)
	c.button_pressed = bool(Save.settings[key])
	c.toggled.connect(func(on: bool) -> void:
		Audio.play("ui_click")
		Save.set_setting(key, on))
	c.focus_entered.connect(func() -> void: Audio.play("ui_move"))
	parent.add_child(c)
	return c


func _on_visibility_changed() -> void:
	if visible:
		_invert.set_pressed_no_signal(bool(Save.settings["invert_pitch"]))
		_fullscreen.set_pressed_no_signal(bool(Save.settings["fullscreen"]))
		_music.set_value_no_signal(float(Save.settings["music_volume"]))
		_sfx.set_value_no_signal(float(Save.settings["sfx_volume"]))
		_first_button.grab_focus.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		Game.resume()
