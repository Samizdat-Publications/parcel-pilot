extends Node
## Plays every sound in the game (all synthesized by tools/build_audio.py).
## One-shots come from a small voice pool; the engine and wind loops follow the plane;
## the music ducks under fanfares. Bus volumes come from the saved settings.
## Streams are loaded in _ready, not preloaded: autoloads compile before a fresh
## clone's first import has produced the audio resources.

const SOUNDS := {
	"deliver": "res://assets/audio/deliver.wav",
	"express": "res://assets/audio/express.wav",
	"new_parcel": "res://assets/audio/new_parcel.wav",
	"ring": "res://assets/audio/ring.wav",
	"boost": "res://assets/audio/boost.wav",
	"crash": "res://assets/audio/crash.wav",
	"stamp": "res://assets/audio/stamp.wav",
	"thunder": "res://assets/audio/thunder.wav",
	"zap": "res://assets/audio/zap.wav",
	"tick": "res://assets/audio/tick.wav",
	"go": "res://assets/audio/go.wav",
	"clock_tick": "res://assets/audio/clock_tick.wav",
	"ui_click": "res://assets/audio/ui_click.wav",
	"ui_move": "res://assets/audio/ui_move.wav",
	"parachute": "res://assets/audio/parachute.wav",
	"results": "res://assets/audio/results.wav",
	"new_best": "res://assets/audio/new_best.wav",
}
const ENGINE := "res://assets/audio/engine_loop.wav"
const WIND := "res://assets/audio/wind_loop.wav"
const MUSIC := "res://assets/audio/music.wav"
const VOICES := 12
const MUSIC_DB := -9.0

var _streams := {}
var _closed := false
var _pool: Array[AudioStreamPlayer] = []
var _next_voice := 0
var _engine: AudioStreamPlayer
var _wind: AudioStreamPlayer
var _music: AudioStreamPlayer
var _duck := 0.0
var _music_target_db := MUSIC_DB


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for bus_name in ["Music", "SFX"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			AudioServer.add_bus()
			var idx := AudioServer.bus_count - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")
	for key: String in SOUNDS:
		_streams[key] = load(SOUNDS[key])
	for i in VOICES:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)
	_engine = _loop_player(load(ENGINE), "SFX", -80.0)
	_wind = _loop_player(load(WIND), "SFX", -80.0)
	_music = _loop_player(load(MUSIC), "Music", MUSIC_DB)
	apply_settings()
	Save.settings_changed.connect(apply_settings)


func apply_settings() -> void:
	_set_bus("Master", float(Save.settings["master_volume"]))
	_set_bus("Music", float(Save.settings["music_volume"]))
	_set_bus("SFX", float(Save.settings["sfx_volume"]))


## Fire-and-forget sound. `pitch_jitter` keeps repeated sounds from sounding robotic.
func play(sound: String, volume_db := 0.0, pitch := 1.0, pitch_jitter := 0.0) -> void:
	if _closed:
		return
	if not _streams.has(sound):
		push_warning("unknown sound: " + sound)
		return
	var p := _pool[_next_voice]
	_next_voice = (_next_voice + 1) % VOICES
	p.stream = _streams[sound]
	p.volume_db = volume_db
	p.pitch_scale = pitch * (1.0 + randf_range(-pitch_jitter, pitch_jitter))
	p.play()


## Lowers the music for a moment so a fanfare can shine.
func duck(amount_db: float, seconds: float) -> void:
	_duck = maxf(_duck, amount_db)
	get_tree().create_timer(seconds, true, false, true).timeout.connect(func() -> void: _duck = 0.0)


func set_music_level(db: float) -> void:
	_music_target_db = db


## Called every frame by the game with the plane's state.
func set_flight(speed_ratio: float, boosting: bool, mix: float) -> void:
	var engine_db := lerpf(-9.0, -4.0, speed_ratio) + (2.0 if boosting else 0.0)
	_engine.volume_db = engine_db + linear_to_db(clampf(mix, 0.0001, 1.0))
	_engine.pitch_scale = lerpf(0.85, 1.45, speed_ratio) + (0.08 if boosting else 0.0)
	var wind := lerpf(0.12, 0.55, speed_ratio) * mix
	_wind.volume_db = linear_to_db(maxf(wind, 0.0001))
	_wind.pitch_scale = lerpf(0.9, 1.25, speed_ratio)


func _process(delta: float) -> void:
	var goal := _music_target_db - _duck
	_music.volume_db = move_toward(_music.volume_db, goal, delta * 24.0)


## Quitting while loops play leaves their playbacks inside the audio server, which then
## reports the streams as leaked. Stop everything and drop the streams; callers that
## quit on purpose (tests, scenarios) wait a few frames after this so the mixer lets go.
func stop_all() -> void:
	_closed = true
	var players: Array[AudioStreamPlayer] = [_engine, _wind, _music]
	players.append_array(_pool)
	for p in players:
		if p != null:
			p.stop()
			p.stream = null
	# Positional players that live in the world (storm thunder) join this group.
	if is_inside_tree():
		for node in get_tree().get_nodes_in_group("audio_players"):
			node.call("stop")
			node.set("stream", null)
	_streams.clear()


## Stops everything and gives the mixer thread real (wall-clock) time to release the
## playbacks. Headless runs at a fixed fps race through frames faster than real time,
## so waiting a few frames is not enough.
func shutdown() -> void:
	stop_all()
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 250:
		await get_tree().process_frame


func _exit_tree() -> void:
	stop_all()


func _loop_player(stream: AudioStreamWAV, bus: String, db: float) -> AudioStreamPlayer:
	if stream.loop_mode == AudioStreamWAV.LOOP_DISABLED:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = int(stream.get_length() * stream.mix_rate)
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.bus = bus
	p.volume_db = db
	add_child(p)
	p.play()
	return p


func _set_bus(bus_name: String, linear: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx != -1:
		AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(linear, 0.0001)))
