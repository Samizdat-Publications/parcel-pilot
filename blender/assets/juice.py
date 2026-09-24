"""Milestone 3 assets: a flapping bird, the parachute parcel dropped on delivery, and
the 3D title logo (Blender's built-in font, converted to beveled mesh)."""

import math

import bpy
from mathutils import Vector

from lib import palette
from lib.geo import Mesh
from lib.registry import asset


@asset("bird")
def bird():
    """A gull-ish bird. WingL / WingR are separate children the game flaps."""
    body = Mesh()
    body.lathe([(0.0, -0.55), (0.12, -0.35), (0.16, 0.0), (0.12, 0.3), (0.0, 0.5)], 6, "white",
               rot=(-math.pi * 0.5, 0, 0))
    body.cone(0.05, 0.16, "mustard", loc=(0, 0.5, 0), rot=(-math.pi * 0.5, 0, 0), segments=4)
    body.prism([(-0.02, -0.4), (0.02, -0.4), (0.18, -0.72), (-0.18, -0.72)], -0.02, 0.02, "cloud_shade",
               loc=(0, 0, 0.02))
    root = body.to_object("Bird")
    for side, name in ((-1, "WingL"), (1, "WingR")):
        w = Mesh()
        outline = [(0.0, -0.14), (0.0, 0.16), (side * 0.45, 0.1), (side * 0.85, -0.04), (side * 0.6, -0.16)]
        if side < 0:
            outline = list(reversed(outline))
        w.prism(outline, -0.015, 0.015, "white")
        w.prism([(side * 0.62, -0.13), (side * 0.85, -0.04), (side * 0.72, -0.16)] if side > 0 else
                [(side * 0.72, -0.16), (side * 0.85, -0.04), (side * 0.62, -0.13)], -0.02, 0.02, "charcoal")
        w.to_object(name, parent=root, loc=(side * 0.08, 0.02, 0.04))


@asset("parcel_chute")
def parcel_chute():
    """A parcel hanging under a striped parachute, dropped onto the island on delivery."""
    m = Mesh()
    m.box((0.8, 0.7, 0.52), "kraft", loc=(0, 0, 0.26))
    m.box((0.83, 0.08, 0.55), "rope", loc=(0, 0, 0.26))
    m.box((0.08, 0.73, 0.55), "rope", loc=(0, 0, 0.26))
    canopy = [(2.4, 3.2), (2.1, 3.9), (1.4, 4.4), (0.0, 4.6)]
    m.lathe(canopy, 12, "cloth_red", seg_mats=["cloth_red", "cloth_cream"], stripe=1)
    m.lathe([(2.35, 3.15), (2.4, 3.2)], 12, "cloth_red")
    for k in range(6):
        a = k * math.tau / 6
        m.rod((0, 0, 0.55), (math.cos(a) * 2.3, math.sin(a) * 2.3, 3.2), 0.025, "rope", segments=3)
    m.to_object("ParcelChute")


def _text_mesh(text, size, extrude, bevel, align="CENTER"):
    curve = bpy.data.curves.new("LogoText", type="FONT")
    curve.body = text
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = bevel
    curve.bevel_resolution = 1
    curve.offset = 0.055  # thickens the glyph outlines: chunky, toy-like lettering
    curve.align_x = align
    curve.align_y = "CENTER"
    ob = bpy.data.objects.new("LogoText", curve)
    bpy.context.scene.collection.objects.link(ob)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(depsgraph))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(curve)
    return mesh


@asset("logo")
def logo():
    """PARCEL PILOT as chunky beveled 3D letters, standing up and facing -Y (the camera)."""
    top = _text_mesh("PARCEL", 2.0, 0.34, 0.06)
    bottom = _text_mesh("PILOT", 2.0, 0.34, 0.06)
    for mesh, z, face, side in ((top, 1.15, "cream", "postal_red"), (bottom, -1.15, "cream", "postal_red")):
        mesh.materials.append(palette.material(face))
        mesh.materials.append(palette.material(side))
        for poly in mesh.polygons:
            poly.material_index = 0 if abs(poly.normal.z) > 0.7 else 1
        ob = bpy.data.objects.new("Logo" + ("Top" if z > 0 else "Bottom"), mesh)
        bpy.context.scene.collection.objects.link(ob)
        ob.rotation_euler = (math.pi * 0.5, 0, 0)
        ob.location = Vector((0, 0, z))
    # A gold ribbon behind the lettering (letters face -Y, so behind is +Y).
    banner = Mesh()
    banner.box((8.6, 0.2, 0.55), "mustard", loc=(0, 0.62, 0.0), rot=(0, -0.04, 0))
    for side in (-1, 1):
        banner.prism([(0.0, -0.45), (0.9, -0.45), (0.55, 0.0), (0.9, 0.45), (0.0, 0.45)], -0.1, 0.1,
                     "postal_red", loc=(side * 4.45, 0.72, 0.0), rot=(math.pi * 0.5, 0, 0 if side > 0 else math.pi))
    banner.to_object("LogoBanner")
