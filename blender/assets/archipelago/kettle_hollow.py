"""Kettle Hollow: a cluster of cottages around a well, with a waterfall off the edge."""

import math

from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib.registry import asset

# (angle deg, distance, width, depth, wall height, wall, roof)
HOUSES = (
    (20, 15.0, 6.0, 7.0, 3.4, "plaster", "roof_red"),
    (95, 14.5, 5.5, 6.5, 3.2, "plaster_blue", "roof_slate"),
    (165, 16.0, 6.5, 7.5, 3.6, "plaster_pink", "roof_teal"),
    (235, 15.0, 5.5, 6.0, 3.0, "plaster_warm", "roof_red"),
    (305, 16.5, 6.0, 7.0, 3.4, "plaster", "roof_blue"),
)


@asset("island_village")
def build():
    b = IslandBuild(radius=36, seed=44, depth=46, bumpiness=0.5)
    pier = b.delivery(128)

    x, y, z = b.spot(0, 0, 3.8)
    structures.well(b.dress, x, y, z, b.rng)
    b.proxy_cyl((x, y, z - 0.5), 1.8, 4.2)

    doors = []
    for (deg, dist, w, d, h, wall, roof) in HOUSES:
        a = math.radians(deg)
        hx, hy = math.cos(a) * dist, math.sin(a) * dist
        rot = b.face_center_rot(hx, hy)
        _, _, hz = b.spot(hx, hy, math.hypot(w, d) * 0.5 + 1.0)
        info = structures.cottage(b.dress, hx, hy, hz, rot, b.rng, w, d, h, wall, roof)
        b.fx_from(info)
        b.proxy_box((hx, hy, hz - 0.8), (w + 0.8, d + 0.8, h + w * 0.5 + 1.4), rot)
        doors.append(info["door"])

    for door in doors:
        isl.stepping_stones(b.dress, [(door.x, door.y, 0), (door.x * 0.3, door.y * 0.3, 0)], b.rng,
                            z_of=b.ground)
        b.place.reserve_path([(door.x, door.y), (door.x * 0.3, door.y * 0.3)], 2.0)
    isl.stepping_stones(b.dress, [(0, 0, 0), (pier.x, pier.y, 0)], b.rng, z_of=b.ground)
    b.place.reserve_path([(pier.x * 0.2, pier.y * 0.2), (pier.x, pier.y)], 2.4)

    mx, my, mz = b.spot(-5.5, 5.5, 2.4)
    structures.market_stall(b.dress, mx, my, mz, b.face_center_rot(mx, my), b.rng)
    for k in range(4):
        a = math.radians(60 + k * 90)
        lx, ly = math.cos(a) * 7.0, math.sin(a) * 7.0
        if b.place.free(lx, ly, 0.6):
            _, _, lz = b.spot(lx, ly, 0.6)
            b.fx("Light", structures.lamp_post(b.dress, lx, ly, lz, 3.3))
    for k in range(3):
        a = math.radians(10 + k * 120)
        bx, by = math.cos(a) * 5.0, math.sin(a) * 5.0
        if b.place.free(bx, by, 1.0):
            _, _, bz = b.spot(bx, by, 1.0)
            structures.bench(b.dress, bx, by, bz, a + math.pi * 0.5)
    cx, cy, cz = b.spot(9.0, -9.0, 2.0)
    structures.cart(b.dress, cx, cy, cz, 0.7, b.rng)

    b.trees(7, "round", min_r=22, palette="summer")
    b.trees(3, "round", min_r=22, palette="autumn")
    b.trees(3, "birch", min_r=24)
    b.scatter_small(bushes=10, rocks=5, flowers=10, tufts=22)
    b.finish(roots=14, debris=5, crystals=2, waterfall_deg=300)
