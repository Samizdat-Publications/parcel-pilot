extends RefCounted
## Integration test (headless, fixed 60 fps): the autopilot flies a complete shift
## through the real game code. It must deliver parcels and land on the results screen.


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	dev.args["autopilot"] = "true"
	main.start_shift()
	var simulated := 0
	while Game.state != Game.State.RESULTS and simulated < 900:
		await dev.wait(1.0)
		simulated += 1
		if simulated % 30 == 0:
			print("[bot] t=%ds state=%s deliveries=%d score=%d clock=%.0f" % [
				simulated, Game.State.keys()[Game.state], Game.deliveries, Game.score, Game.time_left])
	print("[bot] finished: deliveries=%d score=%d crashes=%d stamps=%d flown=%.0fs rank=%s" % [
		Game.deliveries, Game.score, Game.crashes, Game.stamps, Game.shift_time, Game.rank()])
	dev.check(Game.state == Game.State.RESULTS, "shift ended on the results screen")
	dev.check(Game.deliveries >= 3, "autopilot delivered at least 3 parcels (got %d)" % Game.deliveries)
	dev.check(Game.score > 0, "score is positive (%d)" % Game.score)
	dev.check(Game.shift_time > Game.rules.shift_seconds, "delivery bonuses extended the shift")
