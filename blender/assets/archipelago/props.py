"""Island-scale set dressing shared by several islands (flags, parcel stacks, paths)."""

import math

from lib.geo import Mesh


def flag_on_pole(dress, name, x, y, z, rng, height=13.0, cloth="cloth_red", length=3.6):
    """A pole in the dressing mesh plus the cloth as its own FLAG_ object (so the
    game can wave it)."""
    dress.cylinder(0.32, 0.4, "stone", loc=(x, y, z - 0.2), segments=8)
    dress.cylinder(0.13, height, "white", loc=(x, y, z), segments=6, radius_top=0.09)
    dress.ico(0.24, "brass", loc=(x, y, z + height + 0.15), subdiv=1)
    top = z + height - 0.25
    # The cloth's origin sits at the top of the pole, so in the game its local +X is the
    # distance along the flag (the wave shader scales its ripple by it).
    f = Mesh()
    rings = []
    for k in range(9):
        t = k / 8
        px = 0.12 + t * length
        wave = math.sin(t * 5.5 + 0.4) * 0.28 * t
        droop = t * t * 0.25
        rings.append([(px, wave - 0.03, -2.2 - droop), (px, wave + 0.03, -2.2 - droop),
                      (px, wave + 0.03, -droop), (px, wave - 0.03, -droop)])
    f.loft(rings, cloth)
    return f.to_object(name, loc=(x, y, top))


def field(m, x, y, z, rot, rng, width=9.0, length=7.0, crop="wheat"):
    """A tilled plot with crop rows. crop: wheat, greens, or pumpkins."""
    from lib.geo import trs
    M = trs((x, y, z), (0, 0, rot))
    m.box((width + 0.6, length + 0.6, 0.5), "dirt_dark", loc=(0, 0, -0.35), base=True, m=M)
    rows = int(width / 1.3)
    for r in range(rows):
        rx = -width * 0.5 + 0.65 + r * 1.3
        m.box((0.55, length, 0.3), "dirt", loc=(rx, 0, 0.1), base=True, m=M)
        if crop == "wheat":
            m.box((0.5, length - 0.3, 0.9), "hay" if r % 2 else "grass_light", loc=(rx, 0, 0.35), base=True, m=M)
        else:
            steps = int(length / 1.2)
            for k in range(steps):
                py = -length * 0.5 + 0.6 + k * 1.2
                if crop == "pumpkins" and rng.random() < 0.55:
                    m.sphere(0.42, "pumpkin", loc=(rx, py, 0.55), u=8, v=5, scale=(1, 1, 0.7), m=M)
                else:
                    m.ico(0.32, rng.choice(("leaf_light", "leaf", "grass_light")), loc=(rx, py, 0.55),
                          subdiv=1, scale=(1, 1, 0.7), m=M)
    return math.hypot(width, length) * 0.5 + 0.5


def parcel_stack(m, x, y, z, rng, columns=3):
    for c in range(columns):
        cx = x + (c - (columns - 1) * 0.5) * 1.15 + rng.uniform(-0.15, 0.15)
        cy = y + rng.uniform(-0.3, 0.3)
        cz = z
        for _ in range(rng.randint(1, 3)):
            s = rng.uniform(0.7, 1.05)
            h = s * rng.uniform(0.55, 0.8)
            rot = (0, 0, rng.uniform(-0.25, 0.25))
            m.box((s, s * 0.85, h), "kraft", loc=(cx, cy, cz), rot=rot, base=True)
            m.box((s * 1.02, 0.09, h * 1.02), "rope", loc=(cx, cy, cz - 0.005), rot=rot, base=True)
            m.box((0.09, s * 0.87, h * 1.02), "rope", loc=(cx, cy, cz - 0.005), rot=rot, base=True)
            cz += h
