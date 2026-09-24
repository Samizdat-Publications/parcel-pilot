class_name Hud
extends CanvasLayer
## In-flight HUD: score card and combo badge, shift clock, parcel and stamp tally,
## destination card with a draining tip, boost gauge, target pointer, countdown,
## popups, speed lines, and hit flashes.

const SPEED_LINES := preload("res://shaders/speed_lines.gdshader")
const ICON_PARCEL := preload("res://assets/icons/parcel.png")
const ICON_STAMP := preload("res://assets/icons/stamp.png")

var plane: MailPlane
var director: DeliveryDirector
var camera: Camera3D

var _root: Control
var _speed_lines: ColorRect
var _flash: ColorRect
var _score: Label
var _combo: PanelContainer
var _combo_label: Label
var _clock_pill: PanelContainer
var _clock: Label
var _parcels: Label
var _stamps: Label
var _warning: PanelContainer
var _dest_name: Label
var _dest_dist: Label
var _dest_tip: Label
var _tip_bar: TipBar
var _boost: BoostGauge
var _pointer: TargetPointer
var _countdown: Label
var _popups: Popups
var _shown_score := 0.0
var _target_score := 0
var _last_mult := 1.0
var _time := 0.0
var _lines := 0.0


func _ready() -> void:
	layer = 5
	_root = UiKit.full_rect(Control.new())
	_root.theme = UiKit.theme()
	add_child(_root)

	_speed_lines = UiKit.full_rect(ColorRect.new()) as ColorRect
	var lines_mat := ShaderMaterial.new()
	lines_mat.shader = SPEED_LINES
	_speed_lines.material = lines_mat
	_root.add_child(_speed_lines)
	_flash = UiKit.full_rect(ColorRect.new()) as ColorRect
	_flash.color = Color(1, 1, 1, 0)
	_root.add_child(_flash)

	_build_score()
	_build_clock()
	_build_tally()
	_build_destination()

	_boost = BoostGauge.new()
	_boost.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	_boost.offset_left = -170
	_boost.offset_top = -170
	_boost.offset_right = -36
	_boost.offset_bottom = -36
	_root.add_child(_boost)

	_pointer = TargetPointer.new()
	_root.add_child(_pointer)
	_countdown = UiKit.label("", 200, UiKit.GOLD, HORIZONTAL_ALIGNMENT_CENTER, 18)
	_countdown.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_countdown.size = Vector2(600, 260)
	_countdown.position -= _countdown.size * 0.5
	_root.add_child(_countdown)
	_popups = Popups.new()
	UiKit.full_rect(_popups)
	_root.add_child(_popups)

	Game.score_changed.connect(_on_score_changed)
	Game.clock_changed.connect(_on_clock_changed)
	Game.countdown_tick.connect(_on_countdown_tick)
	Game.time_added.connect(_on_time_added)
	Game.delivery_recorded.connect(_on_delivery)
	Game.stamp_collected.connect(_on_stamp)
	Game.state_changed.connect(_on_state_changed)


func setup(p: MailPlane, d: DeliveryDirector, cam: Camera3D) -> void:
	plane = p
	director = d
	camera = cam


# ------------------------------------------------------------------ layout
func _build_score() -> void:
	var card := UiKit.panel(UiKit.PAPER, 16, Vector2(22, 8))
	card.position = Vector2(32, 24)
	_root.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", -8)
	card.add_child(box)
	box.add_child(UiKit.ink("SCORE", 20, Color(UiKit.INK, 0.6), HORIZONTAL_ALIGNMENT_LEFT, 600))
	_score = UiKit.ink("0", 54, UiKit.INK, HORIZONTAL_ALIGNMENT_LEFT, 800)
	_score.custom_minimum_size = Vector2(180, 0)
	box.add_child(_score)
	_combo = UiKit.panel(UiKit.RED, 14, Vector2(14, 4))
	_combo.position = Vector2(250, 44)
	_combo_label = UiKit.label("x1.25", 34, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 800)
	_combo.add_child(_combo_label)
	_combo.visible = false
	_root.add_child(_combo)


