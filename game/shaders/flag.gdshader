shader_type spatial;
// Waving cloth for FLAG_ meshes. The Blender flag is built with its origin at the pole
// top, so local +X is the distance along the flag: the ripple grows with it.
render_mode cull_disabled;

uniform vec3 albedo : source_color = vec3(0.85, 0.28, 0.23);
uniform float amplitude = 0.32;
uniform float wavelength = 1.7;
uniform float speed = 3.2;
uniform float flag_length = 3.7;

void vertex() {
	float d = max(VERTEX.x, 0.0) / flag_length;
	float phase = VERTEX.x * wavelength - TIME * speed;
	VERTEX.z += sin(phase) * amplitude * d;
	VERTEX.y += sin(phase * 0.5 + 1.3) * 0.08 * d;
	NORMAL = normalize(NORMAL + vec3(-cos(phase) * amplitude * wavelength * d, 0.0, 0.0));
}

void fragment() {
	ALBEDO = albedo;
	ROUGHNESS = 0.9;
}
