extends Node
## One-shot particle bursts, built entirely in code. The only texture is a soft round
## puff generated from a gradient, so there are still no image assets.

const PALETTE_CONFETTI := [Color("d9412f"), Color("fff1d8"), Color("e8b83a"), Color("2f9c95"),
	Color("4f80a9"), Color("f28fb1")]

var puff: GradientTexture2D
var _materials := {}


func _ready() -> void:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.45, Color(1, 1, 1, 0.75))
	puff = GradientTexture2D.new()
	puff.gradient = g
	puff.fill = GradientTexture2D.FILL_RADIAL
	puff.fill_from = Vector2(0.5, 0.5)
	puff.fill_to = Vector2(1.0, 0.5)
	puff.width = 64
	puff.height = 64


## A billboard material for particles: soft puff or flat card, alpha or additive.
func material(kind: String) -> StandardMaterial3D:
	if _materials.has(kind):
		return _materials[kind]
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.vertex_color_use_as_albedo = true
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.billboard_keep_scale = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	match kind:
		"puff":
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.albedo_texture = puff
		"glow":
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
			m.albedo_texture = puff
		"card":
			pass
	_materials[kind] = m
	return m


func particles(kind: String, amount: int, lifetime: float, size: float) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(size, size * (0.6 if kind == "card" else 1.0))
	p.mesh = quad
	p.material_override = material(kind)
	p.amount = amount
	p.lifetime = lifetime
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return p


func fade_ramp(color: Color, peak_alpha := 1.0) -> Gradient:
	var g := Gradient.new()
	g.set_color(0, Color(color, peak_alpha))
	g.set_color(1, Color(color, 0.0))
	return g


func shrink_curve() -> Curve:
	var c := Curve.new()
	c.add_point(Vector2(0.0, 1.0))
	c.add_point(Vector2(1.0, 0.0))
	return c


func grow_curve(from := 0.4) -> Curve:
	var c := Curve.new()
	c.add_point(Vector2(0.0, from))
	c.add_point(Vector2(1.0, 1.0))
	return c


## Fire-and-forget burst at a world position.
func burst(kind: String, where: Vector3, tint := Color.WHITE) -> void:
	var p: CPUParticles3D
	match kind:
		"confetti":
			p = particles("card", 110, 2.8, 0.45)
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
			p.emission_sphere_radius = 2.0
			p.direction = Vector3.UP
			p.spread = 180.0
			p.initial_velocity_min = 8.0
			p.initial_velocity_max = 17.0
			p.gravity = Vector3(0, -7.0, 0)
			p.damping_min = 2.0
			p.damping_max = 4.0
			p.angle_min = -180.0
			p.angle_max = 180.0
			p.angular_velocity_min = -400.0
			p.angular_velocity_max = 400.0
			var ramp := Gradient.new()
			ramp.interpolation_mode = Gradient.GRADIENT_INTERPOLATE_CONSTANT
			var offsets := PackedFloat32Array()
			for i in PALETTE_CONFETTI.size():
				offsets.append(float(i) / PALETTE_CONFETTI.size())
			ramp.offsets = offsets
			ramp.colors = PackedColorArray(PALETTE_CONFETTI)
			p.color_initial_ramp = ramp
		"sparkle", "ring", "zap":
			p = particles("glow", 48, 0.9, 0.9)
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
			p.emission_sphere_radius = 0.8 if kind == "sparkle" else 3.5
			p.spread = 180.0
			p.initial_velocity_min = 5.0
			p.initial_velocity_max = 13.0
			p.damping_min = 6.0
			p.damping_max = 9.0
			p.scale_amount_curve = shrink_curve()
			var base: Color = {"sparkle": Color(1.0, 0.82, 0.3), "ring": Color(0.45, 0.95, 1.0),
				"zap": Color(0.75, 0.85, 1.0)}[kind]
			p.color_ramp = fade_ramp(base * Color(1.6, 1.6, 1.6, 1.0))
		"dust":
			p = particles("puff", 26, 1.4, 2.2)
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
			p.emission_sphere_radius = 0.8
			p.spread = 180.0
			p.initial_velocity_min = 2.0
			p.initial_velocity_max = 6.0
			p.damping_min = 3.0
			p.damping_max = 5.0
			p.scale_amount_curve = grow_curve(0.3)
			p.color_ramp = fade_ramp(Color(0.86, 0.8, 0.74), 0.8)
		"debris":
			p = particles("card", 22, 1.6, 0.3)
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
			p.emission_sphere_radius = 0.6
			p.spread = 180.0
			p.initial_velocity_min = 6.0
			p.initial_velocity_max = 11.0
			p.gravity = Vector3(0, -14.0, 0)
			p.angular_velocity_min = -600.0
			p.angular_velocity_max = 600.0
			p.color = tint if tint != Color.WHITE else Color("9c6b3f")
	p.one_shot = true
	p.explosiveness = 0.95
	var root := get_tree().current_scene
	root.add_child(p)
	p.global_position = where
	p.emitting = true
	get_tree().create_timer(p.lifetime + 0.5, false).timeout.connect(p.queue_free)
