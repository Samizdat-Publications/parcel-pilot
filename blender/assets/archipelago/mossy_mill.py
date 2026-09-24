"""Mossy Mill: a teal-capped windmill over wheat and cabbage fields, with a waterfall."""

import math

from assets.archipelago.props import field
from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib import scene
from lib.registry import asset


@asset("island_windmill")
def build():
    b = IslandBuild(radius=28, seed=22, depth=38, bumpiness=0.55)
    pier = b.delivery(30)

    x, y, z = b.spot(3.0, 2.0, 6.8)
    info = structures.windmill(b.dress, x, y, z, math.radians(160), b.rng)
    b.fx_from(info)
    b.proxy_cyl((x, y, z - 0.8), 4.8, 16.6)
    structures.windmill_sails("SPIN_Sails", info["sails"], info["yaw"], b.rng)
    scene.empty("MK_Stamp_1", loc=(x, y, z + 25.0), size=1)

    for (fx, fy, rot, crop) in ((-11.0, -6.0, 0.35, "wheat"), (-8.0, 9.0, 0.35, "greens")):
        _, _, fz = b.spot(fx, fy, 6.5)
        field(b.dress, fx, fy, fz, rot, b.rng, 9.0, 7.0, crop)
    structures.fence(b.dress, [(-16.5, -1.0), (-16.0, 14.0), (-3.0, 16.0)], b.ground)
    cx, cy, cz = b.spot(13.0, 9.0, 4.8)
    info = structures.cottage(b.dress, cx, cy, cz, b.face_center_rot(cx, cy), b.rng, 5.0, 5.5, 3.0,
                              "plaster_warm", "thatch")
    b.fx_from(info)
    b.proxy_box((cx, cy, cz - 0.8), (5.8, 6.3, 6.2), b.face_center_rot(cx, cy))
    for (hx, hy) in ((-2.0, -14.0), (0.5, -15.5), (-4.0, -16.0)):
        if b.place.free(hx, hy, 1.0):
            _, _, hz = b.spot(hx, hy, 1.0)
            nature.hay_bale(b.dress, hx, hy, hz, b.rng, b.rng.uniform(0, 3))
    kx, ky, kz = b.spot(9.0, -8.0, 2.0)
    structures.cart(b.dress, kx, ky, kz, 2.2, b.rng)
    isl.stepping_stones(b.dress, [(x, y - 5.0, 0), (pier.x, pier.y, 0)], b.rng, z_of=b.ground)
    b.place.reserve_path([(x, y - 5.0), (pier.x, pier.y)], 2.2)

    b.trees(5, "round", min_r=16)
    b.trees(2, "round", min_r=16, palette="autumn")
    b.scatter_small(bushes=7, rocks=4, flowers=8, tufts=18)
    b.finish(roots=10, debris=4, waterfall_deg=235)
