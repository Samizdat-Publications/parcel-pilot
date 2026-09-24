extends Node
## Headless unit test runner:
##   godot --headless --path game --scene res://tests/test_runner.tscn
## Exit code 0 when every test passes, 1 otherwise.

const UNIT_DIR := "res://tests/unit/"


func _ready() -> void:
	var total := 0
	var failed := 0
	var files := Array(DirAccess.get_files_at(UNIT_DIR))
	files.sort()
	for file: String in files:
		if not (file.begins_with("test_") and file.ends_with(".gd")):
			continue
		var script: GDScript = load(UNIT_DIR + file)
		var suite: TestCase = script.new()
		var names: Array[String] = []
		for method in script.get_script_method_list():
			var method_name: String = method["name"]
			if method_name.begins_with("test_") and not names.has(method_name):
				names.append(method_name)
		names.sort()
		for method_name in names:
			total += 1
			suite.current_test = "%s.%s" % [file.get_basename(), method_name]
			var before := suite.failures.size()
			await suite.call(method_name)
			if suite.failures.size() > before:
				failed += 1
				print("  FAIL  ", suite.current_test)
				for i in range(before, suite.failures.size()):
					print("        ", suite.failures[i])
			else:
				print("  ok    ", suite.current_test)
	print("[tests] %d passed, %d failed" % [total - failed, failed])
	await Audio.shutdown()
	get_tree().quit(1 if failed > 0 else 0)
