shader_type spatial;
// Every palette material in one shader. At import (pipeline/post_import.gd) each mesh's
// palette surfaces are merged into one, and each face carries its palette entry in its
// vertices: the sRGB color and the roughness in COLOR, metallic and glow in UV2. So a
// mesh is one draw call instead of one per color, which matters most in a browser.
// Lighting is the same as a StandardMaterial3D's (Burley diffuse, Schlick-GGX specular).
render_mode cull_disabled;

vec3 srgb_to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void fragment() {
	vec3 albedo = srgb_to_linear(COLOR.rgb);
	ALBEDO = albedo;
	ROUGHNESS = COLOR.a;
	METALLIC = UV2.x;
	EMISSION = albedo * UV2.y;
}
