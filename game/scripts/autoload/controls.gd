extends Node
## Registers the input map in code so every binding is readable and diffable.
## Letter keys use physical keycodes, so WASD sits in the same place on any layout.

const DEADZONE := 0.2


func _enter_tree() -> void:
	_bind("turn_left", [KEY_A, KEY_LEFT], [], [[JOY_AXIS_LEFT_X, -1.0]])
	_bind("turn_right", [KEY_D, KEY_RIGHT], [], [[JOY_AXIS_LEFT_X, 1.0]])
	_bind("climb", [KEY_W, KEY_UP], [], [[JOY_AXIS_LEFT_Y, -1.0]])
	_bind("dive", [KEY_S, KEY_DOWN], [], [[JOY_AXIS_LEFT_Y, 1.0]])
	_bind("boost", [KEY_SHIFT, KEY_SPACE], [JOY_BUTTON_A], [[JOY_AXIS_TRIGGER_RIGHT, 1.0]])
	_bind("pause", [KEY_ESCAPE, KEY_P], [JOY_BUTTON_START], [])
	_bind("confirm", [KEY_ENTER, KEY_KP_ENTER, KEY_SPACE], [JOY_BUTTON_A], [])
	_bind("back", [KEY_ESCAPE, KEY_BACKSPACE], [JOY_BUTTON_B], [])
	_bind("restart", [KEY_R], [JOY_BUTTON_Y], [])


func _bind(action: StringName, keys: Array, buttons: Array, axes: Array) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, DEADZONE)
	for key in keys:
		var ev := InputEventKey.new()
		ev.physical_keycode = key
		InputMap.action_add_event(action, ev)
	for button in buttons:
		var jb := InputEventJoypadButton.new()
		jb.button_index = button
		InputMap.action_add_event(action, jb)
	for axis in axes:
		var jm := InputEventJoypadMotion.new()
		jm.axis = axis[0]
		jm.axis_value = axis[1]
		InputMap.action_add_event(action, jm)
