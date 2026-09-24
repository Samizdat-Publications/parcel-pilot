extends RefCounted
## Gallery run through the player's chase camera: for each chosen island, make it the
## destination, start the plane ~110 m out at a pleasing angle, let the autopilot fly
## in, and capture. Verifies ambient life (smoke, flags, birds, beacon) and feeds the
## README gallery.

# (island node name, approach bearing in degrees, height above the island top, seconds)
const STOPS := [
	["KettleHollow", 200.0, 16.0, 3.2],
	["MossyMill", 250.0, 14.0, 3.4],
	["BeaconPoint", 160.0, 20.0, 3.0],
	["PostOffice", 30.0, 18.0, 3.0],
	["Bellfry", 80.0, 16.0, 3.2],
	["StargazersPerch", 300.0, 14.0, 3.0],
	["HollowArch", 20.0, 6.0, 4.0],
	["CloudberryFarm", 120.0, 18.0, 3.2],
]


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	dev.args["autopilot"] = "true"
	main.start_shift()
	await dev.wait(3.6)
	for stop in STOPS:
		Game.time_left = 84.0
		var island: Island = main.world.get_node("Islands/" + String(stop[0]))
		var bearing := deg_to_rad(float(stop[1]))
		var hoop := island.delivery_position()
		var start := hoop + Vector3(cos(bearing), 0.0, sin(bearing)) * 110.0
		start.y = island.global_position.y + float(stop[2])
		main.plane.global_position = start
		main.plane.face(island.global_position)
		main.plane.reset_physics_interpolation()
		main.plane_fx.reset()
		main.director.force_destination(island, start)
		main.camera.snap()
		await dev.wait(float(stop[3]))
		await dev.capture("show_" + String(stop[0]).to_snake_case())
