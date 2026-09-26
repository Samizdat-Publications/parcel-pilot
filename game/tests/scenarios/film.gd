extends RefCounted
## Footage for the landing page and the README, rendered frame by frame under Godot's
## movie maker (tools/film.py passes --write-movie and --fixed-fps). --shoot picks one:
##   shift     the title screen, one whole shift flown by the bot, then the shift report
##   features  staged moments: a boost-ring run, a stamp, a storm, an express delivery
##   islands   the title screen, then the ten islands approached one after another,
##             with the HUD hidden
## Every moment worth cutting prints "[mark] <frame> <kind> <label>"; tools/film.py
## turns those into <shoot>.json for tools/make_media.py.

# (island node name, approach bearing in degrees, height above the island top)
const ISLANDS := [
	["PostOffice", 30.0, 18.0],
	["MossyMill", 250.0, 14.0],
	["BeaconPoint", 160.0, 20.0],
	["KettleHollow", 200.0, 16.0],
	["OrchardRest", 60.0, 14.0],
	["Pinewhistle", 200.0, 20.0],
	["CloudberryFarm", 120.0, 18.0],
	["Bellfry", 80.0, 16.0],
	["StargazersPerch", 300.0, 14.0],
	["HollowArch", 20.0, 6.0],
]
const ISLAND_SECONDS := 5.0


## Flies through a list of points (or nodes, followed as they drift) in order with the
## autopilot's steering, boosting on request.
class WaypointPilot:
	var steer: Autopilot
	var points: Array = []
	var boost := false
	var _index := 0

	func get_controls(plane: MailPlane) -> Vector3:
		while _index < points.size() - 1:
			var to := _point(_index) - plane.global_position
			if to.length() > 9.0 and to.dot(plane.forward()) > 0.0:
				break
			_index += 1
		var c := steer.steer_to(plane, _point(_index))
		c.z = 1.0 if boost else 0.0
		return c

	func _point(i: int) -> Vector3:
		var p: Variant = points[i]
		return (p as Node3D).global_position if p is Node3D else p


var _dev: Node
var _main: Node


func run(dev: Node) -> void:
	_dev = dev
	_main = dev.get_tree().current_scene
	_listen()
	var shoot := String(dev.args.get("shoot", "shift"))
	match shoot:
		"shift":
			await _shoot_shift()
		"features":
			await _shoot_features()
		"islands":
			await _shoot_islands()
		_:
			dev.check(false, "unknown shoot: " + shoot)


func _shoot_shift() -> void:
	await _dev.wait(0.5)
	_mark("title", "")
	await _dev.wait(5.5)
	_dev.args["autopilot"] = "true"
	Audio.play("ui_click")
	_main.start_shift()
	var waited := 0.0
	while Game.state != Game.State.RESULTS and waited < 480.0:
		await _dev.wait(0.25)
		waited += 0.25
	_dev.check(Game.state == Game.State.RESULTS, "the shift ended within 8 minutes")
	_dev.check(Game.deliveries >= 3, "the bot delivered at least 3 parcels (%d)" % Game.deliveries)
	print("[film] stats score=%d deliveries=%d stamps=%d crashes=%d rank=%s streak=%d" % [
		Game.score, Game.deliveries, Game.stamps, Game.crashes, Game.rank().replace(" ", "_"), Game.best_streak])
	await _dev.wait(8.0)
	_mark("end", "")


