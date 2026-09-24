"""Stargazer's Perch: the highest island, with an observatory, a spinning orrery,
a weather vane, and glowing crystals underneath."""

import math

from kit import nature, structures
from kit.build import IslandBuild
from lib.geo import Mesh
from lib.registry import asset


def _vane(point):
    """Weather vane as a SPIN_ object. Local +Y (the spin axis) is turned to point up."""
    v = Mesh()
    v.cylinder(0.06, 1.6, "charcoal", rot=(-math.pi * 0.5, 0, 0), segments=4)
    v.beam((0, 1.4, -1.0), (0, 1.4, 1.2), 0.06, "charcoal")
    v.cone(0.22, 0.5, "gold", loc=(0, 1.4, 1.2), segments=4)
    v.box((0.04, 0.7, 0.5), "gold", loc=(0, 1.4, -1.0))
    v.beam((-0.5, 1.2, 0), (0.5, 1.2, 0), 0.03, "charcoal")
    v.to_object("SPIN_Vane", loc=point, rot=(math.pi * 0.5, 0, 0))


def _orrery(dress, x, y, z):
    dress.cylinder(0.6, 1.2, "stone", loc=(x, y, z - 0.2), segments=8)
    o = Mesh()
    for k, (rot, r) in enumerate((((0, 0, 0), 1.3), ((1.1, 0, 0), 1.15), ((0, 1.1, 0.6), 1.0))):
        o.torus(r, 0.05, "brass", rot=rot, major_seg=18, minor_seg=4)
    o.ico(0.35, "gold", subdiv=1)
    o.ico(0.14, "roof_blue", loc=(1.3, 0, 0), subdiv=1)
    o.ico(0.1, "apple", loc=(0, 0, 1.0), subdiv=1)
    o.to_object("SPIN_Orrery", loc=(x, y, z + 2.2), rot=(math.pi * 0.5, 0, 0))


@asset("island_observatory")
def build():
    b = IslandBuild(radius=19, seed=99, depth=60, bumpiness=0.35)
    b.delivery(90)

    x, y, z = b.spot(0.0, -1.0, 7.5)
    rot = math.radians(-120)
    info = structures.observatory(b.dress, x, y, z, rot, b.rng)
    b.fx_from(info)
    b.proxy_cyl((x, y, z - 0.8), 6.3, 12.5)
    _vane(info["vane"])
    ox, oy, oz = b.spot(9.0, 7.0, 1.8)
    _orrery(b.dress, ox, oy, oz)
    cx, cy, cz = b.spot(-9.5, 6.5, 3.6)
    crot = b.face_center_rot(cx, cy)
    info = structures.cottage(b.dress, cx, cy, cz, crot, b.rng, 4.4, 5.0, 2.8, "plaster_blue", "roof_slate")
    b.fx_from(info)
    b.proxy_box((cx, cy, cz - 0.8), (5.2, 5.8, 5.8), crot)
    for k in range(3):
        a = math.radians(-30 + k * 50)
        lx, ly = math.cos(a) * 12.0, math.sin(a) * 12.0
        if b.place.free(lx, ly, 0.6):
            _, _, lz = b.spot(lx, ly, 0.6)
            b.fx("Light", structures.lamp_post(b.dress, lx, ly, lz, 3.0))
    b.trees(3, "pine", min_r=9, height=7.0)
    b.scatter_small(bushes=3, rocks=5, flowers=4, tufts=12)
    b.finish(roots=8, debris=8, crystals=8)
