"""IslandBuild: the shared recipe every island asset follows.

    b = IslandBuild(radius=34, seed=11)
    b.delivery(200)                  # hoop socket + mail pier on the rim
    info = structures.cottage(b.dress, *b.spot(8, 5), ...)
    b.fx_from(info)                  # chimney smoke / lamp sockets
    b.finish()

Objects produced (the node contract Godot relies on):
  Island-col        the terrain body, trimesh collision
  Dressing          every static prop merged into one mesh (no collision)
  Proxies-colonly   invisible boxes/cylinders that give buildings and trees collision
  Roots, Debris, Crystals, Waterfall*   decoration
  MK_*, FX_*        empties
"""

import math
import random

from mathutils import Vector

from kit import islands as isl
from kit import structures
from lib import scene
from lib.geo import Mesh


class IslandBuild:
    def __init__(self, radius, seed, depth=None, bumpiness=0.5, wobble=0.13, segs=36):
        self.shape = isl.IslandShape(radius, seed, depth=depth, segs=segs, bumpiness=bumpiness,
                                     wobble=wobble)
        self.rng = random.Random(seed * 7 + 3)
        self.place = isl.Placer(self.shape, self.rng)
        self.dress = Mesh()
        self.proxies = Mesh()
        self.fx_points = []
        self.delivery_angle = None

    # -------------------------------------------------------------- placing
    def ground(self, x, y):
        return self.shape.height(x, y)

    def spot(self, x, y, r=0.0):
        """Claim a spot and return (x, y, ground z)."""
        self.place.take(x, y, r)
        return x, y, self.ground(x, y)

    def face_center_rot(self, x, y):
        """Yaw that turns a building's front (-Y) toward the island center."""
        return math.atan2(-x, y)

    def fx(self, kind, point):
        self.fx_points.append((kind, Vector(point)))

    def fx_from(self, info):
        for p in info.get("smoke", []):
            self.fx("Smoke", p)
        for p in info.get("lights", []):
            self.fx("Light", p)

    def proxy_box(self, center, size, rot=0.0):
        self.proxies.box(size, "grey_mid", loc=center, rot=(0, 0, rot), base=True)

    def proxy_cyl(self, center, radius, height):
        self.proxies.cylinder(radius, height, "grey_mid", loc=center, segments=8)

    # ----------------------------------------------------------- set pieces
    def delivery(self, angle_deg, height=9.0, pier=True):
        """Hoop socket just off the rim, axis tangent to the edge, plus a mail pier."""
        a = math.radians(angle_deg)
        self.delivery_angle = a
        rim = self.shape.rim_point(a)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        socket = rim + out * 9.0 + Vector((0, 0, height))
        scene.empty("MK_Delivery", loc=socket, rot=(0.0, 0.0, a), size=3.0)
        if pier:
            lamp = structures.mail_pier(self.dress, rim, out, self.ground, self.rng)
            self.fx("Light", lamp)
            inner = rim - out * 6.0
            self.place.reserve_path([(rim.x, rim.y), (inner.x, inner.y)], 3.2)
        return rim - out * 5.0

    def trees(self, count, kind="round", r=2.6, palette="summer", min_r=0.0, max_r=None,
              fruit=None, height=None, proxies=True):
        from kit import nature
        spots = self.place.scatter(count, r, min_r=min_r, max_r=max_r)
        for (x, y, z) in spots:
            if kind == "pine":
                h = height or self.rng.uniform(8, 12)
                nature.pine(self.dress, x, y, z, self.rng, h)
                if proxies:
                    self.proxy_cyl((x, y, z - 0.5), h * 0.14, h * 0.9)
            elif kind == "birch":
                h = height or 7.0
                nature.birch(self.dress, x, y, z, self.rng, h)
                if proxies:
                    self.proxy_cyl((x, y, z - 0.5), 1.4, h)
            else:
                h = height or self.rng.uniform(4.8, 6.4)
                nature.round_tree(self.dress, x, y, z, self.rng, h, palette, fruit)
                if proxies:
                    self.proxy_cyl((x, y, z - 0.5), h * 0.3, h * 1.05)
        return spots

    def scatter_small(self, bushes=6, rocks=4, flowers=6, tufts=14, mushrooms=0):
        from kit import nature
        for (x, y, z) in self.place.scatter(bushes, 1.3):
            nature.bush(self.dress, x, y, z, self.rng, self.rng.uniform(0.9, 1.4),
                        flowers=self.rng.choice([None, "flower_pink", "flower_white", "flower_yellow"]))
        for (x, y, z) in self.place.scatter(rocks, 1.2):
            nature.rock(self.dress, x, y, z, self.rng, self.rng.uniform(0.6, 1.3),
                        self.rng.choice(["rock", "rock_light"]))
        for (x, y, z) in self.place.scatter(flowers, 1.1):
            nature.flower_patch(self.dress, x, y, z, self.rng)
        for (x, y, z) in self.place.scatter(tufts, 0.35):
            nature.grass_tuft(self.dress, x, y, z, self.rng)
        for (x, y, z) in self.place.scatter(mushrooms, 0.5):
            nature.mushroom(self.dress, x, y, z, self.rng, self.rng.uniform(0.35, 0.6))

    # ---------------------------------------------------------------- finish
    def finish(self, roots=10, debris=5, crystals=0, waterfall_deg=None, body_kwargs=None):
        isl.build_body(self.shape, **(body_kwargs or {}))
        if roots:
            isl.build_roots(self.shape, roots)
        if debris:
            isl.build_debris(self.shape, debris)
        if crystals:
            isl.build_crystals(self.shape, crystals)
        if waterfall_deg is not None:
            isl.build_waterfall(self.shape, math.radians(waterfall_deg))
        if not self.dress.is_empty():
            self.dress.to_object("Dressing")
        if not self.proxies.is_empty():
            self.proxies.to_object("Proxies-colonly")
        counts = {}
        for kind, p in self.fx_points:
            counts[kind] = counts.get(kind, 0) + 1
            scene.empty(f"FX_{kind}_{counts[kind]}", loc=p, size=0.5)
