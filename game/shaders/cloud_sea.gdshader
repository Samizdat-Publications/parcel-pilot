shader_type spatial;
// The sea of clouds under the archipelago. Billowy displacement from two drifting
// noise layers (sampled in world space, so the mesh can follow the camera without
// swimming), wrap lighting for soft volume, and a warm rim where it faces the sun.
render_mode diffuse_lambert_wrap, specular_disabled, shadows_disabled;

uniform vec3 top_color : source_color = vec3(0.92, 0.87, 0.88);
uniform vec3 deep_color : source_color = vec3(0.5, 0.48, 0.76);
uniform float height = 16.0;
uniform float scale = 0.0035;
uniform vec2 drift = vec2(0.0025, 0.0012);
uniform sampler2D noise_a : repeat_enable, filter_linear_mipmap;
uniform sampler2D noise_b : repeat_enable, filter_linear_mipmap;
uniform float backlight_strength = 0.2;

varying float billow;

float field(vec2 p, float t) {
	float a = texture(noise_a, p * scale + t * drift).r;
	float b = texture(noise_b, p * scale * 3.3 - t * drift * 1.6).r;
	return pow(clamp(a * 0.78 + b * 0.32, 0.0, 1.0), 1.7);
}

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float h = field(wp.xz, TIME);
	VERTEX.y += h * height;
	float e = 4.0;
	float hx = field(wp.xz + vec2(e, 0.0), TIME) * height;
	float hz = field(wp.xz + vec2(0.0, e), TIME) * height;
	NORMAL = normalize(vec3(h * height - hx, e, h * height - hz));
	billow = h;
}

void fragment() {
	ALBEDO = mix(deep_color, top_color, smoothstep(0.05, 0.6, billow));
	ROUGHNESS = 1.0;
	BACKLIGHT = vec3(backlight_strength);
}
