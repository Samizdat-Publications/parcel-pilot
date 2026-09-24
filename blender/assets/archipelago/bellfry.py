"""Bellfry: a stone chapel with a slate spire, hedges and a flower garden."""

import math

from mathutils import Vector

from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib import scene
from lib.registry import asset


@asset("island_chapel")
def build():
    b = IslandBuild(radius=21, seed=88, depth=44, bumpiness=0.35)
    pier = b.delivery(340)

    x, y, z = b.spot(0.0, 1.5, 8.2)
    rot = math.radians(170)
    info = structures.chapel(b.dress, x, y, z, rot, b.rng)
    b.fx_from(info)
    b.proxy_box((x, y, z - 0.8), (8.4, 13.0, 9.5), rot)
    b.proxy_cyl((info["bell"].x, info["bell"].y, z - 0.5), 3.0, 21.0)
    scene.empty("MK_Stamp_1", loc=info["spire"] + Vector((0, 0, 5.0)), size=1)

    for k in range(6):
        a = math.radians(200 + k * 28)
        hx, hy = math.cos(a) * 13.0, math.sin(a) * 13.0
        if b.place.free(hx, hy, 1.1):
            _, _, hz = b.spot(hx, hy, 1.1)
            nature.bush(b.dress, hx, hy, hz, b.rng, 1.1, "hedge")
    for k in range(3):
        a = math.radians(60 + k * 35)
        fx, fy = math.cos(a) * 11.0, math.sin(a) * 11.0
        if b.place.free(fx, fy, 1.2):
            _, _, fz = b.spot(fx, fy, 1.2)
            nature.flower_patch(b.dress, fx, fy, fz, b.rng, 9, 1.3)
    for k in (-1, 1):
        lx, ly = k * 5.0, -9.0
        if b.place.free(lx, ly, 0.6):
            _, _, lz = b.spot(lx, ly, 0.6)
            b.fx("Light", structures.lamp_post(b.dress, lx, ly, lz, 3.2))
    bx, by, bz = b.spot(8.0, -8.0, 1.0)
    structures.bench(b.dress, bx, by, bz, math.radians(135))
    isl.stepping_stones(b.dress, [(0, -10.0, 0), (pier.x, pier.y, 0)], b.rng, z_of=b.ground)
    b.place.reserve_path([(0, -10.0), (pier.x, pier.y)], 2.2)

    b.trees(4, "round", min_r=12, palette="spring")
    b.trees(2, "birch", min_r=12)
    b.scatter_small(bushes=3, rocks=3, flowers=6, tufts=12)
    b.finish(roots=9, debris=5)
