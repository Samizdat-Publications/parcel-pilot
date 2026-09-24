"""Vegetation, rocks and small farm props.

Every function adds geometry to a shared `Mesh` at ground point (x, y, z) and
returns the footprint radius it occupies. All variation comes from the `rng`
passed in, so an island rebuilds identically from its seed.
"""

import math

from mathutils import Vector

CANOPY = {
    "summer": ("leaf", "leaf_dark", "leaf_light"),
    "spring": ("leaf_light", "leaf", "grass_light"),
    "autumn": ("leaf_autumn", "mustard", "leaf"),
    "hedge": ("hedge", "leaf_dark", "leaf"),
}


def _blob(m, center, radius, mat, rng, squash=0.85, subdiv=1, wobble=0.14):
    faces = m.ico(radius, mat, loc=center, subdiv=subdiv, scale=(1.0, 1.0, squash),
                  rot=(0.0, 0.0, rng.uniform(0, math.tau)))
    m.jitter(faces, radius * wobble, rng)
    return faces


def round_tree(m, x, y, z, rng, height=5.5, palette="summer", fruit=None):
    h = height * rng.uniform(0.85, 1.15)
    trunk_h = h * 0.45
    lx, ly = rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)
    top = Vector((x + lx * trunk_h, y + ly * trunk_h, z + trunk_h))
    mid = Vector((x + lx * trunk_h * 0.35, y + ly * trunk_h * 0.35, z + trunk_h * 0.5))
    m.tube([(x, y, z - 0.4), mid, top], h * 0.055, "bark", segments=6, taper=0.65)
    mats = CANOPY[palette]
    r = h * 0.3
    crown = top + Vector((0, 0, r * 0.55))
    _blob(m, crown, r, mats[0], rng)
    for k in range(rng.randint(2, 3)):
        a = rng.uniform(0, math.tau)
        off = Vector((math.cos(a) * r * 0.65, math.sin(a) * r * 0.65, rng.uniform(-0.3, 0.35) * r))
        _blob(m, crown + off, r * rng.uniform(0.55, 0.72), mats[1 + k % 2], rng)
    if fruit:
        for _ in range(rng.randint(5, 8)):
            a = rng.uniform(0, math.tau)
            e = rng.uniform(-0.2, 0.6)
            p = crown + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * r * 0.98
            m.box((0.3, 0.3, 0.3), fruit, loc=p, rot=(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 1)))
    return r * 1.3


def pine(m, x, y, z, rng, height=9.0):
    h = height * rng.uniform(0.8, 1.2)
    m.cylinder(h * 0.04, h * 0.3, "bark", loc=(x, y, z - 0.3), segments=5, radius_top=h * 0.03)
    tiers = 4 if h > 8 else 3
    base_r = h * 0.26
    z0 = z + h * 0.16
    tier_h = (h * 0.9) / tiers
    for t in range(tiers):
        frac = t / tiers
        r = base_r * (1.0 - frac * 0.62)
        mat = "pine" if t % 2 == 0 else "pine_dark"
        faces = m.cone(r, tier_h * 1.45, mat, loc=(x, y, z0 + t * tier_h * 0.78), segments=7,
                       phase=rng.uniform(0, math.tau))
        m.jitter(faces, r * 0.07, rng, z_scale=0.4)
    return base_r


def birch(m, x, y, z, rng, height=7.0):
    h = height * rng.uniform(0.85, 1.15)
    top = Vector((x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3), z + h * 0.6))
    m.tube([(x, y, z - 0.3), top], h * 0.04, "birch", segments=5, taper=0.7)
    for k in range(3):
        t = 0.2 + k * 0.22
        p = Vector((x, y, z)).lerp(top, t)
        m.box((h * 0.085, h * 0.085, 0.08), "charcoal", loc=p, rot=(0, 0, rng.uniform(0, 3)))
    r = h * 0.22
    for k in range(3):
        off = Vector((rng.uniform(-r, r) * 0.6, rng.uniform(-r, r) * 0.6, k * r * 0.55))
        _blob(m, top + off, r * (1.0 - k * 0.2), ("leaf_light", "grass_light", "leaf")[k], rng,
              squash=1.1)
    return r


