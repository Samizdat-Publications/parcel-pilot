"""glTF export with the project's fixed settings, plus QA preview renders."""

import math
import os

import bpy
from mathutils import Vector

from . import scene

# Four views: (framing, azimuth, elevation) in degrees. "full" frames the whole
# asset, "top" frames the upper surface only (island dressing close-up). The last
# view looks from below because floating islands are mostly seen from underneath.
PREVIEW_VIEWS = [("full", -35.0, 22.0), ("full", 145.0, 18.0), ("top", 30.0, 42.0),
                 ("full", -20.0, -24.0)]

COLLISION_ONLY = ("-colonly", "-convcolonly")


def export_glb(path):
    """Export everything in the scene to a binary glTF at `path`."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.view_layer.update()
    for ob in bpy.context.scene.objects:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        check_existing=False,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_vertex_color="NONE",
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_animations=False,
    )


def stats():
    """Triangle count, bounds, and material list for the build report."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tris = 0
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    mats = set()
    meshes = 0
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH" or ob.name.endswith(COLLISION_ONLY):
            continue
        meshes += 1
        ev = ob.evaluated_get(depsgraph)
        me = ev.data
        for poly in me.polygons:
            tris += len(poly.vertices) - 2
        for slot in ob.material_slots:
            if slot.material:
                mats.add(slot.material.name)
        for corner in ob.bound_box:
            w = ob.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    if meshes == 0:
        lo = hi = Vector((0, 0, 0))
    return {
        "triangles": tris,
        "meshes": meshes,
        "objects": len(bpy.context.scene.objects),
        "size": [round(v, 2) for v in (hi - lo)],
        "min": [round(v, 2) for v in lo],
        "max": [round(v, 2) for v in hi],
        "materials": sorted(mats),
        "markers": sorted(ob.name for ob in bpy.context.scene.objects if ob.type == "EMPTY"),
    }


def _setup_render(res):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.show_cavity = True
    sh.cavity_type = "WORLD"
    sh.show_object_outline = False
    sh.show_specular_highlight = False
    sc.display.light_direction = (-0.45, -0.35, 0.82)
    sc.view_settings.view_transform = "Standard"


def render_previews(out_dir, res=480):
    """Render the scene from PREVIEW_VIEWS into out_dir/view_N.png."""
    os.makedirs(out_dir, exist_ok=True)
    st = stats()
    lo, hi = Vector(st["min"]), Vector(st["max"])
    center = (lo + hi) * 0.5
    radius = max((hi - lo).length * 0.5, 0.25)

    _setup_render(res)
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = radius * 20.0 + 100.0
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    half_fov = cam_data.angle * 0.5
    dist = radius / math.sin(half_fov) * 1.0
    # Collision proxies are invisible in the game, so hide them here too.
    for ob in bpy.context.scene.objects:
        if ob.name.endswith(COLLISION_ONLY):
            ob.hide_render = True
    top_center = Vector((center.x, center.y, max(hi.z * 0.35, lo.z)))
    top_radius = max(max(hi.x - lo.x, hi.y - lo.y) * 0.36, 0.25)
    top_dist = top_radius / math.sin(half_fov)

    paths = []
    for i, (framing, az, el) in enumerate(PREVIEW_VIEWS):
        a, e = math.radians(az), math.radians(el)
        direction = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        is_top = framing == "top" and (hi.z - lo.z) > 12.0
        cam.location = (top_center + direction * top_dist) if is_top else (center + direction * dist)
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(out_dir, f"view_{i}.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        paths.append(path)

    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    return paths


def render_icon(path, azimuth, elevation, res=256):
    """A single framed view with a transparent background, for the game's UI."""
    st = stats()
    lo, hi = Vector(st["min"]), Vector(st["max"])
    center = (lo + hi) * 0.5
    radius = max((hi - lo).length * 0.5, 0.1)
    _setup_render(res)
    sh = bpy.context.scene.display.shading
    sh.show_cavity = False
    sh.show_shadows = False
    cam_data = bpy.data.cameras.new("IconCam")
    cam_data.lens = 70.0
    cam = bpy.data.objects.new("IconCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    a, e = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam.location = center + direction * (radius / math.sin(cam_data.angle * 0.5) * 0.92)
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def export_roots():
    return scene.roots()
