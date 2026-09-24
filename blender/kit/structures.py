"""Buildings and man-made props, in the same chunky toy style.

Conventions: every builder takes a target `Mesh`, a ground point (x, y, z), a yaw
`rot` and an rng. Buildings face local -Y (their front door side). They return a
dict with world-space points of interest ("smoke", "lights", "door", ...) so the
island script can drop FX_ sockets there, plus "radius" for placement.
"""

import math

from mathutils import Matrix, Vector

from lib.geo import trs


def _frame(x, y, z, rot):
    return trs((x, y, z), (0.0, 0.0, rot))


def _wall_frame(M, center, facing):
    """Matrix for a wall-mounted part: local -Y points out of the wall.

    `facing` is the wall's outward direction in building space: one of
    "front" (-Y), "back" (+Y), "left" (-X), "right" (+X).
    """
    angle = {"front": 0.0, "back": math.pi, "left": -0.5 * math.pi, "right": 0.5 * math.pi}[facing]
    return M @ Matrix.Translation(Vector(center)) @ Matrix.Rotation(angle, 4, "Z")


def window(m, W, w=0.9, h=1.05, frame="cream", flower_box=False, rng=None):
    """A lit window on a wall frame W (from _wall_frame)."""
    m.box((w + 0.26, 0.1, h + 0.26), frame, loc=(0, -0.02, 0), m=W)
    m.box((w, 0.1, h), "window", loc=(0, -0.06, 0), m=W)
    m.box((0.07, 0.06, h), frame, loc=(0, -0.12, 0), m=W)
    m.box((w, 0.06, 0.07), frame, loc=(0, -0.12, 0), m=W)
    m.box((w + 0.4, 0.3, 0.1), "wood_light", loc=(0, -0.15, -h * 0.5 - 0.12), m=W)
    if flower_box and rng is not None:
        m.box((w + 0.2, 0.3, 0.26), "wood", loc=(0, -0.2, -h * 0.5 - 0.32), m=W)
        for k in range(4):
            c = rng.choice(("flower_pink", "flower_yellow", "flower_white", "apple"))
            m.ico(0.13, c, loc=(-w * 0.4 + k * w * 0.27, -0.22, -h * 0.5 - 0.12), subdiv=1, m=W)


def door(m, W, w=1.1, h=2.0, color="door"):
    m.box((w + 0.26, 0.12, h + 0.13), "wood_dark", loc=(0, -0.02, h * 0.5), m=W)
    m.box((w, 0.14, h), color, loc=(0, -0.06, h * 0.5), m=W)
    m.box((0.1, 0.1, 0.1), "brass", loc=(w * 0.32, -0.16, h * 0.5), m=W)
    m.box((w + 0.6, 0.7, 0.2), "stone", loc=(0, -0.35, -0.1), m=W)


def chimney(m, M, x, y, z0, top, mat="brick"):
    m.box((0.9, 0.9, top - z0), mat, loc=(x, y, z0), base=True, m=M)
    m.box((1.15, 1.15, 0.22), "stone_dark", loc=(x, y, top), base=True, m=M)
    return M @ Vector((x, y, top + 0.3))


def cottage(m, x, y, z, rot, rng, w=6.0, d=7.0, h=3.4, wall="plaster", roof="roof_red",
            trim="cream", has_chimney=True, flower_boxes=True):
    M = _frame(x, y, z, rot)
    info = {"radius": math.hypot(w, d) * 0.5 + 0.8, "lights": [], "smoke": []}
    m.box((w + 0.5, d + 0.5, 1.1), "stone", loc=(0, 0, -0.8), base=True, m=M)
    m.box((w, d, h), wall, loc=(0, 0, 0.3), base=True, m=M)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((0.28, 0.28, h), "wood_dark", loc=(sx * w * 0.5, sy * d * 0.5, 0.3), base=True, m=M)
    m.box((w + 0.06, d + 0.06, 0.2), "wood_dark", loc=(0, 0, 0.3 + h - 0.2), base=True, m=M)
    roof_h = w * 0.5
    m.gable_roof(w, d, roof_h, roof, loc=(0, 0, 0.3 + h), overhang=0.45, thickness=0.26,
                 gable_mat=wall, m=M)
    door(m, _wall_frame(M, (0, -d * 0.5, 0.3), "front"))
    info["door"] = M @ Vector((0, -d * 0.5 - 1.2, 0))
    wz = 0.3 + h * 0.58
    n_side = 2 if d >= 6.0 else 1
    for side in ("left", "right"):
        sx = -w * 0.5 if side == "left" else w * 0.5
        for k in range(n_side):
            yy = (k - (n_side - 1) * 0.5) * d * 0.42
            window(m, _wall_frame(M, (sx, yy, wz), side), 0.85, 1.0, trim,
                   flower_boxes and rng.random() < 0.5, rng)
    if w >= 5.0:
        for sx in (-1, 1):
            window(m, _wall_frame(M, (sx * w * 0.3, -d * 0.5, wz), "front"), 0.75, 0.95, trim,
                   flower_boxes and rng.random() < 0.6, rng)
    window(m, _wall_frame(M, (0, d * 0.5, wz), "back"), 0.9, 1.0, trim)
    window(m, _wall_frame(M, (0, -d * 0.5, 0.3 + h + roof_h * 0.42), "front"), 0.6, 0.6, trim)
    info["lights"].append(M @ Vector((0, -d * 0.5 - 0.6, 0.3 + 2.4)))
    if has_chimney:
        cx = w * 0.27 * (1 if rng.random() < 0.5 else -1)
        cy = d * 0.22
        roof_at = 0.3 + h + roof_h * (1.0 - abs(cx) / (w * 0.5))
        info["smoke"].append(chimney(m, M, cx, cy, 0.3 + h - 0.2, roof_at + 1.3))
    return info


