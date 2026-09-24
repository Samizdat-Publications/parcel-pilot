"""Hollow Arch: two rock pillars joined by a natural arch. The delivery hoop hangs
inside the opening, so this drop is a fly-through."""

import math
import random

from mathutils import Vector

from kit import islands as isl
from kit import nature
from lib import scene
from lib.geo import Mesh
from lib.registry import asset

PILLAR_X = 17.0
STRATA = ["deep_rock", "rock_dark", "rock", "sandstone", "clay", "sandstone", "rock_light", "sandstone"]


@asset("island_arch")
def build():
    rng = random.Random(606)
    body = Mesh()
    for side in (-1, 1):
        prof = [(0.0, -48.0), (3.5, -40.0), (5.5, -28.0), (7.0, -16.0), (7.6, -5.0), (7.4, 4.0), (7.0, 12.0),
                (6.6, 18.0)]
        body.lathe(prof, 10, STRATA[: len(prof) - 1], loc=(side * PILLAR_X, 0, 0), jitter=0.55, rng=rng)
    rings = []
    steps = 12
    for k in range(steps + 1):
        th = math.pi * k / steps
        c = Vector((PILLAR_X * math.cos(th), 0.0, 14.0 + 11.0 * math.sin(th)))
        t = Vector((-PILLAR_X * math.sin(th), 0.0, 11.0 * math.cos(th))).normalized()
        n = t.cross(Vector((0, 1, 0))).normalized()
        if n.z < 0:
            n = -n
        half_w = 6.5 + 1.2 * math.sin(th * 2.0)
        thick = 4.2 - 1.2 * math.sin(th)
        ring = []
        for (sy, sn) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            j = Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.4)))
            ring.append(c + Vector((0, sy * half_w, 0)) + n * sn * thick + j)
        rings.append(ring)
    faces = body.loft(rings, "rock")
    # Strata are horizontal layers: pick each face's rock by its height, matching the
    # banding of the pillars, then put grass on everything facing up.
    for f in faces:
        z = f.calc_center_median().z
        body.paint([f], STRATA[min(len(STRATA) - 1, max(0, int((z + 48.0) / 66.0 * 7.0)))])
    body.paint_up(faces, "grass", 0.5)
    body.to_object("Island-col")

    dress = Mesh()
    for k in (3, 5, 7, 9):
        th = math.pi * k / steps
        top = Vector((PILLAR_X * math.cos(th), rng.uniform(-3, 3), 14.0 + 11.0 * math.sin(th) + 3.2))
        nature.pine(dress, top.x, top.y, top.z - 0.3, rng, rng.uniform(6.0, 8.0))
    for side in (-1, 1):
        for k in range(3):
            nature.grass_tuft(dress, side * PILLAR_X + rng.uniform(-3, 3), rng.uniform(-3, 3), 18.1, rng)
    vines = Mesh()
    for k in range(9):
        th = math.pi * (0.2 + 0.6 * rng.random())
        c = Vector((PILLAR_X * math.cos(th), rng.uniform(-5.5, 5.5), 14.0 + 11.0 * math.sin(th) - 3.4))
        length = rng.uniform(3.0, 8.0)
        vines.tube([c, c + Vector((0.2, 0.1, -length * 0.5)), c + Vector((0.0, 0.3, -length))],
                   0.1, rng.choice(["leaf_dark", "moss"]), segments=4, taper=0.2)
    dress.to_object("Dressing")
    vines.to_object("Roots")

    debris = Mesh()
    for k in range(6):
        c = Vector((rng.uniform(-30, 30), rng.uniform(-14, 14), rng.uniform(-35, -5)))
        nature.floating_rock(debris, c, rng.uniform(0.8, 2.0), rng)
    debris.to_object("Debris")

    scene.empty("MK_Delivery", loc=(0, 0, 6.0), rot=(0, 0, 0), size=3.0)
    scene.empty("MK_Stamp_1", loc=(0, 0, 33.0), size=1)
