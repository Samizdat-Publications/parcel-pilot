class_name Hud
extends CanvasLayer
## In-flight HUD: clock, score, combo, deliveries, destination card with a draining
## tip, boost gauge, countdown, event messages, and a pointer to the target hoop.

var plane: MailPlane
var director: DeliveryDirector
var camera: Camera3D

var _clock: Label
var _score: Label
var _combo: Label
var _deliveries: Label
var _dest_name: Label
var _dest_info: Label
var _tip_bar: ProgressBar
var _boost_bar: ProgressBar
var _countdown: Label
var _message: Label
var _warning: Label
var _arrow: Polygon2D
var _marker: Label
var _message_time := 0.0


func _ready() -> void:
	layer = 5
	var root := UiKit.full_rect(Control.new())
	add_child(root)

	_score = UiKit.label("0", 52, UiKit.CREAM, HORIZONTAL_ALIGNMENT_LEFT)
	_score.position = Vector2(40, 24)
	root.add_child(_score)
	_combo = UiKit.label("", 30, UiKit.GOLD, HORIZONTAL_ALIGNMENT_LEFT)
	_combo.position = Vector2(42, 92)
	root.add_child(_combo)

	_clock = UiKit.label("1:30", 68)
	_clock.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_clock.offset_top = 18
	_clock.grow_horizontal = Control.GROW_DIRECTION_BOTH
	root.add_child(_clock)

	_warning = UiKit.label("TURN BACK", 40, UiKit.RED)
	_warning.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_warning.offset_top = 110
	_warning.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_warning.visible = false
	root.add_child(_warning)

	_deliveries = UiKit.label("0 delivered", 36, UiKit.CREAM, HORIZONTAL_ALIGNMENT_RIGHT)
	_deliveries.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_deliveries.offset_right = -40
	_deliveries.offset_top = 30
	_deliveries.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	root.add_child(_deliveries)

	var card := VBoxContainer.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	card.offset_bottom = -36
	card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	card.grow_vertical = Control.GROW_DIRECTION_BEGIN
	card.alignment = BoxContainer.ALIGNMENT_END
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(card)
	card.add_child(UiKit.label("DELIVER TO", 24, UiKit.PAPER))
	_dest_name = UiKit.label("", 46)
	card.add_child(_dest_name)
	_dest_info = UiKit.label("", 28, UiKit.PAPER)
	card.add_child(_dest_info)
	_tip_bar = ProgressBar.new()
	_tip_bar.custom_minimum_size = Vector2(420, 14)
	_tip_bar.show_percentage = false
	_tip_bar.max_value = 1.0
	card.add_child(_tip_bar)

	_boost_bar = ProgressBar.new()
	_boost_bar.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	_boost_bar.offset_left = -300
	_boost_bar.offset_top = -64
	_boost_bar.offset_right = -40
	_boost_bar.offset_bottom = -44
	_boost_bar.show_percentage = false
	_boost_bar.max_value = 1.0
	root.add_child(_boost_bar)
	var boost_label := UiKit.label("BOOST", 24, UiKit.PAPER, HORIZONTAL_ALIGNMENT_RIGHT)
	boost_label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	boost_label.offset_right = -40
	boost_label.offset_top = -100
	boost_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	root.add_child(boost_label)

	_countdown = UiKit.label("", 180, UiKit.GOLD)
	_countdown.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_countdown.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_countdown.grow_vertical = Control.GROW_DIRECTION_BOTH
	root.add_child(_countdown)

	_message = UiKit.label("", 54, UiKit.CREAM)
	_message.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_message.offset_top = 250
	_message.grow_horizontal = Control.GROW_DIRECTION_BOTH
	root.add_child(_message)

	_arrow = Polygon2D.new()
	_arrow.polygon = PackedVector2Array([Vector2(26, 0), Vector2(-14, -18), Vector2(-6, 0), Vector2(-14, 18)])
	_arrow.color = UiKit.GOLD
	root.add_child(_arrow)
	_marker = UiKit.label("v", 40, UiKit.GOLD)
	_marker.size = Vector2(60, 60)
	root.add_child(_marker)

	Game.score_changed.connect(_on_score_changed)
	Game.clock_changed.connect(_on_clock_changed)
	Game.countdown_tick.connect(_on_countdown_tick)
	Game.time_added.connect(_on_time_added)
	Game.delivery_recorded.connect(_on_delivery)


func setup(p: MailPlane, d: DeliveryDirector, cam: Camera3D) -> void:
	plane = p
	director = d
	camera = cam


func show_message(text: String, color := UiKit.CREAM, seconds := 1.8) -> void:
	_message.text = text
	_message.label_settings.font_color = color
	_message_time = seconds
	_message.modulate.a = 1.0


func _process(delta: float) -> void:
	if plane == null or director == null or director.current == null:
		return
	_message_time -= delta
	_message.modulate.a = clampf(_message_time / 0.4, 0.0, 1.0)
	_boost_bar.value = plane.boost
	_warning.visible = plane.out_of_bounds
	var target := director.current.delivery_position()
	_dest_name.text = director.current.display_name
	var dist := plane.global_position.distance_to(target)
	_dest_info.text = "%d m    tip %d" % [roundi(dist), roundi(director.current_tip())]
	_tip_bar.value = director.tip_fraction()
	var mult := director.combo_multiplier()
	_combo.text = "combo x%.2f" % mult if mult > 1.0 else ""
	_update_pointer(target)


func _update_pointer(target: Vector3) -> void:
	var view := get_viewport().get_visible_rect().size
	var margin := 80.0
	var inner := Rect2(Vector2(margin, margin), view - Vector2(margin, margin) * 2.0)
	var behind := camera.is_position_behind(target)
	var screen := camera.unproject_position(target)
	if not behind and inner.has_point(screen):
		_arrow.visible = false
		_marker.visible = true
		_marker.position = screen - Vector2(30, 70)
		return
	_marker.visible = false
	_arrow.visible = true
	var center := view * 0.5
	var dir := screen - center
	if behind:
		dir = -dir
	if dir.length() < 1.0:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var half := inner.size * 0.5
	var tx := absf(half.x / dir.x) if absf(dir.x) > 0.0001 else INF
	var ty := absf(half.y / dir.y) if absf(dir.y) > 0.0001 else INF
	_arrow.position = center + dir * minf(tx, ty)
	_arrow.rotation = dir.angle()


func _on_score_changed(score: int, _delta: int) -> void:
	_score.text = str(score)


func _on_clock_changed(seconds: float) -> void:
	_clock.text = UiKit.format_clock(seconds)
	_clock.label_settings.font_color = UiKit.RED if seconds <= 10.0 else UiKit.CREAM


func _on_countdown_tick(value: int) -> void:
	_countdown.text = str(value) if value > 0 else "GO!"
	if value <= 0:
		get_tree().create_timer(0.8).timeout.connect(func() -> void: _countdown.text = "")


func _on_time_added(seconds: float, reason: String) -> void:
	if seconds < 0.0:
		show_message("%s  %ds" % [reason, roundi(seconds)], UiKit.RED)


func _on_delivery(result: Dictionary) -> void:
	_deliveries.text = "%d delivered" % Game.deliveries
	var text := "%s!  +%d  (+%ds)" % [result["grade_name"], result["points"], roundi(result["time_bonus"])]
	show_message(text, UiKit.GOLD if result["grade"] == DeliveryRules.Grade.EXPRESS else UiKit.CREAM)
