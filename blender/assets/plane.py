"""The player's mail plane: a chunky 1920s air-mail biplane. Nose points +Y (Godot -Z).

Node contract used by game code:
  SPIN_Propeller   spun around its local forward axis
  FX_Exhaust       exhaust puff emitter (right-hand exhaust stack)
  FX_WingTipL/R    contrail emitters on the upper wing tips
  MK_Parcel        where the carried parcel rides (on the rear rack)
"""

import math

from lib import scene
from lib.geo import Mesh, rounded_rect
from lib.registry import asset

# Fuselage stations: (y, width, height, z center). Nose first.
COWL = ((2.58, 0.9, 0.9, 0.0), (2.4, 1.14, 1.12, 0.0), (1.62, 1.26, 1.2, 0.02))
BODY = ((1.62, 1.26, 1.2, 0.02), (0.6, 1.24, 1.18, 0.05), (-0.6, 1.08, 1.02, 0.12),
        (-1.8, 0.74, 0.74, 0.22), (-2.9, 0.4, 0.44, 0.31), (-3.5, 0.16, 0.22, 0.35))
# Octagon faces 3 and 7 are the flat sides: paint them cream for the livery stripe.
LIVERY = ["postal_red", "postal_red", "postal_red", "cream",
          "postal_red", "postal_red", "postal_red", "cream"]


def _section(y, w, h, zc):
    pts = []
    for k in range(8):
        a = math.radians(22.5 + k * 45.0)
        pts.append((math.cos(a) * w * 0.54, y, zc + math.sin(a) * h * 0.54))
    return pts


def _wing(m, span, chord, z, y, thickness=0.16):
    outline = rounded_rect(span, chord, chord * 0.48, corner_segments=3)
    m.prism(outline, -thickness * 0.5, thickness * 0.5, "cream", loc=(0, y, z))
    for side in (-1, 1):
        cx = side * (span * 0.5 - 0.95)
        for (r, mat, dz) in ((0.52, "postal_red", 0.0), (0.33, "cream", 0.012), (0.14, "postal_red", 0.024)):
            m.cylinder(r, 0.03, mat, loc=(cx, y, z + thickness * 0.5 + dz), segments=14)