func _build_clock() -> void:
	_clock_pill = UiKit.pill()
	_clock_pill.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_clock_pill.offset_top = 20
	_clock_pill.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_clock = UiKit.label("1:30", 56, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 800)
	_clock.custom_minimum_size = Vector2(150, 0)
	_clock_pill.add_child(_clock)
	_root.add_child(_clock_pill)
	_warning = UiKit.pill(UiKit.RED)
	_warning.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_warning.offset_top = 120
	_warning.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_warning.add_child(UiKit.label("TURN BACK", 34, UiKit.CREAM, HORIZONTAL_ALIGNMENT_CENTER, 0, 800))
	_warning.visible = false
	_root.add_child(_warning)


func _build_tally() -> void:
	var card := UiKit.panel(UiKit.PAPER, 16, Vector2(18, 6))
	card.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	card.offset_right = -32
	card.offset_top = 24
	card.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_root.add_child(card)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	card.add_child(row)
	_parcels = _tally_item(row, ICON_PARCEL)
	var gap := Control.new()
	gap.custom_minimum_size = Vector2(12, 0)
	row.add_child(gap)
	_stamps = _tally_item(row, ICON_STAMP)


func _tally_item(row: HBoxContainer, icon: Texture2D) -> Label:
	var tex := TextureRect.new()
	tex.texture = icon
	tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tex.custom_minimum_size = Vector2(52, 52)
	row.add_child(tex)
	var l := UiKit.ink("0", 40, UiKit.INK, HORIZONTAL_ALIGNMENT_LEFT, 800)
	l.custom_minimum_size = Vector2(36, 0)
	row.add_child(l)
	return l


func _build_destination() -> void:
	var card := UiKit.panel(UiKit.PAPER, 18, Vector2(26, 12))
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	card.offset_bottom = -30
	card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	card.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_root.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 2)
	card.add_child(box)
	box.add_child(UiKit.ink("DELIVER TO", 18, UiKit.RED, HORIZONTAL_ALIGNMENT_CENTER, 700))
	_dest_name = UiKit.ink("", 42, UiKit.INK, HORIZONTAL_ALIGNMENT_CENTER, 800)
	box.add_child(_dest_name)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 30)
	box.add_child(row)
	_dest_dist = UiKit.ink("", 26, Color(UiKit.INK, 0.75), HORIZONTAL_ALIGNMENT_RIGHT, 600)
	_dest_dist.custom_minimum_size = Vector2(150, 0)
	row.add_child(_dest_dist)
	_dest_tip = UiKit.ink("", 26, UiKit.INK, HORIZONTAL_ALIGNMENT_LEFT, 800)
	_dest_tip.custom_minimum_size = Vector2(150, 0)
	row.add_child(_dest_tip)
	_tip_bar = TipBar.new()
	box.add_child(_tip_bar)


# ------------------------------------------------------------------ update
func _process(delta: float) -> void:
	_time += delta
	_shown_score = move_toward(_shown_score, _target_score, maxf(delta * 400.0, absf(_target_score - _shown_score) * delta * 6.0))
	_score.text = str(roundi(_shown_score))
	_flash.color.a = move_toward(_flash.color.a, 0.0, delta * 1.8)
	if plane == null or director == null or director.current == null:
		return
	_boost.value = plane.boost
	_boost.active = plane.boosting
	var lines_goal := plane.speed_ratio() if plane.boosting else 0.0
	_lines = move_toward(_lines, lines_goal, delta * 3.0)
	(_speed_lines.material as ShaderMaterial).set_shader_parameter("intensity", _lines)
	_warning.visible = plane.out_of_bounds and fmod(_time, 0.8) < 0.55
	var target := director.current.delivery_position()
	_dest_name.text = director.current.display_name
	var dist := plane.global_position.distance_to(target)
	_dest_dist.text = "%d m" % roundi(dist)
	_dest_tip.text = "TIP %d" % roundi(director.current_tip())
	_tip_bar.value = director.tip_fraction()
	var mult := director.combo_multiplier()
	if not is_equal_approx(mult, _last_mult):
		_combo.visible = mult > 1.0
		_combo_label.text = "x%.2f" % mult
		if mult > _last_mult:
			UiKit.pop(_combo, 0.4)
		_last_mult = mult
	_update_pointer(target, dist)


