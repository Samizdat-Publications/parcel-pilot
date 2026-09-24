"""Orchard Rest: rows of apple and pear trees, beehives, and a cottage with a view."""

import math

from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib.registry import asset


@asset("island_orchard")
def build():
    b = IslandBuild(radius=27, seed=55, depth=34, bumpiness=0.45)
    pier = b.delivery(250)

    cx, cy, cz = b.spot(11.0, 11.0, 5.2)
    rot = b.face_center_rot(cx, cy)
    info = structures.cottage(b.dress, cx, cy, cz, rot, b.rng, 5.5, 6.5, 3.2, "plaster_pink", "roof_red")
    b.fx_from(info)
    b.proxy_box((cx, cy, cz - 0.8), (6.3, 7.3, 6.6), rot)
    isl.stepping_stones(b.dress, [(info["door"].x, info["door"].y, 0), (0, 0, 0), (pier.x, pier.y, 0)],
                        b.rng, z_of=b.ground)
    b.place.reserve_path([(info["door"].x, info["door"].y), (0, 0), (pier.x, pier.y)], 2.2)

    for row in range(7):
        for col in range(7):
            tx, ty = -18.0 + col * 5.4 + (row % 2) * 1.4, -18.0 + row * 5.2
            if b.place.free(tx, ty, 2.2):
                _, _, tz = b.spot(tx, ty, 2.2)
                fruit = "apple" if (row + col) % 3 else "mustard"
                nature.round_tree(b.dress, tx, ty, tz, b.rng, 4.6, "summer" if (row + col) % 4 else "spring",
                                  fruit=fruit)
                b.proxy_cyl((tx, ty, tz - 0.5), 1.6, 5.0)
    for k in range(4):
        hx, hy = 15.0 + (k % 2) * 1.4, -4.0 - (k // 2) * 1.6
        if b.place.free(hx, hy, 0.8):
            _, _, hz = b.spot(hx, hy, 0.8)
            structures.beehive(b.dress, hx, hy, hz)
    for (kx, ky) in ((4.0, 16.5), (6.0, 17.5)):
        if b.place.free(kx, ky, 0.9):
            _, _, kz = b.spot(kx, ky, 0.9)
            nature.crate(b.dress, kx, ky, kz, b.rng, 0.9, b.rng.uniform(0, 1))
    ax, ay, az = b.spot(-4.0, 17.0, 2.0)
    structures.cart(b.dress, ax, ay, az, 0.4, b.rng)
    bx, by, bz = b.spot(17.0, 4.0, 1.0)
    structures.bench(b.dress, bx, by, bz, math.radians(270))
    for k in range(5):
        for _ in range(20):
            x = b.rng.uniform(-16, 16)
            y = b.rng.uniform(-16, 16)
            if b.place.free(x, y, 0.7):
                _, _, z = b.spot(x, y, 0.7)
                b.dress.lathe([(0.35, 0.0), (0.45, 0.45)], 8, "wood_light", loc=(x, y, z - 0.05))
                for j in range(3):
                    b.dress.ico(0.15, "apple", loc=(x + (j - 1) * 0.18, y, z + 0.45), subdiv=1)
                break
    b.scatter_small(bushes=6, rocks=3, flowers=14, tufts=16)
    b.finish(roots=9, debris=4, waterfall_deg=140)
