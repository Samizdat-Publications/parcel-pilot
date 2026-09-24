class_name DeliveryDirector
extends Node
## Runs the chain of deliveries: picks each destination, arms its hoop, times the leg,
## counts crashes, and scores the drop with DeliveryRules when the hoop is threaded.

signal leg_started(island: Island, distance: float, par: float)
signal delivered(result: Dictionary)

@export var rules: GameRules = preload("res://data/rules.tres")

var islands: Array[Island] = []
var hub: Island
var current: Island
var leg_distance := 0.0
var leg_par := 0.0
var leg_elapsed := 0.0
var leg_crashes := 0
var streak := 0
var rng := RandomNumberGenerator.new()


func setup(all_islands: Array[Island], hub_island: Island) -> void:
	hub = hub_island
	islands.clear()
	for island in all_islands:
		if island.is_destination and island.hoop != null:
			islands.append(island)
			island.hoop_passed.connect(_on_hoop_passed)
	if Dev.args.has("seed"):
		rng.seed = int(Dev.args["seed"])
	else:
		rng.randomize()


## Start of a scored shift: the first leg leaves from the hub and is a short one.
func begin_shift(from: Vector3) -> void:
	streak = 0
	_start_leg(from, islands.find(hub), true)


## Unscored flying (title screen, results backdrop): any destination will do.
func begin_free_flight(from: Vector3) -> void:
	streak = 0
	_start_leg(from, -1, false)


## Developer/scenario hook: make a specific island the next destination.
func force_destination(island: Island, from: Vector3) -> void:
	if current != null:
		current.set_delivery_active(false)
	current = island
	current.set_delivery_active(true)
	leg_distance = from.distance_to(current.delivery_position())
	leg_par = DeliveryRules.par_time(leg_distance, rules)
	leg_elapsed = 0.0
	leg_crashes = 0
	leg_started.emit(current, leg_distance, leg_par)


func register_crash() -> void:
	leg_crashes += 1
	streak = 0


func current_tip() -> float:
	return DeliveryRules.current_tip(leg_distance, leg_elapsed, leg_par, leg_crashes, rules)


func tip_fraction() -> float:
	return current_tip() / maxf(DeliveryRules.base_tip(leg_distance, rules), 1.0)


func combo_multiplier() -> float:
	return DeliveryRules.combo_multiplier(streak, rules)


func _physics_process(delta: float) -> void:
	if current != null and Game.state != Game.State.COUNTDOWN:
		leg_elapsed += delta


func _start_leg(from: Vector3, exclude: int, nearest: bool, retire_previous := false) -> void:
	var positions: Array[Vector3] = []
	for island in islands:
		positions.append(island.delivery_position())
	var idx := DeliveryRules.pick_destination(positions, from, exclude, rng, rules, nearest)
	if current != null:
		if retire_previous:
			current.retire_delivery()
		else:
			current.set_delivery_active(false)
	current = islands[idx]
	current.set_delivery_active(true)
	leg_distance = from.distance_to(current.delivery_position())
	leg_par = DeliveryRules.par_time(leg_distance, rules)
	leg_elapsed = 0.0
	leg_crashes = 0
	leg_started.emit(current, leg_distance, leg_par)


func _on_hoop_passed(island: Island) -> void:
	if island != current:
		return
	var result := DeliveryRules.evaluate(leg_distance, leg_elapsed, leg_par, leg_crashes, streak, rules)
	streak = int(result["streak"])
	result["island"] = island
	result["position"] = island.delivery_position()
	delivered.emit(result)
	_start_leg(island.delivery_position(), islands.find(island), false, true)
