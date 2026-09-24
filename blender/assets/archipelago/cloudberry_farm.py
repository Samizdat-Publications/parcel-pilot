"""Cloudberry Farm: a red barn, a silo, pumpkin rows, hay, and a scarecrow."""

import math

from assets.archipelago.props import field
from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib.registry import asset


@asset("island_farm")
def build():
    b = IslandBuild(radius=33, seed=77, depth=38, bumpiness=0.4)
    pier = b.delivery(160)

    bx, by, bz = b.spot(-5.0, 7.0, 9.0)
    rot = math.radians(15)
    info = structures.barn(b.dress, bx, by, bz, rot, b.rng)
    b.fx_from(info)
    b.proxy_box((bx, by, bz - 0.8), (10.0, 13.0, 11.0), rot)
    sx, sy, sz = b.spot(6.5, 12.5, 3.6)
    structures.silo(b.dress, sx, sy, sz, b.rng)
    b.proxy_cyl((sx, sy, sz - 0.5), 3.2, 16.0)
    hx, hy, hz = b.spot(12.0, -6.0, 5.0)
    hrot = b.face_center_rot(hx, hy)
    info = structures.cottage(b.dress, hx, hy, hz, hrot, b.rng, 6.0, 6.5, 3.2, "white", "roof_red")
    b.fx_from(info)
    b.proxy_box((hx, hy, hz - 0.8), (6.8, 7.3, 6.8), hrot)

    for (fx, fy, crop) in ((-12.0, -10.0, "pumpkins"), (-1.0, -15.0, "greens")):
        _, _, fz = b.spot(fx, fy, 6.0)
        field(b.dress, fx, fy, fz, -0.25, b.rng, 8.5, 7.0, crop)
    cx, cy, cz = b.spot(-6.0, -4.5, 1.0)
    structures.scarecrow(b.dress, cx, cy, cz, 0.3)
    for (hx2, hy2) in ((5.0, 3.0), (7.0, 4.5), (4.0, 5.2)):
        if b.place.free(hx2, hy2, 1.0):
            _, _, hz2 = b.spot(hx2, hy2, 1.0)
            nature.hay_bale(b.dress, hx2, hy2, hz2, b.rng, b.rng.uniform(0, 3))
    structures.fence(b.dress, [(-18.0, -4.0), (-18.0, -18.0), (7.0, -22.0)], b.ground)
    for (px, py) in ((15.0, 4.0), (17.0, 1.0)):
        if b.place.free(px, py, 0.7):
            _, _, pz = b.spot(px, py, 0.7)
            nature.pumpkin(b.dress, px, py, pz, b.rng)
    isl.stepping_stones(b.dress, [(info["door"].x, info["door"].y, 0), (pier.x, pier.y, 0)], b.rng,
                        z_of=b.ground)
    b.place.reserve_path([(info["door"].x, info["door"].y), (pier.x, pier.y)], 2.2)

    b.trees(5, "round", min_r=20)
    b.trees(2, "round", min_r=20, palette="autumn")
    b.scatter_small(bushes=6, rocks=4, flowers=6, tufts=18)
    b.finish(roots=11, debris=5)
