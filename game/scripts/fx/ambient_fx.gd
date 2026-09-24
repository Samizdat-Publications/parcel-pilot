class_name AmbientFx
extends RefCounted
## Builders for the world's ambient effects. Islands attach them at their Blender
## sockets: FX_Smoke (chimneys), FX_Mist (waterfalls), FX_Fire (campfire),
## FX_Beacon (lighthouse) and FLAG_ meshes.

const FLAG_SHADER := preload("res://shaders/flag.gdshader")
const BEACON_SHADER := preload("res://shaders/beacon_cone.gdshader")


static func chimney_smoke() -> CPUParticles3D:
	var p := Fx.particles("puff", 14, 5.5, 1.3)
	p.direction = Vector3.UP
	p.spread = 12.0
	p.initial_velocity_min = 0.9
	p.initial_velocity_max = 1.5
	p.gravity = Vector3(0.35, 0.25, 0.1)
	p.scale_amount_min = 0.8
	p.scale_amount_max = 1.2
	p.scale_amount_curve = Fx.grow_curve(0.35)
	p.color_ramp = Fx.fade_ramp(Color(0.93, 0.9, 0.94), 0.55)
	p.local_coords = false
	return p


static func waterfall_mist() -> CPUParticles3D:
	var p := Fx.particles("puff", 18, 2.6, 3.0)
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 1.6
	p.spread = 180.0
	p.initial_velocity_min = 0.4
	p.initial_velocity_max = 1.4
	p.gravity = Vector3(0, -0.4, 0)
	p.scale_amount_curve = Fx.grow_curve(0.5)
	p.color_ramp = Fx.fade_ramp(Color(1.0, 1.0, 1.0), 0.45)
	return p


static func campfire() -> Node3D:
	var root := Node3D.new()
	var p := Fx.particles("glow", 24, 0.75, 0.7)
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 0.35
	p.direction = Vector3.UP
	p.spread = 15.0
	p.initial_velocity_min = 1.4
	p.initial_velocity_max = 2.6
	p.scale_amount_curve = Fx.shrink_curve()
	var g := Gradient.new()
	g.set_color(0, Color(1.6, 1.3, 0.5, 1.0))
	g.set_color(1, Color(1.2, 0.25, 0.05, 0.0))
	p.color_ramp = g
	root.add_child(p)
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.62, 0.3)
	light.omni_range = 9.0
	light.set_script(preload("res://scripts/fx/flicker.gd"))
	root.add_child(light)
	return root


## A cone of light that sweeps around the lighthouse lamp, plus the light it casts.
static func beacon() -> Node3D:
	var pivot := Node3D.new()
	pivot.set_script(preload("res://scripts/fx/beacon_sweep.gd"))
	for side in [-1.0, 1.0]:
		var cone := MeshInstance3D.new()
		var mesh := CylinderMesh.new()
		mesh.top_radius = 0.4
		mesh.bottom_radius = 4.5
		mesh.height = 46.0
		mesh.radial_segments = 16
		mesh.cap_top = false
		mesh.cap_bottom = false
		var mat := ShaderMaterial.new()
		mat.shader = BEACON_SHADER
		mesh.material = mat
		cone.mesh = mesh
		cone.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		cone.rotation = Vector3(side * PI * 0.5, 0.0, 0.0)
		cone.position = Vector3(0.0, 0.0, -side * 23.0)
		pivot.add_child(cone)
	var spot := SpotLight3D.new()
	spot.light_color = Color(1.0, 0.86, 0.55)
	spot.light_energy = 6.0
	spot.spot_range = 90.0
	spot.spot_angle = 9.0
	pivot.add_child(spot)
	return pivot


## Swaps a Blender flag's material for the waving shader, keeping its palette color.
static func wave_flag(flag: MeshInstance3D) -> void:
	var color := Color(0.85, 0.28, 0.23)
	if flag.mesh != null and flag.mesh.get_surface_count() > 0:
		var src := flag.mesh.surface_get_material(0) as StandardMaterial3D
		if src != null:
			color = src.albedo_color
	var mat := ShaderMaterial.new()
	mat.shader = FLAG_SHADER
	mat.set_shader_parameter("albedo", color)
	flag.material_override = mat
