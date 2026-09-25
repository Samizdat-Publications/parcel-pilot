extends RefCounted
## Footage for the README: the bot flies a shift under Godot's movie maker
## (--write-movie). Marks the frame of the first delivery so tools/make_clip.py can cut
## the clip around it.


func run(dev: Node) -> void:
	var main: Node = dev.get_tree().current_scene
	await dev.wait(2.0)
	dev.args["autopilot"] = "true"
	main.start_shift()
	var start := Game.deliveries
	var waited := 0.0
	while Game.deliveries == start and waited < 60.0:
		await dev.wait(0.1)
		waited += 0.1
	print("[movie] delivery_frame=%d" % Engine.get_frames_drawn())
	await dev.wait(3.5)
