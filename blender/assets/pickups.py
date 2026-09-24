"""Gameplay objects the plane flies through or carries (milestone 1 blockouts).

Axes: every ring's axis is +Y (Godot -Z), so a socket's forward is the flight line.
"""

import math

from lib.geo import Mesh
from lib.registry import asset

RING_ROT = (math.pi * 0.5, 0.0, 0.0)  # torus axis Z -> Y


@asset("parcel")
def parcel():
    m = Mesh()
    m.box((0.9, 0.9, 0.7), "kraft")
    m.box((0.95, 0.12, 0.75), "rope")
    m.box((0.12, 0.95, 0.75), "rope")
    m.to_object("Parcel")


@asset("hoop")
def hoop():
    m = Mesh()
    m.torus(6.0, 0.5, "grey_accent", rot=RING_ROT, major_seg=28, minor_seg=8)
    m.to_object("Hoop")


@asset("boost_ring")
def boost_ring():
    m = Mesh()
    m.torus(4.5, 0.35, "boost", rot=RING_ROT, major_seg=24, minor_seg=6)
    m.to_object("BoostRing")


@asset("stamp")
def stamp():
    m = Mesh()
    m.box((1.4, 0.12, 1.7), "grey_accent")
    m.to_object("Stamp")