def post_office(m, x, y, z, rot, rng):
    """The hub: two storeys, brick ground floor, big sign, clock, awning."""
    M = _frame(x, y, z, rot)
    w, d, h = 12.0, 9.0, 6.8
    info = {"radius": 9.5, "lights": [], "smoke": []}
    m.box((w + 0.8, d + 0.8, 1.2), "stone", loc=(0, 0, -0.9), base=True, m=M)
    m.box((w, d, h), "plaster_warm", loc=(0, 0, 0.3), base=True, m=M)
    m.box((w + 0.12, d + 0.12, 3.2), "brick", loc=(0, 0, 0.3), base=True, m=M)
    m.box((w + 0.3, d + 0.3, 0.25), "cream", loc=(0, 0, 3.5), base=True, m=M)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((0.5, 0.5, h + 0.1), "cream", loc=(sx * w * 0.5, sy * d * 0.5, 0.3), base=True, m=M)
    roof_h = 4.2
    m.gable_roof(w, d, roof_h, "roof_red", loc=(0, 0, 0.3 + h), overhang=0.6, thickness=0.3,
                 gable_mat="plaster_warm", m=M)
    # Double door, awning and sign on the front.
    W = _wall_frame(M, (0, -d * 0.5, 0.3), "front")
    door(m, W, w=2.2, h=2.6, color="navy")
    m.box((3.6, 1.6, 0.14), "cloth_red", loc=(0, -0.8, 3.0), rot=(-0.35, 0, 0), m=W)
    m.box((5.4, 0.2, 1.3), "cream", loc=(0, -0.12, 4.4), m=W)
    m.box((5.0, 0.24, 0.12), "postal_red", loc=(0, -0.14, 4.95), m=W)
    m.box((5.0, 0.24, 0.12), "postal_red", loc=(0, -0.14, 3.85), m=W)
    env = Matrix.Translation(Vector((0, -0.25, 4.4)))
    m.box((1.3, 0.1, 0.85), "white", m=W @ env)
    m.beam((-0.62, -0.08, 0.38), (0.0, -0.08, -0.05), 0.09, "postal_red", m=W @ env)
    m.beam((0.62, -0.08, 0.38), (0.0, -0.08, -0.05), 0.09, "postal_red", m=W @ env)
    m.cylinder(0.16, 0.1, "postal_red", loc=(0, -0.1, 0.0), rot=(math.pi * 0.5, 0, 0), m=W @ env,
               base=False)
    for k in (-1, 1):
        window(m, _wall_frame(M, (k * 3.8, -d * 0.5, 1.9), "front"), 1.3, 1.5, "cream")
        window(m, _wall_frame(M, (k * 3.8, -d * 0.5, 5.2), "front"), 1.1, 1.3, "cream")
    window(m, _wall_frame(M, (0, -d * 0.5, 6.0), "front"), 1.0, 0.8, "cream")
    for side in ("left", "right"):
        sx = w * 0.5 * (-1 if side == "left" else 1)
        for k in (-1, 1):
            window(m, _wall_frame(M, (sx, k * 2.2, 1.9), side), 1.1, 1.4, "cream")
            window(m, _wall_frame(M, (sx, k * 2.2, 5.2), side), 1.0, 1.2, "cream")
    # Clock in the front gable.
    C = _wall_frame(M, (0, -d * 0.5 - 0.1, 0.3 + h + 1.5), "front")
    m.cylinder(0.95, 0.2, "cream", rot=(math.pi * 0.5, 0, 0), base=False, segments=16, m=C)
    m.cylinder(1.08, 0.12, "postal_red", loc=(0, 0.06, 0), rot=(math.pi * 0.5, 0, 0), base=False,
               segments=16, m=C)
    m.beam((0, -0.14, 0), (0, -0.14, 0.7), 0.1, "charcoal", m=C)
    m.beam((0, -0.14, 0), (0.45, -0.14, -0.2), 0.1, "charcoal", m=C)
    info["smoke"].append(chimney(m, M, -w * 0.28, d * 0.2, 0.3 + h, 0.3 + h + roof_h * 0.55 + 1.6))
    info["lights"] += [M @ Vector((k * 2.0, -d * 0.5 - 0.8, 3.0)) for k in (-1, 1)]
    info["door"] = M @ Vector((0, -d * 0.5 - 2.0, 0))
    return info