func _update_pointer(target: Vector3, dist: float) -> void:
	var view := get_viewport().get_visible_rect().size
	var margin := 90.0
	var inner := Rect2(Vector2(margin, margin), view - Vector2(margin, margin) * 2.0)
	var behind := camera.is_position_behind(target)
	var screen := camera.unproject_position(target)
	_pointer.distance = dist
	if not behind and inner.has_point(screen):
		_pointer.on_screen = true
		_pointer.position = screen
		return
	_pointer.on_screen = false
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
	_pointer.position = center + dir * minf(tx, ty)
	_pointer.angle = dir.angle()


# ------------------------------------------------------------------ events
func flash(color: Color, strength := 0.35) -> void:
	_flash.color = Color(color, strength)


func show_message(text: String, color := UiKit.CREAM, _seconds := 1.2) -> void:
	_popups.spawn(text, Vector2(get_viewport().get_visible_rect().size.x * 0.5, 300), 46, color)


func _on_state_changed(state: Game.State, _previous: Game.State) -> void:
	if state == Game.State.COUNTDOWN:
		_shown_score = 0.0
		_target_score = 0
		_last_mult = 1.0
		_combo.visible = false
		_parcels.text = "0"
		_stamps.text = "0"


func _on_score_changed(score: int, _delta: int) -> void:
	_target_score = score


func _on_clock_changed(seconds: float) -> void:
	var text := UiKit.format_clock(seconds)
	if text != _clock.text:
		_clock.text = text
		if seconds <= 10.0 and seconds > 0.0:
			_clock.label_settings.font_color = UiKit.RED
			UiKit.pop(_clock_pill, 1.25, 0.3)
		else:
			_clock.label_settings.font_color = UiKit.CREAM


func _on_countdown_tick(value: int) -> void:
	_countdown.text = str(value) if value > 0 else "GO!"
	_countdown.pivot_offset = _countdown.size * 0.5
	_countdown.scale = Vector2.ONE * 1.8
	_countdown.modulate.a = 1.0
	var tw := _countdown.create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(_countdown, "scale", Vector2.ONE, 0.35)
	if value <= 0:
		tw.tween_interval(0.35)
		tw.tween_property(_countdown, "modulate:a", 0.0, 0.3)


func _on_time_added(seconds: float, reason: String) -> void:
	var clock_at := _clock_pill.get_global_rect().get_center() + Vector2(170, 0)
	if seconds > 0.0:
		_popups.spawn("+%ds" % roundi(seconds), clock_at, 38, UiKit.GOLD, 0.25, 40.0, 0.6)
	elif seconds < 0.0:
		_popups.spawn("%ds" % roundi(seconds), clock_at, 38, UiKit.RED, 0.0, 40.0, 0.6)
		show_message(reason.to_upper(), UiKit.RED)


func _on_delivery(result: Dictionary) -> void:
	_parcels.text = str(Game.deliveries)
	var mid := Vector2(get_viewport().get_visible_rect().size.x * 0.5, 280)
	var express: bool = result["grade"] == DeliveryRules.Grade.EXPRESS
	_popups.spawn(String(result["grade_name"]).to_upper() + "!", mid, 76 if express else 60,
		UiKit.GOLD if express else UiKit.CREAM)
	var pts := "+%d" % result["points"]
	if float(result["multiplier"]) > 1.0:
		pts += "  (x%.2f)" % result["multiplier"]
	_popups.spawn(pts, mid + Vector2(0, 76), 44, UiKit.CREAM, 0.15)


func _on_stamp(_where: Vector3) -> void:
	_stamps.text = str(Game.stamps)
	_popups.spawn("STAMP  +%d" % Game.rules.stamp_points, Vector2(get_viewport().get_visible_rect().size.x * 0.5, 360),
		40, UiKit.GOLD)
