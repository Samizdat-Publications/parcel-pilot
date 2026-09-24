extends TestCase

var rules := GameRules.new()


func test_par_time_scales_with_distance() -> void:
	assert_near(DeliveryRules.par_time(240.0, rules), 240.0 / 24.0 * 1.25 + 5.0)
	assert_true(DeliveryRules.par_time(600.0, rules) > DeliveryRules.par_time(300.0, rules))


func test_speed_factor_curve() -> void:
	var par := 20.0
	assert_near(DeliveryRules.speed_factor(0.0, par, rules), 1.0, 0.001, "fresh parcel")
	assert_near(DeliveryRules.speed_factor(par * 0.5, par, rules), 0.75, 0.001, "half par")
	assert_near(DeliveryRules.speed_factor(par, par, rules), 0.5, 0.001, "at par")
	assert_near(DeliveryRules.speed_factor(par * 2.0, par, rules), 0.25, 0.001, "twice par")
	assert_near(DeliveryRules.speed_factor(par * 9.0, par, rules), 0.25, 0.001, "floor holds")


func test_grades_follow_par_ratio() -> void:
	assert_eq(DeliveryRules.grade(5.0, 20.0, rules), DeliveryRules.Grade.EXPRESS)
	assert_eq(DeliveryRules.grade(12.0, 20.0, rules), DeliveryRules.Grade.EXPRESS, "boundary")
	assert_eq(DeliveryRules.grade(15.0, 20.0, rules), DeliveryRules.Grade.ON_TIME)
	assert_eq(DeliveryRules.grade(20.5, 20.0, rules), DeliveryRules.Grade.LATE)


func test_time_bonus_per_grade() -> void:
	assert_near(DeliveryRules.time_bonus(DeliveryRules.Grade.EXPRESS, rules), 15.0)
	assert_near(DeliveryRules.time_bonus(DeliveryRules.Grade.ON_TIME, rules), 10.0)
	assert_near(DeliveryRules.time_bonus(DeliveryRules.Grade.LATE, rules), 5.0)


func test_crash_dents_tip_and_breaks_combo() -> void:
	var clean := DeliveryRules.evaluate(300.0, 5.0, 20.0, 0, 2, rules)
	var dented := DeliveryRules.evaluate(300.0, 5.0, 20.0, 1, 2, rules)
	assert_true(dented["tip"] < clean["tip"], "crash lowers the tip")
	assert_eq(clean["streak"], 3, "clean express extends the streak")
	assert_eq(dented["streak"], 0, "a crash resets the streak")


func test_late_delivery_breaks_combo() -> void:
	var late := DeliveryRules.evaluate(300.0, 40.0, 20.0, 0, 3, rules)
	assert_eq(late["streak"], 0)
	assert_near(late["multiplier"], 1.0)


func test_combo_multiplier_caps() -> void:
	assert_near(DeliveryRules.combo_multiplier(0, rules), 1.0)
	assert_near(DeliveryRules.combo_multiplier(1, rules), 1.25)
	assert_near(DeliveryRules.combo_multiplier(4, rules), 2.0)
	assert_near(DeliveryRules.combo_multiplier(12, rules), 2.0, 0.001, "cap")


func test_points_include_multiplier() -> void:
	var r := DeliveryRules.evaluate(300.0, 1.0, 20.0, 0, 3, rules)
	assert_eq(r["streak"], 4)
	var raw := DeliveryRules.current_tip(300.0, 1.0, 20.0, 0, rules)
	assert_eq(r["points"], roundi(raw * 2.0))


func test_tip_never_below_floor() -> void:
	var r := DeliveryRules.evaluate(300.0, 500.0, 20.0, 6, 0, rules)
	var floor_tip := DeliveryRules.base_tip(300.0, rules) * rules.tip_floor
	assert_near(float(r["tip"]), floor_tip, 1.0)


func test_rank_thresholds() -> void:
	assert_eq(DeliveryRules.rank_for(0, rules), "Trainee")
	assert_eq(DeliveryRules.rank_for(399, rules), "Trainee")
	assert_eq(DeliveryRules.rank_for(400, rules), "Courier")
	assert_eq(DeliveryRules.rank_for(1499, rules), "Ace Courier")
	assert_eq(DeliveryRules.rank_for(9000, rules), "Sky Postmaster")


func test_pick_destination_respects_exclusion() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(300, 0, 0), Vector3(0, 0, 400), Vector3(900, 0, 0)]
	for i in 300:
		var idx := DeliveryRules.pick_destination(pts, Vector3.ZERO, 1, rng, rules)
		assert_true(idx != 1 and idx >= 0 and idx < pts.size(), "drew %d" % idx)


func test_pick_destination_prefers_band() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(300, 0, 0), Vector3(0, 0, 400), Vector3(900, 0, 0)]
	var counts := [0, 0, 0, 0]
	for i in 4000:
		counts[DeliveryRules.pick_destination(pts, Vector3.ZERO, 0, rng, rules)] += 1
	assert_eq(counts[0], 0, "excluded never drawn")
	assert_true(counts[3] < counts[1] * 0.6, "off-band drawn less often: %s" % str(counts))


func test_first_leg_picks_nearest() -> void:
	var rng := RandomNumberGenerator.new()
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(300, 0, 0), Vector3(0, 0, 400), Vector3(900, 0, 0)]
	assert_eq(DeliveryRules.pick_destination(pts, Vector3(10, 0, 0), 0, rng, rules, true), 1)