def bush(m, x, y, z, rng, size=1.2, palette="hedge", flowers=None):
    mats = CANOPY[palette]
    for k in range(rng.randint(2, 3)):
        off = Vector((rng.uniform(-0.5, 0.5) * size, rng.uniform(-0.5, 0.5) * size, 0))
        _blob(m, Vector((x, y, z + size * 0.35)) + off, size * rng.uniform(0.55, 0.8),
              mats[k % 3], rng, squash=0.75)
    if flowers:
        for _ in range(5):
            a = rng.uniform(0, math.tau)
            p = (x + math.cos(a) * size * 0.6, y + math.sin(a) * size * 0.6,
                 z + size * rng.uniform(0.5, 0.85))
            m.ico(0.13, flowers, loc=p, subdiv=1)
    return size


def rock(m, x, y, z, rng, size=1.0, mat="rock"):
    faces = m.ico(size, mat, loc=(x, y, z + size * 0.25), subdiv=1,
                  scale=(1.0, rng.uniform(0.7, 1.0), rng.uniform(0.5, 0.75)),
                  rot=(0, 0, rng.uniform(0, math.tau)))
    m.jitter(faces, size * 0.18, rng)
    return size


def flower_patch(m, x, y, z, rng, count=7, spread=1.2):
    colors = ("flower_pink", "flower_yellow", "flower_white", "flower_purple")
    color = rng.choice(colors)
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0, spread)
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        m.cylinder(0.03, 0.35, "leaf_dark", loc=(px, py, z - 0.05), segments=3)
        m.cone(0.15, 0.2, color, loc=(px, py, z + 0.48), rot=(math.pi, 0, 0), segments=4)
    return spread


def grass_tuft(m, x, y, z, rng):
    for k in range(3):
        a = k * 2.1 + rng.uniform(-0.3, 0.3)
        m.cone(0.16, rng.uniform(0.45, 0.7), "grass_dark" if k % 2 else "grass_light",
               loc=(x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, z - 0.05), segments=3,
               rot=(math.cos(a) * 0.25, math.sin(a) * 0.25, 0))
    return 0.3


def mushroom(m, x, y, z, rng, size=0.5):
    m.cylinder(size * 0.18, size * 0.8, "white", loc=(x, y, z - 0.05), segments=6,
               radius_top=size * 0.14)
    m.sphere(size * 0.5, "apple", loc=(x, y, z + size * 0.8), u=8, v=4, scale=(1, 1, 0.55))
    for _ in range(3):
        a = rng.uniform(0, math.tau)
        m.ico(size * 0.07, "white", loc=(x + math.cos(a) * size * 0.3, y + math.sin(a) * size * 0.3,
                                          z + size * 0.98), subdiv=1)
    return size


def hay_bale(m, x, y, z, rng, rot=0.0):
    m.cylinder(0.7, 1.4, "hay", loc=(x, y, z + 0.7), rot=(0, math.pi * 0.5, rot), segments=8,
               base=False)
    return 1.0


def pumpkin(m, x, y, z, rng, size=0.55):
    faces = m.sphere(size, "pumpkin", loc=(x, y, z + size * 0.6), u=10, v=6, scale=(1, 1, 0.72))
    m.jitter(faces, size * 0.04, rng)
    m.cylinder(size * 0.08, size * 0.35, "leaf_dark", loc=(x, y, z + size * 0.95), segments=4)
    return size


def crate(m, x, y, z, rng, size=1.0, rot=0.0):
    from lib.geo import trs
    mm = trs((x, y, z), (0, 0, rot))
    m.box((size, size, size), "wood_light", base=True, m=mm)
    for sx in (-1, 1):
        m.box((0.08, size * 1.02, size * 1.02), "wood_dark", loc=(sx * size * 0.47, 0, 0),
              base=True, m=mm)
    return size * 0.75


def barrel(m, x, y, z, rng, size=1.0):
    r = 0.42 * size
    h = 1.1 * size
    m.lathe([(r * 0.85, 0), (r, h * 0.3), (r, h * 0.7), (r * 0.85, h)], 8, "wood",
            loc=(x, y, z))
    for t in (0.18, 0.82):
        m.cylinder(r * 0.97 + 0.02, 0.07, "charcoal", loc=(x, y, z + h * t), segments=8)
    return r


def floating_rock(m, center, size, rng, mat="rock_dark"):
    faces = m.ico(size, mat, loc=center, subdiv=1,
                  scale=(1.0, rng.uniform(0.7, 1.0), rng.uniform(0.9, 1.3)),
                  rot=(rng.uniform(0, 3), rng.uniform(0, 3), rng.uniform(0, 3)))
    m.jitter(faces, size * 0.22, rng)
