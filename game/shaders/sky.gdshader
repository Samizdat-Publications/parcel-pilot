shader_type sky;
// Golden-hour sky: a zenith-to-horizon gradient that warms toward the sun and turns
// lavender away from it, a soft sun with an HDR disc (so glow picks it up), and a
// layer of wispy high cloud. Static on purpose, so radiance is only baked once.
// Every pow() base is clamped: the radiance bake samples exactly straight up, where
// 1.0 - dir.y can dip below zero and pow() of a negative base is NaN (black world).

uniform vec3 zenith_color : source_color = vec3(0.16, 0.33, 0.7);
uniform vec3 upper_color : source_color = vec3(0.4, 0.58, 0.9);
uniform vec3 horizon_sun_color : source_color = vec3(1.0, 0.72, 0.48);
uniform vec3 horizon_away_color : source_color = vec3(0.78, 0.66, 0.86);
uniform vec3 below_color : source_color = vec3(0.74, 0.66, 0.82);
uniform float horizon_sharpness : hint_range(0.5, 8.0) = 3.2;
uniform vec3 sun_tint : source_color = vec3(1.0, 0.84, 0.58);
uniform float sun_disc_size : hint_range(0.0005, 0.02) = 0.0026;
uniform float sun_glow : hint_range(0.0, 2.0) = 0.45;
uniform sampler2D cloud_noise : filter_linear_mipmap, repeat_enable;
uniform float cloud_coverage : hint_range(0.0, 1.0) = 0.5;
uniform float cloud_opacity : hint_range(0.0, 1.0) = 0.6;

void sky() {
	vec3 dir = EYEDIR;
	vec3 sun = LIGHT0_ENABLED ? LIGHT0_DIRECTION : vec3(0.0, 0.3, -1.0);
	float sun_dot = clamp(dot(dir, sun), 0.0, 1.0);
	vec2 flat_dir = normalize(dir.xz + vec2(1e-5));
	vec2 flat_sun = normalize(sun.xz + vec2(1e-5));
	float toward_sun = clamp(dot(flat_dir, flat_sun) * 0.5 + 0.5, 0.0, 1.0);
	vec3 horizon = mix(horizon_away_color, horizon_sun_color, pow(toward_sun, 1.6));

	vec3 col;
	if (dir.y >= 0.0) {
		float t = pow(clamp(1.0 - dir.y, 0.0, 1.0), horizon_sharpness);
		vec3 top = mix(zenith_color, upper_color, smoothstep(0.0, 0.7, clamp(1.0 - dir.y, 0.0, 1.0)));
		col = mix(top, horizon, t);
	} else {
		col = mix(horizon, below_color, smoothstep(0.0, 0.3, -dir.y));
	}

	if (dir.y > 0.0) {
		vec2 uv = dir.xz / (dir.y + 0.12) * 0.22;
		float n = texture(cloud_noise, uv * 0.3 + vec2(0.13, 0.0)).r * 0.7
			+ texture(cloud_noise, uv * 1.3 + vec2(0.4, 0.7)).r * 0.3;
		float c = smoothstep(cloud_coverage, cloud_coverage + 0.28, n) * smoothstep(0.02, 0.3, dir.y);
		vec3 cloud_col = mix(vec3(1.0, 0.92, 0.9), sun_tint * 1.35, pow(sun_dot, 5.0));
		col = mix(col, cloud_col, c * cloud_opacity);
	}

	col += sun_tint * pow(sun_dot, 10.0) * sun_glow;
	col += sun_tint * pow(sun_dot, 90.0) * 0.8;
	float disc = smoothstep(1.0 - sun_disc_size, 1.0 - sun_disc_size * 0.6, sun_dot);
	col = mix(col, sun_tint * 6.0, disc);
	COLOR = col;
}
