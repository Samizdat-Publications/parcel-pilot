shader_type spatial;
// Destination beacon: an additive light pillar that fades at both ends, softens at
// its silhouette, and pulses upward. Ignores fog so it reads from across the map.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 color : source_color = vec3(1.0, 0.74, 0.34);
uniform float intensity = 1.4;
uniform float band_speed = 2.2;

void fragment() {
	float v = UV.y;
	float ends = smoothstep(0.0, 0.3, v) * smoothstep(1.0, 0.5, v);
	float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float soft = smoothstep(0.0, 0.8, facing);
	float bands = 0.72 + 0.28 * sin(v * 140.0 + TIME * band_speed * 6.0);
	ALBEDO = color * intensity * bands;
	ALPHA = ends * soft * 0.6;
}
