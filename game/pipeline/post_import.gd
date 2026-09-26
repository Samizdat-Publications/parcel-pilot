@tool
extends EditorScenePostImport
## Runs on every Blender-built .glb at import time (wired in project.godot through
## [importer_defaults]). Blender stays the source of truth for geometry and palette
## colors; this applies engine-side material settings, keyed by palette name, then merges
## each mesh's palette surfaces into one surface for shaders/palette.gdshader.

const PALETTE_MATERIAL := preload("res://shaders/palette_material.tres")

## Palette materials that glow, and how strongly (emission energy multiplier).
const EMISSION_ENERGY := {
	"window": 2.2,
	"lamp": 4.0,
	"crystal": 3.0,
	"boost": 4.0,
	"beacon": 5.0,
	"bolt": 12.0,
	"nav_red": 3.0,
	"nav_green": 3.0,
	"gold": 0.25,
}
## Soft, matte, wrap-lit materials (cloud puffs read as volume instead of plastic).
const SOFT := ["cloud", "cloud_shade", "storm", "storm_dark"]


func _post_import(scene: Node) -> Object:
	_visit(scene)
	return scene


func _visit(node: Node) -> void:
	var mesh_instance := node as MeshInstance3D
	if mesh_instance != null and mesh_instance.mesh != null:
		for i in mesh_instance.mesh.get_surface_count():
			var mat := mesh_instance.mesh.surface_get_material(i) as StandardMaterial3D
			if mat != null:
				_tweak(mat)
		if mesh_instance.name.begins_with("BOLT_") or mesh_instance.name == "Roots":
			mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_merge_palette(mesh_instance)
	for child in node.get_children():
		_visit(child)


func _tweak(mat: StandardMaterial3D) -> void:
	var key := mat.resource_name
	if EMISSION_ENERGY.has(key):
		mat.emission_enabled = true
		mat.emission_energy_multiplier = EMISSION_ENERGY[key]
	if key in SOFT:
		mat.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
		mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
		mat.roughness = 1.0
		mat.rim_enabled = true
		mat.rim = 0.35
		mat.rim_tint = 0.6
	match key:
		"water":
			# Opaque (it was 82% alpha), so it merges with the rest of the palette.
			mat.roughness = 0.08
			mat.emission_enabled = true
			mat.emission = Color(0.25, 0.55, 0.62)
			mat.emission_energy_multiplier = 0.35
		"glass":
			mat.roughness = 0.05
			mat.metallic = 0.4
			mat.metallic_specular = 0.9
		"bolt":
			mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED


## Merges every plain palette surface of a mesh into one surface drawn by the shared
## palette material, with each face's palette entry carried by its vertices: the sRGB
## color and roughness in COLOR, metallic and glow in UV2. A mesh then costs one draw
## call instead of one per color: the islands went from about 40 each to a handful,
## which is what keeps the web build (WebGL, where draw calls are costly) at full frame
## rate, and it means one shader to compile instead of one per material feature set.
## Soft cloud materials, unshaded ones and anything transparent keep their own surfaces.
func _merge_palette(mi: MeshInstance3D) -> void:
	var src := mi.mesh as ArrayMesh
	if src == null or src.get_blend_shape_count() > 0 or mi.name.begins_with("BOLT_"):
		return
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	var extras := PackedVector2Array()
	var indices := PackedInt32Array()
	var kept: Array[int] = []
	for i in src.get_surface_count():
		var mat := src.surface_get_material(i) as StandardMaterial3D
		var arrays := src.surface_get_arrays(i)
		if not _mergeable(mat) or src.surface_get_primitive_type(i) != Mesh.PRIMITIVE_TRIANGLES 				or arrays[Mesh.ARRAY_NORMAL] == null or arrays[Mesh.ARRAY_BONES] != null:
			kept.append(i)
			continue
		var surface_verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var base := verts.size()
		verts.append_array(surface_verts)
		normals.append_array(arrays[Mesh.ARRAY_NORMAL])
		var color := Color(mat.albedo_color.r, mat.albedo_color.g, mat.albedo_color.b, mat.roughness)
		var extra := Vector2(mat.metallic, _glow(mat))
		for k in surface_verts.size():
			colors.append(color)
			extras.append(extra)
		if arrays[Mesh.ARRAY_INDEX] == null:
			for k in surface_verts.size():
				indices.append(base + k)
		else:
			for k: int in arrays[Mesh.ARRAY_INDEX]:
				indices.append(base + k)
	if verts.is_empty():
		return
	var merged := ArrayMesh.new()
	merged.resource_name = src.resource_name
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_TEX_UV2] = extras
	arrays[Mesh.ARRAY_INDEX] = indices
	merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	merged.surface_set_material(0, PALETTE_MATERIAL)
	for i in kept:
		merged.add_surface_from_arrays(src.surface_get_primitive_type(i), src.surface_get_arrays(i))
		merged.surface_set_material(merged.get_surface_count() - 1, src.surface_get_material(i))
	mi.mesh = merged


func _mergeable(mat: StandardMaterial3D) -> bool:
	return mat != null and not mat.resource_name in SOFT 		and mat.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED 		and mat.shading_mode == BaseMaterial3D.SHADING_MODE_PER_PIXEL


## Emission strength relative to the surface's own color (the palette glows in its own
## color; the shader multiplies the albedo by this).
func _glow(mat: StandardMaterial3D) -> float:
	if not mat.emission_enabled:
		return 0.0
	var albedo := mat.albedo_color.srgb_to_linear().get_luminance()
	var emission := mat.emission.srgb_to_linear().get_luminance()
	if albedo < 0.001:
		return 0.0
	return mat.emission_energy_multiplier * emission / albedo
