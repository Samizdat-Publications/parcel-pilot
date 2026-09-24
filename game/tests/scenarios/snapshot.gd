extends RefCounted
## Progress snapshot for docs/progress (driven by tools/snap.py).
## --shots=title,flight,delivery picks which player-camera frames to save.


func run(dev: Node) -> void:
	var shots := String(dev.args.get("shots", "title,flight")).split(",")
	var main: Node = dev.get_tree().current_scene
	await dev.wait(3.0)
	if shots.has("title"):
		await dev.capture("title")
	if not (shots.has("flight") or shots.has("delivery")):
		return
	dev.args["autopilot"] = "true"
	main.start_shift()
	await dev.wait(9.0)
	if shots.has("flight"):
		await dev.capture("flight")
	if shots.has("delivery"):
		var start := Game.deliveries
		var waited := 0.0
		while Game.deliveries == start and waited < 75.0:
			await dev.wait(0.1)
			waited += 0.1
		await dev.wait(0.35)
		await dev.capture("delivery")
