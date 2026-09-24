class_name Autopilot
extends RefCounted
## A bot pilot that delivers parcels. It follows the active hoop's axis line with pure
## pursuit, threads the hoop, and climbs or dives around anything in its way.
## Used for the title-screen attract mode, automated tests, and --autopilot.

const CARROT := 30.0            ## pursuit look-ahead along the approach line (m)
const MAX_CARROT_OUT := 90.0    ## farthest out the carrot may sit from the hoop (m)
const EXIT_DIST := 40.0         ## aim this far past the hoop once committed (m)
const COMMIT_DIST := 14.0       ## closer than this along the axis: aim through the hoop
const PROBE_DIST := 55.0        ## obstacle ray length (m)

var director: DeliveryDirector
var _target: Island
var _side := 1.0


func get_controls(plane: MailPlane) -> Vector3:
	var island := director.current if director != null else null
	if island == null or island.hoop == null:
		return Vector3.ZERO
	var hoop_pos := island.hoop.global_position
	var axis := -island.hoop.global_basis.z
	var rel := plane.global_position - hoop_pos
	if island != _target:
		_target = island
		_side = 1.0 if rel.dot(axis) >= 0.0 else -1.0
	var along := rel.dot(axis * _side)
	if along < -12.0:
		# Flew past without threading it: come around from this side instead.
		_side = -_side
		along = -along
	var goal: Vector3
	if along > COMMIT_DIST:
		goal = hoop_pos + axis * _side * clampf(along - CARROT, 0.0, MAX_CARROT_OUT)
	else:
		goal = hoop_pos - axis * _side * EXIT_DIST
	return _steer(plane, goal)


func _steer(plane: MailPlane, goal: Vector3) -> Vector3:
	var to := goal - plane.global_position
	var desired_yaw := atan2(-to.x, -to.z)
	var yaw_err := wrapf(desired_yaw - plane.yaw, -PI, PI)
	var turn := clampf(-yaw_err * 2.4, -1.0, 1.0)
	var horizontal := Vector2(to.x, to.z).length()
	var desired_pitch := clampf(atan2(to.y, horizontal), -0.85, 0.85)
	var climb := clampf((desired_pitch - plane.pitch) * 3.0, -1.0, 1.0)

	var avoid := _avoidance(plane)
	if avoid != 0.0:
		climb = avoid
	var boost := 1.0 if plane.boost > 0.45 and absf(yaw_err) < 0.2 and to.length() > 160.0 else 0.0
	return Vector3(turn, climb, boost)


## Returns +1 (climb) or -1 (dive) when something is dead ahead, 0 when clear.
func _avoidance(plane: MailPlane) -> float:
	var space := plane.get_world_3d().direct_space_state
	var from := plane.global_position
	for dir in [plane.forward(), (plane.forward() + Vector3.DOWN * 0.35).normalized()]:
		var query := PhysicsRayQueryParameters3D.create(from, from + dir * PROBE_DIST, 1, [plane.get_rid()])
		var hit := space.intersect_ray(query)
		if not hit.is_empty():
			var normal: Vector3 = hit["normal"]
			return -1.0 if normal.y < -0.35 else 1.0
	return 0.0
