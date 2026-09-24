extends Node3D
## Wires the world, plane, camera, deliveries and UI together and owns the shift flow:
## attract mode on the title screen, countdown, play, results, back again.

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


func _ready() -> void:
	director.setup(world.islands(), world.hub())
	autopilot.director = director
	camera.target = plane
	hud.setup(plane, director, camera)
	player_input.invert_pitch = bool(Save.settings["invert_pitch"])
	Save.settings_changed.connect(func() -> void: player_input.invert_pitch = bool(Save.settings["invert_pitch"]))

	plane.crashed.connect(_on_plane_crashed)
	plane.fell.connect(_on_plane_fell)
	director.delivered.connect(_on_delivered)
	Game.state_changed.connect(_on_state_changed)
	pause_menu.restart_requested.connect(start_shift)
	pause_menu.title_requested.connect(Game.to_title)
	for ring in get_tree().get_nodes_in_group("boost_rings"):
		(ring as BoostRing).boosted.connect(_on_boost_ring)
	for cloud in get_tree().get_nodes_in_group("storm_clouds"):
		(cloud as StormCloud).zapped.connect(_on_zapped)

	_show_for_state(Game.state)
	_enter_free_flight()
	camera.snap()


func _unhandled_input(event: InputEvent) -> void:
	match Game.state:
		Game.State.TITLE:
			if event.is_action_pressed("confirm"):
				get_viewport().set_input_as_handled()
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
	camera.snap()
	Game.begin_shift()


func _enter_free_flight() -> void:
	plane.input_source = autopilot
	plane.frozen = false
	director.begin_free_flight(plane.global_position)


func _on_state_changed(state: Game.State, previous: Game.State) -> void:
	_show_for_state(state)
	match state:
		Game.State.PLAYING:
			plane.frozen = false
		Game.State.RESULTS:
			plane.input_source = autopilot
		Game.State.TITLE:
			if previous != Game.State.RESULTS:
				_enter_free_flight()
			else:
				plane.input_source = autopilot


func _show_for_state(state: Game.State) -> void:
	title.visible = state == Game.State.TITLE
	hud.visible = state in [Game.State.COUNTDOWN, Game.State.PLAYING, Game.State.PAUSED]
	results.visible = state == Game.State.RESULTS
	pause_menu.visible = state == Game.State.PAUSED


func _on_delivered(result: Dictionary) -> void:
	if Game.is_playing():
		Game.record_delivery(result)


func _on_plane_crashed(impact: float) -> void:
	camera.add_trauma(0.35 + impact * 0.5)
	if Game.is_playing():
		director.register_crash()
		Game.record_crash()
		hud.show_message("Parcel damaged!", UiKit.RED, 1.2)


func _on_zapped(_where: Vector3) -> void:
	camera.add_trauma(0.8)


func _on_boost_ring(_where: Vector3) -> void:
	if Game.is_playing():
		hud.show_message("Boost!", UiKit.SKY, 0.8)


func _on_plane_fell() -> void:
	var spawn := world.spawn_transform()
	plane.reset_to(spawn)
	if director.current != null:
		plane.face(director.current.delivery_position())
	camera.snap()
	if Game.is_playing():
		Game.add_time(-Game.rules.fall_penalty_seconds, "Lost in the clouds")
