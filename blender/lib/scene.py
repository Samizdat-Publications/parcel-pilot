"""Scene bookkeeping: clean slate per asset, marker empties, hierarchy helpers."""

import bpy
from mathutils import Euler, Vector


def reset():
    """Remove every object and datablock so each asset builds from nothing."""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                   bpy.data.lights, bpy.data.curves, bpy.data.images):
        for block in list(blocks):
            blocks.remove(block)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, size=1.0, kind="ARROWS"):
    """A named empty. Exported as a plain node that Godot code can find by name.

    Naming contract (see docs/PIPELINE.md):
      MK_*   gameplay sockets (delivery hoop, spawn points, stamps)
      FX_*   effect sockets (chimney smoke, lights, waterfall mist)
    """
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(loc)
    ob.rotation_euler = Euler(rot, "XYZ")
    if parent is not None:
        ob.parent = parent
    return ob


def descendants(ob):
    out = [ob]
    for child in ob.children:
        out += descendants(child)
    return out


def roots():
    return [ob for ob in bpy.context.scene.objects if ob.parent is None]
