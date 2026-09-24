extends Node3D
## Wires the world, plane, camera, deliveries and UI together, owns the shift flow
## (attract mode, countdown, play, results), and turns game events into feel:
## sound, particles, camera kicks and hit-stop.

@onready var world: World = $World
@onready var plane: MailPlane = $Plane
@onready var camera: ChaseCamera = $ChaseCamera
@onready var director: DeliveryDirector = $Director
@onready var hud: Hud = $HUD
@onready var title: TitleScreen = $Title
@onready var results: ResultsScreen = $Results
@onready var pause_menu: PauseMenu = $Pause

var player_input := PlayerInput.new()
var autopilot := Autopilot.new()
var plane_fx := PlaneFx.new()
var _last_tick_second := -1


func _ready() -> void:
	director.setup(world.islands(), world.hub())
	autopilot.director = director
	camera.target = plane
	hud.setup(plane, director, camera)
	add_child(plane_fx)
	plane_fx.setup(plane)
	_apply_settings()
	Save.settings_changed.connect(_apply_settings)

	plane.crashed.connect(_on_plane_crashed)
	plane.fell.connect(_on_plane_fell)
	director.delivered.connect(_on_delivered)
	Game.state_changed.connect(_on_state_changed)
	Game.countdown_tick.connect(func(v: int) -> void: Audio.play("tick" if v > 0 else "go"))
	Game.clock_changed.connect(_on_clock_changed)
	Game.stamp_collected.connect(_on_stamp)
	Game.shift_ended.connect(_on_shift_ended)
	pause_menu.restart_requested.connect(start_shift)
	pause_menu.title_requested.connect(Game.to_title)
	results.fly_again_requested.connect(start_shift)
	results.title_requested.connect(Game.to_title)
	results.rank_stamped.connect(func() -> void: Audio.play("crash", -10.0, 1.8))
	for ring in get_tree().get_nodes_in_group("boost_rings"):
		(ring as BoostRing).boosted.connect(_on_boost_ring)
	for cloud in get_tree().get_nodes_in_group("storm_clouds"):
		(cloud as StormCloud).zapped.connect(_on_zapped)

	_show_for_state(Game.state)
	_enter_free_flight()
	camera.snap()


func _process(_delta: float) -> void:
	var mix := 1.0 if Game.state in [Game.State.COUNTDOWN, Game.State.PLAYING] else 0.45
	if Game.state == Game.State.PAUSED:
		mix = 0.0
	Audio.set_flight(plane.speed_ratio(), plane.boosting, mix)


func _unhandled_input(event: InputEvent) -> void:
	match Game.state:
		Game.State.TITLE:
			if event.is_action_pressed("confirm"):
				get_viewport().set_input_as_handled()
				Audio.play("ui_click")
				start_shift()
		Game.State.PLAYING:
			if event.is_action_pressed("pause"):
				get_viewport().set_input_as_handled()
				Game.pause()
		Game.State.RESULTS:
			if event.is_action_pressed("confirm") or event.is_action_pressed("restart"):
				get_viewport().set_input_as_handled()
				start_shift()
			elif event.is_action_pressed("back"):
				get_viewport().set_input_as_handled()
				Game.to_title()


func start_shift() -> void:
	var spawn := world.spawn_transform()
	plane.reset_to(spawn)
	director.begin_shift(spawn.origin)
	plane.face(director.current.delivery_position())
	plane.input_source = autopilot if Dev.has_flag("autopilot") else player_input
	plane.frozen = true
	plane_fx.reset()
	camera.snap()
	_last_tick_second = -1
	Audio.set_music_level(Audio.MUSIC_DB - 3.0)
	Game.begin_shift()


func _enter_free_flight() -> void:
	plane.input_source = autopilot
	plane.frozen = false
	director.begin_free_flight(plane.global_position)
	Audio.set_music_level(Audio.MUSIC_DB)


func _apply_settings() -> void:
	player_input.invert_pitch = bool(Save.settings["invert_pitch"])
	if Dev.args.has("scenario"):
		return
	var want := DisplayServer.WINDOW_MODE_FULLSCREEN if bool(Save.settings["fullscreen"]) else DisplayServer.WINDOW_MODE_WINDOWED
	if DisplayServer.window_get_mode() != want:
		DisplayServer.window_set_mode(want)


