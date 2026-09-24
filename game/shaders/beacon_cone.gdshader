shader_type spatial;
// The lighthouse's sweeping beam: an additive cone that fades toward its wide end and
// along its silhouette.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

uniform vec3 color : source_color = vec3(1.0, 0.86, 0.55);
uniform float strength = 0.5;

void fragment() {
	float along = UV.y;
	float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
	ALBEDO = color;
	ALPHA = strength * (1.0 - along) * (1.0 - along) * smoothstep(0.0, 0.7, facing);
}
