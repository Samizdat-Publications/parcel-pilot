extends RefCounted
## Windowed capture tour. Every shot is the real game viewport: the player camera
## plus UI, exactly what a player would see at that moment.


## Wraps another pilot and holds the boost button down.
class BoostingPilot:
	var inner: Object

	func get_controls(plane: MailPlane) -> Vector3:
		var c: Vector3 = inner.get_controls(plane)
		c.z = 1.0
		return c


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	await dev.wait(3.0)
	await dev.capture("01_title")

	dev.args["autopilot"] = "true"
	main.start_shift()
	await dev.wait(1.2)
	await dev.capture("02_countdown")

	await dev.wait(7.0)
	await dev.capture("03_flight")
	await _measure_performance(dev)

	var start := Game.deliveries
	var waited := 0.0
	while Game.deliveries == start and waited < 75.0:
		await dev.wait(0.1)
		waited += 0.1
	dev.check(Game.deliveries > start, "a parcel was delivered within 75 s")
	await dev.wait(0.35)
	await dev.capture("04_delivered")

	var booster := BoostingPilot.new()
	booster.inner = main.plane.input_source
	main.plane.boost = 1.0
	main.plane.input_source = booster
	await dev.wait(1.6)
	await dev.capture("05_boost")
	main.plane.input_source = booster.inner

	Game.pause()
	await dev.wait(0.5)
	await dev.capture("06_pause")
	Game.resume()

	Game.end_shift()
	await dev.wait(3.2)
	await dev.capture("07_results")


## Average frame rate over two seconds of flight, plus the renderer's load that frame.
func _measure_performance(dev: Node) -> void:
	var frames := 0
	var start := Time.get_ticks_usec()
	while Time.get_ticks_usec() - start < 2000000:
		await dev.get_tree().process_frame
		frames += 1
	var fps := frames / ((Time.get_ticks_usec() - start) / 1000000.0)
	var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var prims := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	print("[perf] fps=%.0f draw_calls=%d primitives=%d" % [fps, draws, prims])
	dev.check(fps >= 60.0, "frame rate at least 60 fps (%.0f)" % fps)
