extends RefCounted
## Integration test (headless): real key events, through the input map defined in
## controls.gd, drive the menus and the plane. The bot bypasses the keyboard, so this
## is what proves a player's keys work.


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	var plane: MailPlane = main.plane
	await dev.wait(0.5)
	await _tap(dev, KEY_ENTER)
	dev.check(Game.state == Game.State.COUNTDOWN, "Enter starts a shift from the title")
	dev.check(plane.input_source is PlayerInput, "the player, not the bot, is flying")
	var waited := 0.0
	while Game.state != Game.State.PLAYING and waited < 5.0:
		await dev.wait(0.1)
		waited += 0.1
	dev.check(Game.state == Game.State.PLAYING, "the countdown hands over to play")

	var yaw_before := plane.yaw
	var min_bank := 0.0
	_key(KEY_D, true)
	for i in 10:
		await dev.wait(0.1)
		min_bank = minf(min_bank, plane.bank)
	_key(KEY_D, false)
	var turned := wrapf(plane.yaw - yaw_before, -PI, PI)
	dev.check(turned < -0.6, "D turns right (yaw changed by %.2f rad)" % turned)
	dev.check(min_bank < -0.3, "the plane banks into the turn (%.2f rad)" % min_bank)

	await dev.wait(0.6)
	_key(KEY_W, true)
	await dev.wait(0.7)
	var climbing := plane.pitch
	_key(KEY_W, false)
	dev.check(climbing > 0.3, "W pitches the nose up (%.2f rad)" % climbing)

	_key(KEY_SHIFT, true)
	await dev.wait(0.4)
	var boosting := plane.boosting
	_key(KEY_SHIFT, false)
	dev.check(boosting, "Shift boosts")

	await _tap(dev, KEY_ESCAPE)
	dev.check(Game.state == Game.State.PAUSED, "Esc pauses")
	await _tap(dev, KEY_ESCAPE)
	dev.check(Game.state == Game.State.PLAYING, "Esc again resumes")


func _key(keycode: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = keycode
	ev.keycode = keycode
	ev.pressed = pressed
	Input.parse_input_event(ev)


func _tap(dev: Node, keycode: Key) -> void:
	_key(keycode, true)
	await dev.get_tree().process_frame
	await dev.get_tree().process_frame
	_key(keycode, false)
	await dev.get_tree().process_frame
	await dev.get_tree().process_frame
