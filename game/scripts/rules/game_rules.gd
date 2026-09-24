class_name GameRules
extends Resource
## Scoring and pacing numbers for a shift. Edit data/rules.tres to tune.

@export_group("Shift")
@export var shift_seconds := 90.0
@export var countdown_seconds := 3.0
@export var fall_penalty_seconds := 5.0

@export_group("Par time")
## Par = distance / par_speed * par_slack + par_base (seconds).
@export var par_speed := 24.0
@export var par_slack := 1.25
@export var par_base := 5.0

@export_group("Tips")
@export var tip_base := 60.0
@export var tip_per_meter := 0.12
## Fraction of the tip left when the par time runs out.
@export var tip_at_par := 0.5
## The tip never drops below this fraction, however late.
@export var tip_floor := 0.25
## Each crash on the current leg multiplies the tip by this.
@export var crash_tip_factor := 0.85

@export_group("Grades and time bonus")
## Delivered within this fraction of par counts as Express.
@export var express_ratio := 0.6
@export var bonus_express := 15.0
@export var bonus_on_time := 10.0
@export var bonus_late := 5.0

@export_group("Combo")
@export var combo_step := 0.25
@export var combo_cap := 4

@export_group("Collectibles")
@export var stamp_points := 25
@export var stamp_seconds := 3.0
@export var stamp_respawn := 45.0
@export var ring_boost := 0.35

@export_group("Destinations")
@export var preferred_min_distance := 250.0
@export var preferred_max_distance := 600.0
## Weight of destinations outside the preferred band (inside it the weight is 1).
@export var off_band_weight := 0.35

@export_group("Ranks")
@export var rank_thresholds: PackedInt32Array = PackedInt32Array([0, 400, 900, 1500])
@export var rank_names: PackedStringArray = PackedStringArray(["Trainee", "Courier", "Ace Courier", "Sky Postmaster"])
