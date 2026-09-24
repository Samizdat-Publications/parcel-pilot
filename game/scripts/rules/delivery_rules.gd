class_name DeliveryRules
extends RefCounted
## Pure scoring, pacing and destination rules. No scene access: everything here is
## unit tested in tests/unit/test_delivery_rules.gd.

enum Grade { EXPRESS, ON_TIME, LATE }

const GRADE_NAMES := {
	Grade.EXPRESS: "Express",
	Grade.ON_TIME: "On time",
	Grade.LATE: "Late",
}


static func par_time(distance: float, rules: GameRules) -> float:
	return distance / rules.par_speed * rules.par_slack + rules.par_base


static func base_tip(distance: float, rules: GameRules) -> float:
	return rules.tip_base + rules.tip_per_meter * distance


## 1.0 at pickup, tip_at_par at par, tip_floor at twice par and beyond.
static func speed_factor(elapsed: float, par: float, rules: GameRules) -> float:
	if par <= 0.0:
		return 1.0
	var r := elapsed / par
	if r <= 1.0:
		return lerpf(1.0, rules.tip_at_par, r)
	return maxf(rules.tip_floor, lerpf(rules.tip_at_par, rules.tip_floor, r - 1.0))


static func damage_factor(crashes: int, rules: GameRules) -> float:
	return pow(rules.crash_tip_factor, maxi(crashes, 0))


## The tip as it stands right now (what the HUD shows while flying).
static func current_tip(distance: float, elapsed: float, par: float, crashes: int, rules: GameRules) -> float:
	var factor := maxf(rules.tip_floor, speed_factor(elapsed, par, rules) * damage_factor(crashes, rules))
	return base_tip(distance, rules) * factor


static func grade(elapsed: float, par: float, rules: GameRules) -> Grade:
	var r := elapsed / maxf(par, 0.001)
	if r <= rules.express_ratio:
		return Grade.EXPRESS
	if r <= 1.0:
		return Grade.ON_TIME
	return Grade.LATE


static func time_bonus(g: Grade, rules: GameRules) -> float:
	match g:
		Grade.EXPRESS:
			return rules.bonus_express
		Grade.ON_TIME:
			return rules.bonus_on_time
	return rules.bonus_late


static func next_streak(streak: int, g: Grade, crashed: bool) -> int:
	if crashed or g == Grade.LATE:
		return 0
	return streak + 1


static func combo_multiplier(streak: int, rules: GameRules) -> float:
	return 1.0 + rules.combo_step * clampi(streak, 0, rules.combo_cap)


## Everything that happens when a parcel arrives, as one dictionary.
static func evaluate(distance: float, elapsed: float, par: float, crashes: int, streak_before: int, rules: GameRules) -> Dictionary:
	var g := grade(elapsed, par, rules)
	var streak := next_streak(streak_before, g, crashes > 0)
	var tip := current_tip(distance, elapsed, par, crashes, rules)
	var mult := combo_multiplier(streak, rules)
	return {
		"grade": g,
		"grade_name": GRADE_NAMES[g],
		"tip": roundi(tip),
		"multiplier": mult,
		"points": roundi(tip * mult),
		"time_bonus": time_bonus(g, rules),
		"streak": streak,
		"elapsed": elapsed,
		"par": par,
		"crashes": crashes,
	}


static func rank_for(score: int, rules: GameRules) -> String:
	var rank := rules.rank_names[0]
	for i in rules.rank_thresholds.size():
		if score >= rules.rank_thresholds[i] and i < rules.rank_names.size():
			rank = rules.rank_names[i]
	return rank


## Picks the index of the next destination.
## `positions` are candidate hoop positions; `exclude` is an index that may not be chosen
## (-1 for none). With `nearest` the closest candidate wins (used for the gentle first leg).
## Otherwise candidates inside the preferred distance band are weighted 1, others
## off_band_weight, and one is drawn with `rng`.
static func pick_destination(positions: Array[Vector3], from: Vector3, exclude: int, rng: RandomNumberGenerator, rules: GameRules, nearest := false) -> int:
	var best := -1
	var best_d := INF
	var weights: Array[float] = []
	var total := 0.0
	for i in positions.size():
		var d := from.distance_to(positions[i])
		var w := 0.0
		if i != exclude:
			if nearest and d < best_d:
				best_d = d
				best = i
			var in_band := d >= rules.preferred_min_distance and d <= rules.preferred_max_distance
			w = 1.0 if in_band else rules.off_band_weight
		weights.append(w)
		total += w
	if nearest or total <= 0.0:
		return best
	var roll := rng.randf() * total
	for i in weights.size():
		roll -= weights[i]
		if roll <= 0.0 and weights[i] > 0.0:
			return i
	for i in range(weights.size() - 1, -1, -1):
		if weights[i] > 0.0:
			return i
	return -1
