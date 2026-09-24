extends Node
## Persists records and settings in user://save.cfg. Automated runs (any --scenario)
## use a throwaway file so they never touch the player's best score.

signal settings_changed

const PLAYER_PATH := "user://save.cfg"
const TEST_PATH := "user://save_test.cfg"

var path := PLAYER_PATH
var best_score := 0
var best_deliveries := 0
var settings := {
	"invert_pitch": false,
	"master_volume": 1.0,
	"music_volume": 0.7,
	"sfx_volume": 0.9,
	"fullscreen": false,
}


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--scenario"):
			path = TEST_PATH
			DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_PATH))
	load_file()


func load_file() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(path) != OK:
		return
	best_score = cfg.get_value("records", "best_score", 0)
	best_deliveries = cfg.get_value("records", "best_deliveries", 0)
	for key in settings:
		settings[key] = cfg.get_value("settings", key, settings[key])


func save_file() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("records", "best_score", best_score)
	cfg.set_value("records", "best_deliveries", best_deliveries)
	for key in settings:
		cfg.set_value("settings", key, settings[key])
	var err := cfg.save(path)
	if err != OK:
		push_warning("could not save %s: %s" % [path, error_string(err)])


## Records a finished shift. Returns true when it beats the best score.
func submit(score: int, deliveries: int) -> bool:
	var is_best := score > best_score
	if is_best:
		best_score = score
	best_deliveries = maxi(best_deliveries, deliveries)
	save_file()
	return is_best


func set_setting(key: String, value: Variant) -> void:
	settings[key] = value
	save_file()
	settings_changed.emit()
