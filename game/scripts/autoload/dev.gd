extends Node
## Developer harness used by the automated verification loop.
##
## Command line flags (after the `--` separator):
##   --scenario=<name>   run res://tests/scenarios/<name>.gd, then quit with its result
##   --out=<dir>         screenshot folder (absolute path, or res:// / user://)
##   --autopilot         let the bot fly the plane during normal play
##   --seed=<int>        fixed random seed for reproducible runs

var args: Dictionary = {}
var out_dir := "user://captures"
var failures: PackedStringArray = []


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	args = parse_args(OS.get_cmdline_user_args())
	if args.has("out"):
		out_dir = str(args["out"])
	if args.has("seed"):
		seed(int(args["seed"]))
	if args.has("scenario"):
		_run_scenario.call_deferred(str(args["scenario"]))


static func parse_args(list: PackedStringArray) -> Dictionary:
	var parsed := {}
	for arg in list:
		if not arg.begins_with("--"):
			continue
		var kv := arg.substr(2).split("=", true, 1)
		parsed[kv[0]] = kv[1] if kv.size() > 1 else "true"
	return parsed


func has_flag(flag: String) -> bool:
	return args.has(flag)


## Saves exactly what the player sees (3D camera plus UI) to <out>/<shot_name>.png.
func capture(shot_name: String) -> String:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var dir := _absolute(out_dir)
	DirAccess.make_dir_recursive_absolute(dir)
	var path := dir.path_join(shot_name + ".png")
	var err := img.save_png(path)
	if err != OK:
		push_error("[capture] failed to save %s: %s" % [path, error_string(err)])
	else:
		print("[capture] %s" % path)
	return path


func wait(seconds: float) -> void:
	await get_tree().create_timer(seconds, true).timeout


func check(condition: bool, message: String) -> void:
	if condition:
		print("[check] ok: ", message)
	else:
		failures.append(message)
		push_error("[check] FAILED: " + message)


func _absolute(path: String) -> String:
	if path.begins_with("res://") or path.begins_with("user://"):
		return ProjectSettings.globalize_path(path)
	return path


func _run_scenario(scenario_name: String) -> void:
	var path := "res://tests/scenarios/%s.gd" % scenario_name
	if not ResourceLoader.exists(path):
		push_error("[scenario] not found: " + path)
		get_tree().quit(2)
		return
	print("[scenario] start: ", scenario_name)
	var scenario: Object = load(path).new()
	await scenario.run(self)
	var ok := failures.is_empty()
	print("[scenario] done: %s -> %s" % [scenario_name, "PASS" if ok else "FAIL x%d" % failures.size()])
	await Audio.shutdown()
	get_tree().quit(0 if ok else 1)
