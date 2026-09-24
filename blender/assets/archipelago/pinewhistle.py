"""Pinewhistle: a dense pine wood around a log cabin and a campfire."""

import math

from kit import islands as isl
from kit import nature, structures
from kit.build import IslandBuild
from lib.registry import asset


@asset("island_forest")
def build():
    b = IslandBuild(radius=31, seed=66, depth=40, bumpiness=0.65)
    pier = b.delivery(60)

    x, y, z = b.spot(-2.0, -2.0, 5.2)
    rot = math.radians(205)
    info = structures.log_cabin(b.dress, x, y, z, rot, b.rng)
    b.fx_from(info)
    b.proxy_box((x, y, z - 0.8), (7.4, 6.4, 7.0), rot)
    fx, fy, fz = b.spot(4.5, -8.5, 2.6)
    b.fx("Fire", structures.campfire(b.dress, fx, fy, fz, b.rng))
    wx, wy, wz = b.spot(-8.0, 4.0, 1.4)
    structures.woodpile(b.dress, wx, wy, wz, 0.6, b.rng)
    isl.stepping_stones(b.dress, [(info["door"].x, info["door"].y, 0), (fx, fy, 0), (pier.x, pier.y, 0)],
                        b.rng, z_of=b.ground)
    b.place.reserve_path([(info["door"].x, info["door"].y), (fx, fy), (pier.x, pier.y)], 2.4)

    b.trees(24, "pine", r=2.4, min_r=8)
    b.trees(3, "birch", min_r=10)
    b.scatter_small(bushes=5, rocks=6, flowers=3, tufts=14, mushrooms=9)
    b.finish(roots=16, debris=5)