func _on_state_changed(state: Game.State, previous: Game.State) -> void:
	_show_for_state(state)
	match state:
		Game.State.PLAYING:
			plane.frozen = false
		Game.State.PAUSED:
			Audio.set_music_level(Audio.MUSIC_DB - 8.0)
		Game.State.RESULTS:
			plane.input_source = autopilot
			Audio.set_music_level(Audio.MUSIC_DB)
		Game.State.TITLE:
			if previous != Game.State.RESULTS:
				_enter_free_flight()
			else:
				plane.input_source = autopilot
	if previous == Game.State.PAUSED and state == Game.State.PLAYING:
		Audio.set_music_level(Audio.MUSIC_DB - 3.0)


func _show_for_state(state: Game.State) -> void:
	title.visible = state == Game.State.TITLE
	hud.visible = state in [Game.State.COUNTDOWN, Game.State.PLAYING, Game.State.PAUSED]
	results.visible = state == Game.State.RESULTS
	pause_menu.visible = state == Game.State.PAUSED


# ------------------------------------------------------------------- feel
func _on_delivered(result: Dictionary) -> void:
	if not Game.is_playing():
		return
	Game.record_delivery(result)
	var where: Vector3 = result["position"]
	var express: bool = result["grade"] == DeliveryRules.Grade.EXPRESS
	Audio.play("express" if express else "deliver")
	Audio.duck(7.0, 1.6)
	Fx.burst("confetti", where)
	var island: Island = result["island"]
	var inward := island.global_position - where
	inward.y = 0.0
	ParcelDrop.spawn(world, where + inward.normalized() * 8.0 + Vector3.DOWN * 3.0)
	camera.add_trauma(0.16)
	camera.kick_fov(7.0)
	get_tree().create_timer(1.0).timeout.connect(func() -> void:
		if Game.is_playing():
			Audio.play("new_parcel", -6.0))


func _on_plane_crashed(impact: float) -> void:
	camera.add_trauma(0.35 + impact * 0.5)
	Audio.play("crash", 0.0, 1.0, 0.1)
	Fx.burst("dust", plane.global_position)
	Fx.burst("debris", plane.global_position)
	_hit_stop(0.03 + 0.06 * impact)
	if Game.is_playing():
		director.register_crash()
		Game.record_crash()
		hud.show_message("PARCEL DAMAGED", UiKit.RED)
		hud.flash(UiKit.RED, 0.3)


func _on_zapped(where: Vector3) -> void:
	camera.add_trauma(0.8)
	Audio.play("zap")
	Fx.burst("zap", where)
	hud.flash(Color(0.8, 0.9, 1.0), 0.55)


func _on_boost_ring(where: Vector3) -> void:
	Audio.play("ring", -3.0, 1.0, 0.05)
	Fx.burst("ring", where)
	camera.kick_fov(5.0)


func _on_stamp(where: Vector3) -> void:
	Audio.play("stamp", 0.0, 1.0, 0.04)
	Fx.burst("sparkle", where)


func _on_clock_changed(seconds: float) -> void:
	if not Game.is_playing() or seconds > 10.0 or seconds <= 0.0:
		return
	var s := ceili(seconds)
	if s != _last_tick_second:
		_last_tick_second = s
		Audio.play("clock_tick", -2.0)


func _on_shift_ended(new_best: bool) -> void:
	Audio.play("results")
	Audio.duck(10.0, 4.5)
	if new_best:
		get_tree().create_timer(2.2).timeout.connect(func() -> void: Audio.play("new_best"))


func _on_plane_fell() -> void:
	var spawn := world.spawn_transform()
	plane.reset_to(spawn)
	if director.current != null:
		plane.face(director.current.delivery_position())
	plane_fx.reset()
	camera.snap()
	Audio.play("ring", -6.0, 0.6)
	if Game.is_playing():
		Game.add_time(-Game.rules.fall_penalty_seconds, "Lost in the clouds")


## A tiny freeze-frame that sells the impact.
func _hit_stop(seconds: float) -> void:
	Engine.time_scale = 0.05
	await get_tree().create_timer(seconds, true, false, true).timeout
	Engine.time_scale = 1.0
