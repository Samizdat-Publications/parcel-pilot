"""Floating islands, milestone 1 blockouts.

Node contract per island (kept through the art pass):
  Island-col      visible body with trimesh collision (Godot `-col` suffix)
  MK_Delivery     delivery hoop socket; +Y (Godot -Z) is the hoop axis
  MK_Spawn        (post office only) where a shift starts
  MK_Stamp*       collectible stamp sockets
  SPIN_*          parts spun by the game (windmill sails)
Island tops sit at z = 0; the game places islands in world.tscn.
"""

import math

from kit.blockout import cone_tree, delivery_socket, house, island_body, round_tree
from lib import scene
from lib.geo import Mesh
from lib.registry import asset


def _finish(m):
    return m.to_object("Island-col")


@asset("island_post_office")
def post_office():
    m = Mesh()
    island_body(m, 34, 42, seed=11)
    house(m, 0, 4, 16, 11, 9, roof_h=5)
    m.box((5, 5, 15), "grey_light", loc=(-9, 4, 0), base=True)
    m.cylinder(0.25, 18, "grey_dark", loc=(-12, -10, 0), segments=6)
    m.box((0.1, 4.0, 2.4), "grey_accent", loc=(-12, -8, 15.5))
    for i in range(5):
        m.box((1.6, 1.6, 1.4), "grey_mid", loc=(8 + (i % 3) * 1.8, -8 - (i // 3) * 1.8, 0),
              base=True)
    _finish(m)
    delivery_socket(34, 200)
    scene.empty("MK_Spawn", loc=(0, -75, 24), size=3)
    scene.empty("MK_Stamp_1", loc=(0, 4, 26), size=1)


@asset("island_windmill")
def windmill():
    m = Mesh()
    island_body(m, 28, 34, seed=22)
    m.cylinder(4.2, 13, "grey_light", loc=(3, 3, 0), radius_top=3.1, segments=8)
    m.cone(4.4, 4.5, "grey_accent", loc=(3, 3, 13), segments=8)
    for i in range(4):
        m.box((14, 2.2, 0.4), "grey_mid", loc=(-10, -10 + i * 3.2, 0.2), base=True)
    house(m, -12, 9, 6, 5, 3.5, rz=0.4)
    _finish(m)
    sails = Mesh()
    for i in range(4):
        ang = i * math.pi * 0.5
        sails.box((1.4, 0.25, 9.0), "grey_dark", loc=(math.sin(ang) * 4.6, 0, math.cos(ang) * 4.6),
                  rot=(0, ang, 0))
    sails.cylinder(0.6, 1.2, "grey_dark", rot=(-math.pi * 0.5, 0, 0), base=False)
    sails.to_object("SPIN_Sails", loc=(3, -1.6, 12.5))
    delivery_socket(28, 30)
    scene.empty("MK_Stamp_1", loc=(3, -1.6, 24), size=1)


@asset("island_lighthouse")
def lighthouse():
    m = Mesh()
    island_body(m, 16, 64, seed=33)
    m.cylinder(3.2, 22, "grey_light", radius_top=2.4, segments=10)
    m.cylinder(2.8, 3.2, "grey_accent", loc=(0, 0, 22), segments=10)
    m.cone(3.3, 3.0, "grey_dark", loc=(0, 0, 25.2), segments=10)
    house(m, 7, -5, 5, 4, 3, rz=0.7)
    _finish(m)
    delivery_socket(16, 300, height=12)
    for i in range(3):
        a = math.radians(40 + i * 110)
        scene.empty(f"MK_Stamp_{i + 1}", loc=(math.cos(a) * 13, math.sin(a) * 13, 30), size=1)


@asset("island_village")
def village():
    m = Mesh()
    island_body(m, 36, 38, seed=44)
    for (x, y, w, d, h, rz) in ((-12, 8, 8, 6, 5, 0.2), (6, 12, 7, 6, 4.5, -0.4),
                                (12, -6, 9, 7, 5.5, 1.3), (-8, -12, 7, 5, 4, 0.9)):
        house(m, x, y, w, d, h, rz=rz)
    m.cylinder(1.6, 1.4, "grey_mid", loc=(0, 0, 0), segments=10)
    for (x, y) in ((-24, -4), (22, 14), (18, -20), (-20, 20), (0, 26)):
        round_tree(m, x, y)
    _finish(m)
    delivery_socket(36, 120)


@asset("island_orchard")
def orchard():
    m = Mesh()
    island_body(m, 27, 30, seed=55)
    for row in range(3):
        for col in range(4):
            round_tree(m, -11 + col * 7, -6 + row * 7, h=4.5, r=2.0)
    house(m, 12, 14, 6, 5, 3.5, rz=-0.3)
    _finish(m)
    delivery_socket(27, 250)


@asset("island_forest")
def forest():
    m = Mesh()
    island_body(m, 31, 36, seed=66)
    import random
    rng = random.Random(6)
    for _ in range(22):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(6, 25)
        cone_tree(m, math.cos(a) * r, math.sin(a) * r, h=rng.uniform(8, 13))
    house(m, 0, 0, 6, 5, 3.5, rz=0.5)
    _finish(m)
    delivery_socket(31, 60)


@asset("island_farm")
def farm():
    m = Mesh()
    island_body(m, 33, 34, seed=77)
    house(m, -6, 6, 12, 16, 7, rz=0.15, roof_h=5)
    m.cylinder(3.2, 15, "grey_light", loc=(9, 12, 0), segments=10)
    m.sphere(3.2, "grey_accent", loc=(9, 12, 15), u=10, v=6, scale=(1, 1, 0.6))
    for i in range(3):
        m.box((18, 3.0, 0.4), "grey_mid", loc=(4, -10 - i * 4, 0.2), base=True)
    _finish(m)
    delivery_socket(33, 160)


@asset("island_chapel")
def chapel():
    m = Mesh()
    island_body(m, 21, 40, seed=88)
    house(m, 0, -2, 8, 14, 7, roof_h=4.5)
    m.box((4.2, 4.2, 16), "grey_light", loc=(0, 7, 0), base=True)
    m.cone(3.2, 7, "grey_accent", loc=(0, 7, 16), segments=4, phase=math.pi * 0.25)
    _finish(m)
    delivery_socket(21, 340)
    scene.empty("MK_Stamp_1", loc=(0, 7, 28), size=1)


@asset("island_observatory")
def observatory():
    m = Mesh()
    island_body(m, 19, 50, seed=99)
    m.cylinder(6, 6, "grey_light", segments=12)
    m.sphere(6, "grey_mid", loc=(0, 0, 6), u=12, v=8, scale=(1, 1, 0.85))
    m.cylinder(0.9, 7, "grey_dark", loc=(0, 1, 8), rot=(-0.9, 0, 0), segments=8)
    _finish(m)
    delivery_socket(19, 90)


@asset("island_arch")
def arch():
    """Two rock pillars joined by a bridge. The hoop hangs inside the opening."""
    m = Mesh()
    for side in (-1, 1):
        m.lathe([(0.0, -46), (5.0, -30), (7.5, -8), (6.5, 14), (6.0, 22)], 9, "grey_mid",
                loc=(side * 17, 0, 0))
    m.box((48, 14, 7), "grey_mid", loc=(0, 0, 21), base=True)
    m.box((48, 14, 0.6), "grey_light", loc=(0, 0, 28), base=True)
    _finish(m)
    scene.empty("MK_Delivery", loc=(0, 0, 6), rot=(0, 0, 0), size=3)
    scene.empty("MK_Stamp_1", loc=(0, 0, 34), size=1)


def _islet(seed, radius, depth, trees):
    m = Mesh()
    island_body(m, radius, depth, seed=seed, segs=10)
    for (x, y, h) in trees:
        round_tree(m, x, y, h=h, r=h * 0.4)
    _finish(m)


@asset("islet_a")
def islet_a():
    _islet(101, 8, 14, [(0, 0, 5)])


@asset("islet_b")
def islet_b():
    _islet(102, 6, 11, [])


@asset("islet_c")
def islet_c():
    _islet(103, 10, 18, [(-3, 2, 6), (3, -2, 4)])
