class_name PauseMenu
extends CanvasLayer
## Pause overlay. Runs while the tree is paused.

signal restart_requested
signal title_requested

var _first_button: Button
var _invert: CheckButton


func _ready() -> void:
	layer = 20
	process_mode = Node.PROCESS_MODE_ALWAYS
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var shade := ColorRect.new()
	shade.color = Color(0.08, 0.06, 0.1, 0.55)
	UiKit.full_rect(shade)
	root.add_child(shade)
	var box := VBoxContainer.new()
	box.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	box.add_theme_constant_override("separation", 14)
	root.add_child(box)
	box.add_child(UiKit.label("PAUSED", 88))
	_first_button = _button(box, "Resume", Game.resume)
	_button(box, "Restart shift", func() -> void: restart_requested.emit())
	_button(box, "Title screen", func() -> void: title_requested.emit())
	_invert = CheckButton.new()
	_invert.text = "Invert pitch"
	_invert.add_theme_font_size_override("font_size", 30)
	_invert.button_pressed = bool(Save.settings["invert_pitch"])
	_invert.toggled.connect(func(on: bool) -> void: Save.set_setting("invert_pitch", on))
	box.add_child(_invert)
	_button(box, "Quit", func() -> void: get_tree().quit())
	visibility_changed.connect(_on_visibility_changed)


func _button(parent: Control, text: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(380, 64)
	b.add_theme_font_size_override("font_size", 32)
	b.pressed.connect(action)
	parent.add_child(b)
	return b


func _on_visibility_changed() -> void:
	if visible:
		_invert.set_pressed_no_signal(bool(Save.settings["invert_pitch"]))
		_first_button.grab_focus.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		Game.resume()
