"""Milestone 1 blockout shapes: right scale and silhouette, no detail.

These establish gameplay spaces (island sizes, heights, hoop corridors). The art
pass replaces them with the kit generators while keeping every node name.
"""

import math
import random

from lib import scene
from lib.geo import Mesh, trs


def island_body(m, radius, depth, seed, segs=18, top="grey_light", side="grey_mid"):
    """Flat irregular top slab plus a jagged cone underneath, tip at z = -depth."""
    rng = random.Random(seed)
    raw = [rng.uniform(0.86, 1.08) for _ in range(segs)]
    smooth = [(raw[i - 1] + 2.0 * raw[i] + raw[(i + 1) % segs]) * 0.25 for i in range(segs)]
    outline = []
    for i, s in enumerate(smooth):
        a = 2.0 * math.pi * i / segs
        outline.append((math.cos(a) * radius * s, math.sin(a) * radius * s))
    m.prism(outline, -2.5, 0.0, side, top_mat=top)

    rings = []
    for z_frac, scale in ((0.0, 0.97), (0.28, 0.78), (0.55, 0.5), (0.8, 0.24)):
        z = -2.5 - z_frac * (depth - 2.5)
        ring = []
        for (x, y) in outline:
            j = radius * 0.05
            ring.append((x * scale + rng.uniform(-j, j), y * scale + rng.uniform(-j, j), z))
        rings.append(ring)
    rings.append([(rng.uniform(-1, 1), rng.uniform(-1, 1), -depth)])
    m.loft(rings, side)
    return outline


def house(m, x, y, w, d, h, rz=0.0, z=0.0, roof_h=None):
    mm = trs((x, y, z), (0.0, 0.0, rz))
    m.box((w, d, h), "grey_light", base=True, m=mm)
    m.gable_roof(w, d, roof_h if roof_h is not None else h * 0.6, "grey_accent",
                 loc=(0, 0, h), m=mm)


def round_tree(m, x, y, h=5.0, r=2.2, z=0.0):
    m.cylinder(0.35, h * 0.45, "grey_dark", loc=(x, y, z), segments=6)
    m.ico(r, "grey_mid", loc=(x, y, z + h * 0.45 + r * 0.7), subdiv=1)


def cone_tree(m, x, y, h=8.0, r=2.4, z=0.0):
    m.cylinder(0.3, h * 0.2, "grey_dark", loc=(x, y, z), segments=6)
    m.cone(r, h * 0.85, "grey_mid", loc=(x, y, z + h * 0.15), segments=8)


def delivery_socket(radius, angle_deg, height=9.0):
    """Hoop socket just outside the rim, its axis tangent to the island edge.

    The socket's +Y (Godot -Z) runs along the edge, so the flight line through the
    hoop skims past the island instead of into it.
    """
    a = math.radians(angle_deg)
    dist = radius * 1.12 + 8.0
    return scene.empty("MK_Delivery", loc=(math.cos(a) * dist, math.sin(a) * dist, height),
                       rot=(0.0, 0.0, a), size=3.0)
