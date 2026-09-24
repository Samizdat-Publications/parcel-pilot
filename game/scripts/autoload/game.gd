extends Node
## The shift: state machine, clock, and scoreboard. Scenes react to its signals and
## report events back through record_delivery / collect_stamp / add_time.

enum State { TITLE, COUNTDOWN, PLAYING, PAUSED, RESULTS }

signal state_changed(state: State, previous: State)
signal score_changed(score: int, delta: int)
signal clock_changed(seconds: float)
signal time_added(seconds: float, reason: String)
signal countdown_tick(value: int)
signal delivery_recorded(result: Dictionary)
signal stamp_collected(where: Vector3)
signal shift_ended(new_best: bool)

var rules: GameRules = preload("res://data/rules.tres")
var state: State = State.TITLE
var score := 0
var time_left := 0.0
var shift_time := 0.0
var deliveries := 0
var stamps := 0
var crashes := 0
var best_streak := 0
var new_best := false
var _countdown := 0.0


func _process(delta: float) -> void:
	match state:
		State.COUNTDOWN:
			var before := ceili(_countdown)
			_countdown -= delta
			var after := ceili(maxf(_countdown, 0.0))
			if after != before:
				countdown_tick.emit(after)
			if _countdown <= 0.0:
				_set_state(State.PLAYING)
		State.PLAYING:
			time_left = maxf(0.0, time_left - delta)
			shift_time += delta
			clock_changed.emit(time_left)
			if time_left <= 0.0:
				end_shift()


func begin_shift() -> void:
	get_tree().paused = false
	score = 0
	deliveries = 0
	stamps = 0
	crashes = 0
	best_streak = 0
	shift_time = 0.0
	new_best = false
	time_left = rules.shift_seconds
	_countdown = rules.countdown_seconds
	_set_state(State.COUNTDOWN)
	score_changed.emit(score, 0)
	clock_changed.emit(time_left)
	countdown_tick.emit(ceili(_countdown))


func end_shift() -> void:
	if state != State.PLAYING and state != State.PAUSED:
		return
	get_tree().paused = false
	new_best = Save.submit(score, deliveries)
	_set_state(State.RESULTS)
	shift_ended.emit(new_best)


func to_title() -> void:
	get_tree().paused = false
	_set_state(State.TITLE)


func pause() -> void:
	if state == State.PLAYING:
		get_tree().paused = true
		_set_state(State.PAUSED)


func resume() -> void:
	if state == State.PAUSED:
		get_tree().paused = false
		_set_state(State.PLAYING)


func is_playing() -> bool:
	return state == State.PLAYING


func record_delivery(result: Dictionary) -> void:
	deliveries += 1
	best_streak = maxi(best_streak, int(result["streak"]))
	add_score(int(result["points"]))
	add_time(float(result["time_bonus"]), String(result["grade_name"]))
	delivery_recorded.emit(result)


func record_crash() -> void:
	crashes += 1


func collect_stamp(where: Vector3) -> void:
	stamps += 1
	add_score(rules.stamp_points)
	add_time(rules.stamp_seconds, "Stamp")
	stamp_collected.emit(where)


func add_score(points: int) -> void:
	score += points
	score_changed.emit(score, points)


func add_time(seconds: float, reason: String) -> void:
	time_left = maxf(0.0, time_left + seconds)
	time_added.emit(seconds, reason)
	clock_changed.emit(time_left)


func rank() -> String:
	return DeliveryRules.rank_for(score, rules)


func _set_state(next: State) -> void:
	if next == state:
		return
	var previous := state
	state = next
	state_changed.emit(next, previous)