def pillar_box(m, x, y, z, rot=0.0):
    """The classic red post box."""
    M = _frame(x, y, z, rot)
    m.cylinder(0.5, 0.25, "charcoal", segments=10, m=M)
    m.cylinder(0.42, 1.3, "postal_red", loc=(0, 0, 0.25), segments=10, m=M)
    m.sphere(0.46, "postal_red", loc=(0, 0, 1.55), u=10, v=6, scale=(1, 1, 0.55), m=M)
    m.box((0.5, 0.12, 0.08), "charcoal", loc=(0, -0.38, 1.25), m=M)
    m.box((0.36, 0.06, 0.22), "cream", loc=(0, -0.41, 0.9), m=M)
    return 0.8


def lamp_post(m, x, y, z, height=3.4):
    m.cylinder(0.3, 0.3, "charcoal", loc=(x, y, z - 0.1), segments=6)
    m.cylinder(0.09, height, "charcoal", loc=(x, y, z), segments=5)
    m.box((0.46, 0.46, 0.55), "lamp", loc=(x, y, z + height), base=True)
    m.cone(0.45, 0.35, "charcoal", loc=(x, y, z + height + 0.55), segments=4, phase=math.pi * 0.25)
    return Vector((x, y, z + height + 0.3))


def fence(m, points, z_of, post_every=2.2, height=1.0, mat="wood_light"):
    pts = [Vector(p) for p in points]
    for a, b in zip(pts[:-1], pts[1:]):
        steps = max(1, int((b - a).length / post_every))
        prev = None
        for k in range(steps + 1):
            p = a.lerp(b, k / steps)
            g = z_of(p.x, p.y)
            m.box((0.18, 0.18, height + 0.4), "wood", loc=(p.x, p.y, g - 0.4), base=True)
            cur = Vector((p.x, p.y, g))
            if prev is not None:
                for rail in (0.45, 0.85):
                    m.beam(prev + Vector((0, 0, rail * height)), cur + Vector((0, 0, rail * height)),
                           0.1, mat, height=0.14)
            prev = cur


def mail_pier(m, rim, outward, z_of, rng, length=5.0):
    """A little plank dock sticking out over the void, with a post box at the end.

    `rim` is the rim ground point, `outward` a unit vector pointing off the island.
    Returns the lantern point.
    """
    out = Vector((outward.x, outward.y, 0.0)).normalized()
    side = Vector((-out.y, out.x, 0.0))
    start = Vector((rim.x, rim.y, rim.z)) - out * 3.0
    z = rim.z + 0.25
    end = start + out * (length + 3.0)
    for k in range(int((length + 3.0) / 0.55)):
        p = start + out * (0.3 + k * 0.55)
        m.beam(p - side * 1.1 + Vector((0, 0, z - p.z)), p + side * 1.1 + Vector((0, 0, z - p.z)),
               0.45, rng.choice(("wood", "wood_light")), height=0.14)
    for s in (-1, 1):
        m.beam(start + side * s * 0.9 + Vector((0, 0, z - start.z - 0.1)),
               end + side * s * 0.9 + Vector((0, 0, z - end.z - 0.1)), 0.2, "wood_dark", height=0.2)
        for t in (0.45, 1.0):
            p = start.lerp(end, t) + side * s * 0.95
            m.beam(Vector((p.x, p.y, z - 2.6)), Vector((p.x, p.y, z + 0.1)), 0.22, "wood_dark")
    tip = end - out * 0.6
    rail = [start + side * 1.0 + Vector((0, 0, z - start.z + 1.0)), tip + side * 1.0 + Vector((0, 0, z - tip.z + 1.0))]
    m.beam(rail[0], rail[1], 0.09, "wood_light")
    for t in (0.0, 0.5, 1.0):
        p = rail[0].lerp(rail[1], t)
        m.beam(Vector((p.x, p.y, z)), p, 0.1, "wood")
    rot = math.atan2(out.y, out.x) + math.pi * 0.5
    pillar_box(m, tip.x - side.x * 0.5, tip.y - side.y * 0.5, z + 0.07, rot)
    return lamp_post(m, tip.x + side.x * 0.8, tip.y + side.y * 0.8, z + 0.07, 2.6)


