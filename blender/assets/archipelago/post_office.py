"""Post Office Peak: the hub where every shift starts."""

import math

from assets.archipelago.props import flag_on_pole, parcel_stack
from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib import scene
from lib.registry import asset


@asset("island_post_office")
def build():
    b = IslandBuild(radius=34, seed=11, depth=46, bumpiness=0.4)
    pier = b.delivery(200)

    x, y, z = b.spot(0, 5, 10.5)
    info = structures.post_office(b.dress, x, y, z, 0.0, b.rng)
    b.fx_from(info)
    b.proxy_box((x, y, z - 0.6), (12.8, 9.8, 12.0))
    door = info["door"]

    # Forecourt: flag, post boxes, parcel stacks, lamps, benches.
    fx, fy, fz = b.spot(-9.5, -7.0, 1.5)
    flag_on_pole(b.dress, "FLAG_Post", fx, fy, fz, b.rng, height=14.0)
    b.proxy_cyl((fx, fy, fz), 0.4, 14.5)
    for px in (-3.4, 3.4):
        _, _, pz = b.spot(px, -2.6, 0.9)
        structures.pillar_box(b.dress, px, -2.6, pz, 0.0)
    for (sx, sy) in ((8.8, -3.5), (9.6, 8.0)):
        _, _, sz = b.spot(sx, sy, 2.2)
        parcel_stack(b.dress, sx, sy, sz, b.rng)
    for lx in (-6.0, 6.0):
        _, _, lz = b.spot(lx, -6.5, 0.6)
        b.fx("Light", structures.lamp_post(b.dress, lx, -6.5, lz, 3.6))
    for (bx, brot) in ((-3.0, 0.0), (3.0, 0.0)):
        _, _, bz = b.spot(bx, -8.8, 1.1)
        structures.bench(b.dress, bx, -8.8, bz, brot + math.pi)

    path = [(door.x, door.y), (0.0, -12.0), (pier.x * 0.55, pier.y * 0.55), (pier.x, pier.y)]
    isl.stepping_stones(b.dress, [(px, py, 0) for px, py in path], b.rng, z_of=b.ground)
    b.place.reserve_path(path, 2.6)
    sx, sy, sz = b.spot(4.0, -13.0, 0.7)
    structures.signpost(b.dress, sx, sy, sz, math.atan2(pier.y - sy, pier.x - sx), "cream")

    hx, hy, hz = b.spot(-15.5, 9.0, 9.0)
    hrot = math.radians(-70)
    info = structures.hangar(b.dress, hx, hy, hz, hrot, b.rng)
    b.fx_from(info)
    b.proxy_box((hx, hy, hz - 0.6), (11.6, 14.6, 6.0), hrot)
    wx, wy, wz = b.spot(-18.0, -6.0, 1.0)
    structures.windsock(b.dress, wx, wy, wz, math.radians(30))
    for (cx, cy) in ((13.5, 12.0), (14.5, 9.4)):
        _, _, cz = b.spot(cx, cy, 1.0)
        nature.crate(b.dress, cx, cy, cz, b.rng, 1.1, b.rng.uniform(0, 1))

    b.trees(7, "round", min_r=15)
    b.trees(4, "birch", min_r=17)
    b.scatter_small(bushes=10, rocks=5, flowers=10, tufts=22)
    b.finish(roots=12, debris=6)
    scene.empty("MK_Spawn", loc=(0, -75, 24), size=3)
    scene.empty("MK_Stamp_1", loc=(0, 5, 24), size=1)
