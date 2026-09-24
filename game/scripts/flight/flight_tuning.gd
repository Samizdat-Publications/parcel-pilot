class_name FlightTuning
extends Resource
## How the plane handles. Edit data/flight.tres to tune.

@export_group("Speed")
@export var cruise_speed := 24.0
@export var boost_speed := 40.0
@export var min_speed := 14.0
## How quickly speed approaches its target (1/s).
@export var speed_response := 1.6
## Extra speed at the steepest dive, and speed lost at the steepest climb (m/s).
@export var dive_speed_gain := 9.0
@export var climb_speed_loss := 6.0

@export_group("Handling")
## Heading change at full stick (rad/s).
@export var turn_rate := 1.3
## Pitch change at full stick (rad/s).
@export var pitch_rate := 1.1
@export var max_pitch_deg := 55.0
## How quickly the nose returns to level with no pitch input (1/s).
@export var auto_level := 0.9
@export var max_bank_deg := 50.0
@export var bank_response := 4.0

@export_group("Boost")
@export var boost_drain := 0.35
@export var boost_refill := 0.06

@export_group("Crashes")
## Fraction of velocity kept after bouncing off a surface.
@export var crash_bounce := 0.55
## Minimum seconds between two crash events.
@export var crash_cooldown := 1.0
## Hits more glancing than this (0 = grazing, 1 = head-on) are just scrapes.
@export var crash_min_impact := 0.15

@export_group("World limits")
@export var ceiling := 200.0
@export var floor_y := -55.0
@export var boundary_radius := 850.0