@asset("plane", icon=(-58.0, 22.0))
def build():
    body = Mesh()
    body.loft([_section(*s) for s in COWL], ["metal", "postal_red"])
    body.loft([_section(*s) for s in BODY], "postal_red", seg_mats=LIVERY)
    body.cylinder(0.3, 0.06, "charcoal", loc=(0, 2.6, 0), rot=(-math.pi * 0.5, 0, 0), base=False,
                  segments=10)

    # Exhaust stacks on both sides of the cowl.
    for side in (-1, 1):
        for k in range(3):
            y = 2.05 - k * 0.3
            body.rod((side * 0.6, y, 0.05), (side * 0.78, y - 0.35, -0.3), 0.07, "charcoal",
                     segments=5)

    # Cockpit, windscreen and pilot.
    body.cylinder(0.43, 0.08, "charcoal", loc=(0, -0.6, 0.6), segments=10)
    body.torus(0.46, 0.07, "leather", loc=(0, -0.6, 0.66), major_seg=12, minor_seg=5)
    body.box((0.72, 0.05, 0.34), "glass", loc=(0, -0.02, 0.8), rot=(-0.45, 0, 0))
    body.box((0.62, 0.42, 0.34), "leather", loc=(0, -0.66, 0.6), base=True)
    body.ico(0.22, "skin", loc=(0, -0.66, 1.08), subdiv=2)
    body.sphere(0.235, "leather", loc=(0, -0.68, 1.12), u=10, v=5, scale=(1, 1.05, 0.8))
    for side in (-1, 1):
        body.cylinder(0.075, 0.06, "brass", loc=(side * 0.09, -0.46, 1.2), rot=(-math.pi * 0.5, 0, 0),
                      base=False, segments=8)
        body.cylinder(0.05, 0.07, "glass", loc=(side * 0.09, -0.45, 1.2), rot=(-math.pi * 0.5, 0, 0),
                      base=False, segments=8)
    body.torus(0.2, 0.06, "cloth_red", loc=(0, -0.66, 0.88), major_seg=10, minor_seg=4)
    body.beam((0.05, -0.8, 0.9), (0.28, -1.75, 1.02), 0.12, "cloth_red", height=0.04)
    body.beam((-0.05, -0.8, 0.88), (-0.18, -1.6, 0.92), 0.11, "cloth_red", height=0.04)

    # Parcel rack behind the cockpit.
    for sx in (-1, 1):
        body.beam((sx * 0.3, -1.15, 0.55), (sx * 0.3, -1.95, 0.4), 0.06, "wood_dark")
    for yy in (-1.25, -1.85):
        body.beam((-0.33, yy, 0.52 + (yy + 1.25) * 0.18), (0.33, yy, 0.52 + (yy + 1.25) * 0.18),
                  0.06, "wood_dark")

    # Wings, struts and rigging.
    _wing(body, 9.0, 1.55, 1.45, 0.55)
    _wing(body, 8.2, 1.42, -0.42, 0.72)
    for side in (-1, 1):
        x = side * 3.0
        body.beam((x, 1.1, -0.34), (x, 0.95, 1.38), 0.1, "wood_dark")
        body.beam((x, 0.2, -0.34), (x, 0.05, 1.38), 0.1, "wood_dark")
        body.beam((x, 1.1, -0.34), (x, 0.05, 1.38), 0.07, "wood_dark")
        body.rod((side * 0.45, 0.6, 0.4), (x, 0.95, -0.34), 0.022, "charcoal", segments=3)
        body.rod((side * 0.45, 0.6, -0.35), (x, 0.9, 1.38), 0.022, "charcoal", segments=3)
        for yy in (0.95, 0.15):
            body.beam((side * 0.35, yy, 0.55), (side * 0.55, yy, 1.38), 0.08, "wood_dark")
    for side, mat in ((-1, "nav_red"), (1, "nav_green")):
        body.ico(0.09, mat, loc=(side * 4.48, 0.55, 1.45), subdiv=1)

    # Tail: stabilizer and a striped rudder with the envelope emblem.
    body.prism(rounded_rect(3.3, 0.95, 0.42), -0.05, 0.05, "cream", loc=(0, -3.05, 0.36))
    fin = [(-2.55, 0.45), (-2.95, 1.55), (-3.3, 1.72), (-3.62, 1.45), (-3.62, 0.3)]
    body.prism(fin, -0.05, 0.05, "postal_red", rot=(math.pi * 0.5, 0, math.pi * 0.5))
    for k, mat in enumerate(("cream", "postal_red", "cream")):
        body.box((0.12, 0.1, 0.9), mat, loc=(0, -3.38 - k * 0.001, 0.55 + k * 0.33), base=True)
    for side in (-1, 1):
        body.box((0.02, 0.5, 0.33), "cream", loc=(side * 0.06, -3.08, 1.02))
        body.beam((side * 0.075, -2.86, 1.16), (side * 0.075, -3.08, 0.98), 0.05, "postal_red", height=0.02)
        body.beam((side * 0.075, -3.3, 1.16), (side * 0.075, -3.08, 0.98), 0.05, "postal_red", height=0.02)

    # Landing gear.
    for side in (-1, 1):
        body.beam((side * 0.35, 1.05, -0.48), (side * 0.9, 0.7, -1.3), 0.08, "wood_dark")
        body.beam((side * 0.35, 0.3, -0.48), (side * 0.9, 0.7, -1.3), 0.08, "wood_dark")
        body.cylinder(0.42, 0.2, "charcoal", loc=(side * 1.0, 0.7, -1.32), rot=(0, math.pi * 0.5, 0),
                      base=False, segments=14)
        body.cylinder(0.2, 0.24, "cream", loc=(side * 1.0, 0.7, -1.32), rot=(0, math.pi * 0.5, 0),
                      base=False, segments=8)
    body.rod((-1.0, 0.7, -1.32), (1.0, 0.7, -1.32), 0.05, "metal", segments=5)
    body.beam((0, -3.2, 0.2), (0, -3.35, -0.18), 0.07, "wood_dark")
    plane = body.to_object("Plane")

    prop = Mesh()
    prop.cone(0.34, 0.55, "postal_red", rot=(-math.pi * 0.5, 0, 0), segments=10)
    prop.cylinder(0.3, 0.12, "metal", loc=(0, -0.06, 0), rot=(-math.pi * 0.5, 0, 0), base=False, segments=10)
    blade = [(-0.07, 0.0), (0.07, 0.0), (0.16, 0.55), (0.13, 1.1), (0.05, 1.3), (-0.08, 1.25), (-0.13, 0.6)]
    for k in range(2):
        ang = k * math.pi
        prop.prism(blade, -0.04, 0.04, "wood_light", rot=(math.pi * 0.5, ang + 0.25 * (1 if k else -1), 0))
        prop.box((0.24, 0.1, 0.18), "mustard", loc=(0, 0.0, 1.2 * (1 if k == 0 else -1)),
                 rot=(0, ang, 0))
    prop.to_object("SPIN_Propeller", parent=plane, loc=(0, 2.62, 0))

    scene.empty("FX_Exhaust", loc=(0.8, 1.35, -0.34), parent=plane, size=0.3)
    scene.empty("FX_WingTipL", loc=(-4.5, 0.55, 1.45), parent=plane, size=0.3)
    scene.empty("FX_WingTipR", loc=(4.5, 0.55, 1.45), parent=plane, size=0.3)
    scene.empty("MK_Parcel", loc=(0, -1.55, 0.72), parent=plane, size=0.3)
