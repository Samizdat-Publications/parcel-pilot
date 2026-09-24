"""Beacon Point: a striped lighthouse on a tall, crystal-studded spire."""

import math

from kit import nature, structures
from kit.build import IslandBuild
from lib import scene
from lib.registry import asset


@asset("island_lighthouse")
def build():
    b = IslandBuild(radius=17, seed=33, depth=70, bumpiness=0.3, wobble=0.1)
    b.delivery(300, height=12.0)

    x, y, z = b.spot(0.0, 1.0, 4.6)
    info = structures.lighthouse(b.dress, x, y, z, math.radians(-60), b.rng)
    b.fx_from(info)
    b.fx("Beacon", info["beacon"])
    b.proxy_cyl((x, y, z - 0.8), 3.9, 27.0)

    cx, cy, cz = b.spot(8.5, -6.0, 3.6)
    info = structures.cottage(b.dress, cx, cy, cz, b.face_center_rot(cx, cy), b.rng, 4.2, 4.6, 2.6,
                              "white", "roof_blue", has_chimney=True)
    b.fx_from(info)
    b.proxy_box((cx, cy, cz - 0.8), (5.0, 5.4, 5.4), b.face_center_rot(cx, cy))
    bx, by, bz = b.spot(-7.5, -5.5, 1.0)
    structures.bench(b.dress, bx, by, bz, math.radians(150))
    for (rx, ry) in ((-9.0, 6.0), (6.0, 9.5), (-3.0, -11.0)):
        if b.place.free(rx, ry, 1.4):
            _, _, rz = b.spot(rx, ry, 1.4)
            nature.rock(b.dress, rx, ry, rz, b.rng, 1.3, "rock_light")

    b.trees(3, "pine", min_r=7, height=7.5)
    b.scatter_small(bushes=4, rocks=2, flowers=5, tufts=12)
    b.finish(roots=8, debris=7, crystals=5)
    for i in range(3):
        a = math.radians(40 + i * 120)
        scene.empty(f"MK_Stamp_{i + 1}", loc=(math.cos(a) * 13, math.sin(a) * 13, 30), size=1)