func _shoot_features() -> void:
	_dev.args["autopilot"] = "true"
	_main.start_shift()
	await _dev.wait(4.0)
	var world: Node3D = _main.world

	# A run down the three rings toward Mossy Mill, starting low on boost.
	var rings: Array = [world.get_node("BoostRings/ToMill1"), world.get_node("BoostRings/ToMill2"),
		world.get_node("BoostRings/ToMill3")]
	var first: Vector3 = rings[0].global_position
	var line: Vector3 = (rings[2].global_position - first).normalized()
	var pilot := _pilot(true)
	for ring: Node3D in rings:
		pilot.points.append(ring.global_position)
	pilot.points.append(rings[2].global_position + line * 120.0)
	_place(first - line * 95.0 + Vector3.UP * 2.0, first)
	_main.plane.boost = 0.2
	_main.plane.input_source = pilot
	_mark("shot", "rings")
	await _dev.wait(7.0)

	# A floating stamp, dead ahead, with the balloon behind it.
	var stamp: Node3D = world.get_node("Stamps/Stamp1")
	var toward := Vector3(0.0, 0.0, -1.0)
	pilot = _pilot(false)
	pilot.points = [stamp, stamp.global_position - toward * 90.0]
	_place(stamp.global_position + toward * 85.0, stamp.global_position)
	_main.plane.input_source = pilot
	_mark("shot", "stamp")
	await _dev.wait(5.5)

	# Straight into a thundercloud (it drifts, so the pilot follows the node).
	var storm: Node3D = world.get_node("Hazards/Storm1")
	toward = Vector3(0.9, 0.0, 0.45).normalized()
	pilot = _pilot(false)
	pilot.points = [storm, storm.global_position - toward * 150.0]
	_place(storm.global_position + toward * 120.0 + Vector3.DOWN * 4.0, storm.global_position)
	_main.plane.input_source = pilot
	_mark("shot", "storm")
	await _dev.wait(7.0)

	# An express delivery at Mossy Mill, flown in by the regular autopilot.
	_mark("shot", "deliver")
	await _approach("MossyMill", 250.0, 14.0)
	var start := Game.deliveries
	var waited := 0.0
	while Game.deliveries == start and waited < 12.0:
		await _dev.wait(0.1)
		waited += 0.1
	_dev.check(Game.deliveries > start, "the staged delivery landed")
	await _dev.wait(4.5)
	_mark("end", "")


func _shoot_islands() -> void:
	await _dev.wait(0.5)
	_mark("title", "")
	await _dev.wait(6.0)
	_dev.args["autopilot"] = "true"
	_main.start_shift()
	await _dev.wait(4.0)
	_main.hud.visible = false
	for stop in ISLANDS:
		Game.time_left = 90.0
		_mark("island", String(stop[0]))
		await _approach(String(stop[0]), float(stop[1]), float(stop[2]))
		await _dev.wait(ISLAND_SECONDS)
	_mark("end", "")


## Makes the island the destination and starts the plane 110 m out on the bearing,
## so the regular autopilot flies the approach.
func _approach(island_name: String, bearing_deg: float, height: float) -> void:
	var island: Island = _main.world.get_node("Islands/" + island_name)
	var bearing := deg_to_rad(bearing_deg)
	var hoop := island.delivery_position()
	var start := hoop + Vector3(cos(bearing), 0.0, sin(bearing)) * 110.0
	start.y = island.global_position.y + height
	_main.plane.input_source = _main.autopilot
	_place(start, island.global_position)
	_main.director.force_destination(island, start)
	await _dev.get_tree().process_frame


func _place(where: Vector3, look_at: Vector3) -> void:
	_main.plane.global_position = where
	_main.plane.face(look_at)
	_main.plane.reset_physics_interpolation()
	_main.plane_fx.reset()
	_main.camera.snap()


func _pilot(boost: bool) -> WaypointPilot:
	var p := WaypointPilot.new()
	p.steer = _main.autopilot
	p.boost = boost
	return p


func _listen() -> void:
	Game.state_changed.connect(_on_state_changed)
	Game.delivery_recorded.connect(func(result: Dictionary) -> void:
		var island: Island = result["island"]
		_mark("delivery", "%s|%s|%d" % [String(result["grade_name"]), island.display_name, int(result["points"])]))
	Game.stamp_collected.connect(func(_where: Vector3) -> void: _mark("stamp", ""))
	_main.plane.crashed.connect(func(_impact: float) -> void: _mark("crash", ""))
	for ring in _dev.get_tree().get_nodes_in_group("boost_rings"):
		(ring as BoostRing).boosted.connect(func(_where: Vector3) -> void: _mark("ring", ""))
	for cloud in _dev.get_tree().get_nodes_in_group("storm_clouds"):
		(cloud as StormCloud).zapped.connect(func(_where: Vector3) -> void: _mark("zap", ""))


func _on_state_changed(state: Game.State, _previous: Game.State) -> void:
	match state:
		Game.State.COUNTDOWN:
			_mark("countdown", "")
		Game.State.PLAYING:
			_mark("go", "")
		Game.State.RESULTS:
			_mark("results", Game.rank())


func _mark(kind: String, label: String) -> void:
	print("[mark] %d %s %s" % [Engine.get_frames_drawn(), kind, label])
