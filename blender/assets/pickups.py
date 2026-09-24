"""Gameplay objects the plane flies through or carries.

Axes: every ring's axis is +Y (Godot -Z), so a socket's forward is the flight line.
"""

import math

from lib.geo import Mesh, rounded_rect, scalloped_rect
from lib.registry import asset

RING_ROT = (math.pi * 0.5, 0.0, 0.0)  # torus axis Z -> Y


@asset("parcel")
def parcel():
    m = Mesh()
    w, d, h = 0.8, 0.7, 0.52
    m.prism(rounded_rect(w, d, 0.07, 1), 0.0, h, "kraft", loc=(0, 0, -h * 0.5))
    m.box((w + 0.03, 0.08, h + 0.03), "rope")
    m.box((0.08, d + 0.03, h + 0.03), "rope")
    m.box((0.32, 0.24, 0.02), "paper", loc=(0.17, -0.14, h * 0.5 + 0.01))
    m.box((0.1, 0.12, 0.025), "postal_red", loc=(0.27, -0.2, h * 0.5 + 0.02))
    m.cylinder(0.09, 0.04, "apple", loc=(0, 0, h * 0.5 + 0.01), segments=8)
    m.to_object("Parcel")


@asset("hoop")
def hoop():
    m = Mesh()
    m.torus(6.0, 0.48, "postal_red", rot=RING_ROT, major_seg=32, minor_seg=8,
            seg_mats=["postal_red", "cream"], stripe=2)
    m.torus(6.0, 0.2, "gold", loc=(0, 0.42, 0), rot=RING_ROT, major_seg=32, minor_seg=4)
    m.torus(6.0, 0.2, "gold", loc=(0, -0.42, 0), rot=RING_ROT, major_seg=32, minor_seg=4)
    for k in range(8):
        a = k * math.tau / 8 + math.tau / 16
        m.ico(0.3, "lamp", loc=(math.cos(a) * 6.55, 0, math.sin(a) * 6.55), subdiv=1)
    # Envelope emblem on top, readable from both sides.
    for side in (-1, 1):
        y = side * 0.35
        m.box((1.7, 0.1, 1.15), "white", loc=(0, y, 7.1))
        m.beam((-0.8, y + side * 0.07, 7.62), (0.0, y + side * 0.07, 7.0), 0.1, "postal_red", height=0.04)
        m.beam((0.8, y + side * 0.07, 7.62), (0.0, y + side * 0.07, 7.0), 0.1, "postal_red", height=0.04)
    m.cylinder(0.22, 0.9, "postal_red", loc=(0, 0, 7.0), rot=RING_ROT, base=False, segments=10)
    # Pennants hanging from the bottom of the ring.
    for k in range(5):
        a = math.radians(225 + k * 22.5)
        p = (math.cos(a) * 6.2, 0, math.sin(a) * 6.2)
        m.cone(0.45, 1.3, ("cloth_teal", "cloth_mustard", "cloth_cream")[k % 3], loc=p,
               rot=(math.pi, 0, 0), segments=3)
    m.to_object("Hoop")


@asset("boost_ring")
def boost_ring():
    m = Mesh()
    m.torus(4.5, 0.32, "boost", rot=RING_ROT, major_seg=28, minor_seg=6)
    m.torus(4.95, 0.12, "white", rot=RING_ROT, major_seg=28, minor_seg=4)
    for k in range(6):
        a = k * math.tau / 6
        c = (math.cos(a) * 4.5, 0.0, math.sin(a) * 4.5)
        m.cone(0.3, 0.9, "white", loc=c, rot=(0.0, math.pi * 0.5 - a, 0.0), segments=4, base=False)
    m.to_object("BoostRing")


@asset("stamp")
def stamp():
    m = Mesh()
    card = scalloped_rect(1.5, 1.85, 6, 7, 0.08)
    m.prism(card, -0.05, 0.05, "white", rot=(math.pi * 0.5, 0, 0))
    for side in (-1, 1):
        y = side * 0.065
        m.box((1.16, 0.03, 1.5), "teal", loc=(0, y, 0.0))
        m.box((1.16, 0.035, 0.42), "grass_light", loc=(0, y * 1.05, -0.54))
        m.ico(0.2, "gold", loc=(0.36, y * 1.2, 0.46), subdiv=1, scale=(1, 0.2, 1))
        # An envelope with a red flap and wax seal.
        m.box((0.74, 0.04, 0.5), "cream", loc=(-0.08, y * 1.25, -0.02))
        m.beam((-0.44, y * 1.4, 0.22), (-0.08, y * 1.4, -0.06), 0.06, "postal_red", height=0.02)
        m.beam((0.28, y * 1.4, 0.22), (-0.08, y * 1.4, -0.06), 0.06, "postal_red", height=0.02)
        m.cylinder(0.07, 0.03, "apple", loc=(-0.08, y * 1.5, -0.06), rot=(math.pi * 0.5, 0, 0),
                   base=False, segments=8)
    m.to_object("Stamp")
