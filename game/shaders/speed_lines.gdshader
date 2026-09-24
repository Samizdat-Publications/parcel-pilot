shader_type canvas_item;
// Screen-space speed lines for boosting: thin radial streaks that race outward from
// the center, stronger toward the screen edge. `intensity` 0..1 comes from the plane.

uniform float intensity : hint_range(0.0, 1.0) = 0.0;
uniform float line_count = 90.0;
uniform vec4 tint : source_color = vec4(1.0, 0.98, 0.94, 1.0);

float hash(float n) {
	return fract(sin(n * 12.9898) * 43758.5453);
}

void fragment() {
	vec2 aspect = vec2(SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x, 1.0);
	vec2 p = (SCREEN_UV - 0.5) * aspect;
	float r = length(p);
	float a = atan(p.y, p.x) / TAU + 0.5;
	float lane = floor(a * line_count);
	float h = hash(lane);
	float across = abs(fract(a * line_count) - 0.5) * 2.0;
	float thin = smoothstep(0.35 + 0.4 * h, 0.0, across);
	float travel = fract(r * (1.6 + h) - TIME * (1.4 + 1.8 * h) + h * 7.0);
	float dash = smoothstep(0.0, 0.2, travel) * smoothstep(0.75, 0.3, travel);
	float edge = smoothstep(0.18, 0.62, r);
	float keep = step(0.45, h);
	COLOR = vec4(tint.rgb, thin * dash * edge * keep * intensity * 0.55);
}
