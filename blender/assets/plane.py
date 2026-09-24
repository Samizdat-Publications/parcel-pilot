"""The player's mail plane (greybox). Nose points +Y, which is Godot's -Z (forward).

Node contract used by game code:
  SPIN_Propeller   spun around its local forward axis
  FX_Exhaust       exhaust puff emitter
  FX_WingTipL/R    contrail emitters
  MK_Parcel        where the carried parcel is attached
"""

import math

from lib import scene
from lib.geo import Mesh
from lib.registry import asset


@asset("plane")
def build():
    body = Mesh()
    body.box((1.1, 4.6, 1.1), "grey_accent")
    body.box((8.5, 1.3, 0.16), "grey_light", loc=(0, 0.6, 0.15))
    body.box((3.2, 0.9, 0.12), "grey_light", loc=(0, -2.1, 0.25))
    body.box((0.12, 0.9, 1.2), "grey_light", loc=(0, -2.1, 0.7))
    body.box((0.7, 0.9, 0.35), "grey_dark", loc=(0, -0.4, 0.7))
    plane = body.to_object("Plane")

    prop = Mesh()
    prop.cylinder(0.2, 0.35, "grey_dark", rot=(-math.pi * 0.5, 0, 0), base=False)
    prop.box((0.2, 0.08, 2.4), "grey_dark")
    prop.to_object("SPIN_Propeller", parent=plane, loc=(0, 2.45, 0))

    scene.empty("FX_Exhaust", loc=(0.5, 1.7, -0.35), parent=plane, size=0.3)
    scene.empty("FX_WingTipL", loc=(-4.2, 0.6, 0.15), parent=plane, size=0.3)
    scene.empty("FX_WingTipR", loc=(4.2, 0.6, 0.15), parent=plane, size=0.3)
    scene.empty("MK_Parcel", loc=(0, -0.9, 0.6), parent=plane, size=0.3)