def well(m, x, y, z, rng):
    m.lathe([(1.5, -0.2), (1.55, 0.9), (1.25, 0.9), (1.25, 0.3)], 10, "stone", loc=(x, y, z))
    m.cylinder(1.25, 0.1, "water", loc=(x, y, z + 0.35), segments=10)
    for s in (-1, 1):
        m.box((0.2, 0.2, 2.3), "wood_dark", loc=(x + s * 1.3, y, z + 0.8), base=True)
    m.gable_roof(3.2, 1.8, 0.9, "roof_red", loc=(x, y, z + 3.1), overhang=0.2, thickness=0.15,
                 rot=(0, 0, math.pi * 0.5))
    m.cylinder(0.08, 2.7, "wood", loc=(x - 1.35, y, z + 2.6), rot=(0, math.pi * 0.5, 0), segments=5)
    m.lathe([(0.25, 0.0), (0.3, 0.4)], 6, "wood", loc=(x, y, z + 1.5))
    return 1.9


def market_stall(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((0.16, 0.16, 2.6), "wood", loc=(sx * 1.6, sy * 0.9, 0), base=True, m=M)
    m.box((3.4, 1.3, 0.9), "wood_light", loc=(0, -0.3, 0), base=True, m=M)
    colors = ("cloth_red", "cloth_cream")
    for k in range(6):
        m.box((0.6, 2.4, 0.08), colors[k % 2], loc=(-1.5 + k * 0.6, 0, 2.75), rot=(-0.22, 0, 0), m=M)
    for k in range(4):
        m.ico(0.2, rng.choice(("apple", "pumpkin", "leaf_light", "mustard")),
              loc=(-1.2 + k * 0.8, -0.55, 1.05), subdiv=1, m=M)
    return 2.2


def bench(m, x, y, z, rot):
    M = _frame(x, y, z, rot)
    m.box((1.8, 0.5, 0.1), "wood", loc=(0, 0, 0.45), base=True, m=M)
    m.box((1.8, 0.1, 0.45), "wood", loc=(0, 0.22, 0.6), base=True, m=M)
    for sx in (-1, 1):
        m.box((0.1, 0.5, 0.45), "charcoal", loc=(sx * 0.75, 0, 0), base=True, m=M)
    return 1.1


def cart(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    m.box((1.6, 2.4, 0.6), "wood", loc=(0, 0, 0.7), base=True, m=M)
    for sx in (-1, 1):
        m.cylinder(0.55, 0.12, "wood_dark", loc=(sx * 0.9, -0.3, 0.55), rot=(0, math.pi * 0.5, 0),
                   base=False, segments=10, m=M)
    m.beam((0.3, 1.2, 0.9), (0.3, 2.6, 0.5), 0.1, "wood_dark", m=M)
    m.beam((-0.3, 1.2, 0.9), (-0.3, 2.6, 0.5), 0.1, "wood_dark", m=M)
    for k in range(5):
        m.ico(0.28, rng.choice(("apple", "apple", "leaf_light", "pumpkin")),
              loc=(rng.uniform(-0.5, 0.5), rng.uniform(-0.9, 0.9), 1.4), subdiv=1, m=M)
    return 1.8


def beehive(m, x, y, z):
    for k in range(3):
        m.box((0.8, 0.8, 0.35), "mustard" if k % 2 else "cream", loc=(x, y, z + k * 0.36), base=True)
    m.box((0.95, 0.95, 0.12), "wood_dark", loc=(x, y, z + 1.08), base=True)
    return 0.7


def scarecrow(m, x, y, z, rot):
    M = _frame(x, y, z, rot)
    m.box((0.14, 0.14, 2.6), "wood", base=True, m=M)
    m.box((1.8, 0.12, 0.12), "wood", loc=(0, 0, 1.9), m=M)
    m.box((0.8, 0.5, 1.0), "cloth_teal", loc=(0, 0, 1.4), base=True, m=M)
    m.sphere(0.32, "hay", loc=(0, 0, 2.6), u=8, v=5, m=M)
    m.cone(0.55, 0.6, "hay", loc=(0, 0, 2.75), segments=8, m=M)
    return 1.0


def hangar(m, x, y, z, rot, rng, w=11.0, d=14.0):
    """Curved-roof aircraft hangar with ribbed metal roof and big front doors."""
    M = _frame(x, y, z, rot)
    r = w * 0.5
    m.box((w + 0.6, d + 0.6, 1.0), "stone", loc=(0, 0, -0.75), base=True, m=M)
    arch = [(math.cos(math.pi * k / 10) * r, math.sin(math.pi * k / 10) * r * 0.85 + 0.25)
            for k in range(11)]
    rings = [[(px, yy, pz) for (px, pz) in arch] for yy in (d * 0.5, -d * 0.5)]
    m.loft(rings, "metal", m=M, seg_mats=["metal", "stone"], stripe=1)
    W = _wall_frame(M, (0, -d * 0.5, 0.25), "front")
    m.box((w * 0.62, 0.2, r * 0.72), "wood_dark", loc=(0, -0.05, r * 0.36), m=W)
    for k in range(4):
        m.box((0.12, 0.26, r * 0.7), "wood_light", loc=(-w * 0.3 + k * w * 0.2, -0.1, r * 0.36), m=W)
    m.box((w * 0.62, 0.26, 0.14), "mustard", loc=(0, -0.12, r * 0.74), m=W)
    m.box((2.2, 0.2, 0.9), "cream", loc=(0, -0.1, r * 0.95), m=W)
    return {"radius": math.hypot(w, d) * 0.5 + 1.0, "lights": [M @ Vector((w * 0.36, -d * 0.5 - 0.5, 3.2))],
            "smoke": []}


def windmill(m, x, y, z, rot, rng):
    """Tapered octagonal tower with a teal cap. The sails are a separate SPIN_ object;
    this returns where to hang them ("sails" point) and the tower yaw."""
    M = _frame(x, y, z, rot)
    m.lathe([(5.0, -0.8), (4.9, 1.1), (4.5, 1.3)], 8, "stone", m=M, phase=math.pi / 8)
    m.lathe([(4.4, 1.2), (3.3, 11.6)], 8, "plaster", m=M, phase=math.pi / 8)
    m.lathe([(3.9, 11.5), (3.85, 12.3), (2.3, 14.3), (0.0, 15.8)], 8,
            ["wood_dark", "roof_teal", "roof_teal"], m=M, phase=math.pi / 8)
    m.lathe([(4.6, 5.2), (4.6, 5.45)], 8, "wood", m=M, phase=math.pi / 8)
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        m.beam((math.cos(a) * 4.55, math.sin(a) * 4.55, 5.45), (math.cos(a) * 4.55, math.sin(a) * 4.55, 6.4),
               0.1, "wood_dark", m=M)
    door(m, _wall_frame(M, (0, -4.25, 1.2), "front"), 1.3, 2.3)
    for (zz, s) in ((7.4, 0.8), (9.8, 0.7)):
        r = 4.4 - (zz - 1.2) * 0.106
        window(m, _wall_frame(M, (0, -r * 0.93, zz), "front"), s, s * 1.15, "cream")
        window(m, _wall_frame(M, (r * 0.93, 0, zz - 1.2), "right"), s * 0.9, s, "cream")
    m.cylinder(0.55, 1.6, "wood_dark", loc=(0, -3.6, 12.6), rot=(-math.pi * 0.5, 0, 0), m=M)
    m.beam((0, 3.6, 12.4), (0, 7.5, 3.0), 0.25, "wood_dark", m=M)
    return {"radius": 6.0, "sails": M @ Vector((0, -5.2, 12.6)), "yaw": rot,
            "lights": [M @ Vector((0, -5.2, 3.3))], "smoke": []}


def windmill_sails(name, point, yaw, rng):
    """Four lattice sails as their own object, spinning about local Y (Godot -Z)."""
    from lib.geo import Mesh
    s = Mesh()
    s.cylinder(0.7, 1.0, "wood_dark", rot=(-math.pi * 0.5, 0, 0), base=False, segments=8)
    s.cone(0.55, 0.7, "roof_teal", loc=(0, -0.5, 0), rot=(math.pi * 0.5, 0, 0), segments=8)
    for k in range(4):
        R = Matrix.Rotation(k * math.pi * 0.5 + 0.35, 4, "Y")
        s.box((0.35, 0.3, 9.6), "wood_dark", loc=(0, -0.15, 5.0), m=R)
        s.box((1.9, 0.08, 7.2), "cloth_cream", loc=(1.0, -0.3, 5.6), m=R)
        for j in range(5):
            s.box((2.05, 0.14, 0.1), "wood", loc=(1.0, -0.36, 2.4 + j * 1.6), m=R)
        s.box((0.1, 0.14, 7.2), "wood", loc=(1.98, -0.36, 5.6), m=R)
    obj = s.to_object(name, loc=point, rot=(0, 0, yaw))
    return obj


def lighthouse(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    m.lathe([(3.9, -0.8), (3.8, 1.5), (3.3, 1.8)], 12, "stone", m=M)
    zs = [1.8 + k * 3.05 for k in range(7)]
    radii = [3.1 - (zz - 1.8) * 0.045 for zz in zs]
    m.lathe(list(zip(radii, zs)), 12, ["white", "postal_red"] * 3, m=M)
    top = zs[-1]
    m.cylinder(3.3, 0.35, "charcoal", loc=(0, 0, top), segments=12, m=M)
    for k in range(12):
        a = k * math.tau / 12
        m.rod((math.cos(a) * 3.1, math.sin(a) * 3.1, top + 0.35), (math.cos(a) * 3.1, math.sin(a) * 3.1, top + 1.3),
              0.05, "charcoal", segments=4, m=M)
    m.torus(3.1, 0.07, "charcoal", loc=(0, 0, top + 1.3), major_seg=16, minor_seg=4, m=M)
    m.cylinder(1.95, 2.6, "lamp", loc=(0, 0, top + 0.35), segments=10, m=M)
    for k in range(6):
        a = k * math.tau / 6
        m.beam((math.cos(a) * 1.98, math.sin(a) * 1.98, top + 0.35), (math.cos(a) * 1.98, math.sin(a) * 1.98, top + 2.95),
               0.12, "charcoal", m=M)
    m.lathe([(2.45, top + 2.9), (2.3, top + 3.2), (1.2, top + 4.2), (0.0, top + 4.9)], 12,
            ["roof_red", "roof_red", "roof_red"], m=M)
    m.ico(0.3, "brass", loc=(0, 0, top + 5.1), subdiv=1, m=M)
    door(m, _wall_frame(M, (0, -3.12, 1.8), "front"), 1.1, 2.1, "navy")
    for zz in (7.0, 12.5):
        r = 3.1 - (zz - 1.8) * 0.045
        window(m, _wall_frame(M, (0, -r * 0.99, zz), "front"), 0.6, 0.9, "white")
    return {"radius": 4.5, "lights": [M @ Vector((0, 0, top + 1.6))], "smoke": [],
            "beacon": M @ Vector((0, 0, top + 1.6))}


def barn(m, x, y, z, rot, rng, w=9.0, d=12.0, h=4.6):
    M = _frame(x, y, z, rot)
    m.box((w + 0.5, d + 0.5, 1.0), "stone", loc=(0, 0, -0.7), base=True, m=M)
    m.box((w, d, h), "brick", loc=(0, 0, 0.3), base=True, m=M)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((0.3, 0.3, h), "white", loc=(sx * w * 0.5, sy * d * 0.5, 0.3), base=True, m=M)
    rh = w * 0.62
    hw = w * 0.5 + 0.45
    prof = [(-hw, 0.0), (-hw * 0.66, rh * 0.62), (0.0, rh), (hw * 0.66, rh * 0.62), (hw, 0.0),
            (hw - 0.3, -0.2), (-hw + 0.3, -0.2)]
    m.prism(prof, -d * 0.5 - 0.4, d * 0.5 + 0.4, "roof_slate", loc=(0, 0, 0.3 + h),
            rot=(math.pi * 0.5, 0, 0), m=M)
    gable = [(-w * 0.5, 0.0), (w * 0.5, 0.0), (w * 0.5 * 0.66, rh * 0.62 - 0.3), (0.0, rh - 0.4),
             (-w * 0.5 * 0.66, rh * 0.62 - 0.3)]
    m.prism(gable, -d * 0.5 - 0.05, d * 0.5 + 0.05, "brick", loc=(0, 0, 0.3 + h),
            rot=(math.pi * 0.5, 0, 0), m=M)
    W = _wall_frame(M, (0, -d * 0.5, 0.3), "front")
    m.box((3.6, 0.16, 3.4), "wood_dark", loc=(0, -0.05, 1.7), m=W)
    m.box((3.8, 0.2, 0.18), "white", loc=(0, -0.12, 3.45), m=W)
    for s in (-1, 1):
        m.box((0.18, 0.2, 3.4), "white", loc=(s * 1.8, -0.12, 1.7), m=W)
        m.beam((-1.7, -0.14, 0.1 if s > 0 else 3.3), (1.7, -0.14, 3.3 if s > 0 else 0.1), 0.16,
               "white", height=0.06, m=W)
    m.box((1.6, 0.16, 1.4), "wood_dark", loc=(0, -0.05, h + 1.6), m=W)
    m.box((1.8, 0.2, 0.14), "white", loc=(0, -0.12, h + 2.35), m=W)
    for side in ("left", "right"):
        sx = w * 0.5 * (-1 if side == "left" else 1)
        for k in (-1, 1):
            window(m, _wall_frame(M, (sx, k * 3.0, 2.6), side), 0.8, 0.8, "white")
    return {"radius": math.hypot(w, d) * 0.5 + 1.0, "lights": [M @ Vector((0, -d * 0.5 - 0.6, 4.0))],
            "smoke": []}


def silo(m, x, y, z, rng, r=2.8, h=13.0):
    m.cylinder(r + 0.3, 0.8, "stone", loc=(x, y, z - 0.5), segments=12)
    m.lathe([(r, 0.3)] + [(r, 0.3 + h * t) for t in (0.33, 0.66, 1.0)], 12,
            ["stone_dark", "stone", "stone_dark"], loc=(x, y, z))
    m.lathe([(r + 0.15, h + 0.3), (r * 0.7, h + 0.3 + r * 0.55), (0.0, h + 0.3 + r * 0.8)], 12,
            ["metal", "metal"], loc=(x, y, z))
    for k in range(9):
        zz = z + 1.0 + k * 1.3
        m.beam((x + r + 0.2, y - 0.3, zz), (x + r + 0.2, y + 0.3, zz), 0.07, "charcoal")
    m.beam((x + r + 0.2, y - 0.3, z), (x + r + 0.2, y - 0.3, z + h), 0.08, "charcoal")
    m.beam((x + r + 0.2, y + 0.3, z), (x + r + 0.2, y + 0.3, z + h), 0.08, "charcoal")
    return r + 0.6


def chapel(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    w, d, h = 7.5, 12.0, 5.2
    m.box((w + 0.6, d + 0.6, 1.1), "stone_dark", loc=(0, 1.0, -0.8), base=True, m=M)
    m.box((w, d, h), "stone", loc=(0, 1.0, 0.3), base=True, m=M)
    m.gable_roof(w, d, w * 0.62, "roof_slate", loc=(0, 1.0, 0.3 + h), overhang=0.4, thickness=0.28,
                 gable_mat="stone", m=M)
    for side in ("left", "right"):
        sx = w * 0.5 * (-1 if side == "left" else 1)
        for k in (-1, 0, 1):
            window(m, _wall_frame(M, (sx, 1.0 + k * 3.4, 2.9), side), 0.8, 1.9, "white")
    # Tower on the front with an open belfry, bell, and spire.
    tw, th = 4.2, 10.5
    m.box((tw, tw, th), "stone", loc=(0, -d * 0.5 + 1.0 - tw * 0.3, 0.3), base=True, m=M)
    ty = -d * 0.5 + 1.0 - tw * 0.3
    door(m, _wall_frame(M, (0, ty - tw * 0.5, 0.3), "front"), 1.5, 2.8, "door")
    m.cylinder(0.85, 0.2, "window", loc=(0, ty - tw * 0.5 - 0.05, 6.2), rot=(math.pi * 0.5, 0, 0),
               base=False, segments=12, m=M)
    m.torus(0.9, 0.12, "white", loc=(0, ty - tw * 0.5 - 0.1, 6.2), rot=(math.pi * 0.5, 0, 0), major_seg=12,
            minor_seg=4, m=M)
    bz = 0.3 + th
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((0.7, 0.7, 3.2), "stone", loc=(sx * (tw * 0.5 - 0.35), ty + sy * (tw * 0.5 - 0.35), bz),
                  base=True, m=M)
    m.box((tw + 0.4, tw + 0.4, 0.4), "stone_dark", loc=(0, ty, bz), base=True, m=M)
    m.box((tw + 0.5, tw + 0.5, 0.45), "stone_dark", loc=(0, ty, bz + 3.2), base=True, m=M)
    m.lathe([(0.25, 2.9), (0.55, 2.5), (0.95, 1.2), (1.0, 1.0)], 10, "brass", loc=(0, ty, bz), m=M)
    m.cone(tw * 0.68, 6.5, "roof_slate", loc=(0, ty, bz + 3.65), segments=4, phase=math.pi * 0.25, m=M)
    m.ico(0.3, "gold", loc=(0, ty, bz + 10.3), subdiv=1, m=M)
    return {"radius": 8.5, "lights": [M @ Vector((0, ty - tw * 0.5 - 0.8, 3.4))], "smoke": [],
            "bell": M @ Vector((0, ty, bz + 1.6)), "spire": M @ Vector((0, ty, bz + 10.4))}


def observatory(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    m.lathe([(6.4, -0.8), (6.3, 0.5), (5.8, 0.7)], 14, "stone_dark", m=M)
    m.lathe([(5.6, 0.6), (5.5, 5.5)], 14, "stone", m=M)
    m.lathe([(5.9, 5.4), (5.9, 5.8)], 14, "wood_dark", m=M)
    dome = [(5.6 * math.cos(math.radians(a)), 5.8 + 5.6 * math.sin(math.radians(a))) for a in (0, 22, 45, 68, 90)]
    dome[-1] = (0.0, dome[-1][1])
    m.lathe(dome, 14, "metal", m=M)
    m.beam((0, -5.7, 6.0), (0, -1.2, 11.1), 1.1, "charcoal", height=0.25, m=M)
    m.rod((0, 0.5, 7.5), (0, -5.0, 11.0), 0.55, "brass", segments=8, radius_end=0.45, m=M)
    m.cylinder(0.62, 0.3, "charcoal", loc=(0, -5.0, 11.0), rot=(-0.99, 0, 0), base=False, segments=8, m=M)
    door(m, _wall_frame(M, (0, -5.55, 0.6), "front"), 1.3, 2.4, "navy")
    for k in range(4):
        a = math.radians(40 + k * 60)
        W = M @ Matrix.Translation((math.cos(a) * 5.55, math.sin(a) * 5.55, 3.2)) @ \
            Matrix.Rotation(a + math.pi * 0.5, 4, "Z")
        window(m, W, 0.7, 1.0, "cream")
    return {"radius": 7.5, "lights": [M @ Vector((0, -6.4, 3.0))], "smoke": [],
            "vane": M @ Vector((0, 0, 11.5))}


def log_cabin(m, x, y, z, rot, rng, w=6.4, d=5.4, levels=7):
    M = _frame(x, y, z, rot)
    lr = 0.22
    m.box((w + 0.4, d + 0.4, 0.9), "stone", loc=(0, 0, -0.7), base=True, m=M)
    for lv in range(levels):
        zz = 0.35 + lv * 0.42
        for sy in (-1, 1):
            m.cylinder(lr, w + 0.8, rng.choice(("wood", "bark")), loc=(0, sy * d * 0.5, zz + (0.21 if sy > 0 else 0)),
                       rot=(0, math.pi * 0.5, 0), base=False, segments=6, m=M)
        for sx in (-1, 1):
            m.cylinder(lr, d + 0.8, rng.choice(("wood", "bark")), loc=(sx * w * 0.5, 0, zz + 0.21),
                       rot=(math.pi * 0.5, 0, 0), base=False, segments=6, m=M)
    h = 0.35 + levels * 0.42
    m.box((w - 0.2, d - 0.2, h - 0.2), "wood_dark", loc=(0, 0, 0.3), base=True, m=M)
    # Ridge runs along X (the long side), so the roof is turned 90 degrees:
    # its width spans the cabin's depth and its ridge spans the cabin's width.
    m.gable_roof(d + 0.4, w + 0.4, d * 0.45, "wood_dark", loc=(0, 0, h), overhang=0.5, thickness=0.3,
                 gable_mat="wood", rot=(0, 0, math.pi * 0.5), m=M)
    door(m, _wall_frame(M, (0, -d * 0.5 - 0.2, 0.3), "front"), 1.0, 2.0, "wood_dark")
    window(m, _wall_frame(M, (w * 0.28, -d * 0.5 - 0.22, 1.7), "front"), 0.8, 0.8, "wood_light")
    window(m, _wall_frame(M, (w * 0.5 + 0.22, 0, 1.7), "right"), 0.8, 0.8, "wood_light")
    smoke = chimney(m, M, -w * 0.5 - 0.1, d * 0.15, 0.3, h + d * 0.45 + 0.8, "stone")
    return {"radius": math.hypot(w, d) * 0.5 + 1.0, "lights": [M @ Vector((0, -d * 0.5 - 0.8, 2.6))],
            "smoke": [smoke], "door": M @ Vector((0, -d * 0.5 - 1.5, 0))}


def campfire(m, x, y, z, rng):
    for k in range(8):
        a = k * math.tau / 8
        m.ico(0.3, rng.choice(("rock", "rock_dark")), loc=(x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, z + 0.1),
              subdiv=1, scale=(1, 1, 0.7))
    for k in range(3):
        a = k * math.tau / 3
        m.beam((x + math.cos(a) * 0.6, y + math.sin(a) * 0.6, z + 0.05), (x, y, z + 0.6), 0.14, "bark")
    for k in range(4):
        a = k * math.tau / 4 + 0.4
        m.cylinder(0.18, 1.6, "bark", loc=(x + math.cos(a) * 2.0, y + math.sin(a) * 2.0, z + 0.2),
                   rot=(0, math.pi * 0.5, a), base=False, segments=6)
    return Vector((x, y, z + 0.5))


def woodpile(m, x, y, z, rot, rng):
    M = _frame(x, y, z, rot)
    for row in range(3):
        for k in range(4 - row):
            m.cylinder(0.2, 1.6, rng.choice(("wood", "bark", "wood_light")),
                       loc=(-0.6 + k * 0.42 + row * 0.21, 0, 0.2 + row * 0.36),
                       rot=(math.pi * 0.5, 0, 0), base=False, segments=6, m=M)
    return 1.2


def windsock(m, x, y, z, rot, height=7.0):
    M = _frame(x, y, z, rot)
    m.cylinder(0.1, height, "white", segments=5, m=M)
    m.torus(0.45, 0.05, "charcoal", loc=(0.0, 0.0, height), rot=(0, math.pi * 0.5, 0), major_seg=10,
            minor_seg=4, m=M)
    m.lathe([(0.45, 0.0), (0.38, 0.7), (0.3, 1.4), (0.22, 2.1), (0.12, 2.8)], 8,
            ["postal_red", "white", "postal_red", "white"], loc=(0, 0, height),
            rot=(0, math.pi * 0.5 + 0.25, 0), m=M)
    return 0.8


def signpost(m, x, y, z, rot, color="cream"):
    M = _frame(x, y, z, rot)
    m.box((0.16, 0.16, 2.6), "wood", base=True, m=M)
    m.box((1.4, 0.1, 0.4), color, loc=(0.55, 0, 2.2), m=M)
    m.cone(0.28, 0.35, color, loc=(1.35, 0, 2.2), rot=(0, math.pi * 0.5, 0), segments=3, base=False, m=M)
    return 0.6
