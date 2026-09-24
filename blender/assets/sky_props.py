"""Clouds, the storm cloud (with its lightning bolt), and the hot air balloon."""

import math
import random

from mathutils import Vector

from lib import scene
from lib.geo import Mesh
from lib.registry import asset


def _cloud(m, seed, count, spread, size, top="cloud", under="cloud_shade", flat=0.35):
    """Overlapping faceted puffs with a flattened base and a lavender underside."""
    rng = random.Random(seed)
    base_z = -size * flat
    for i in range(count):
        t = i / max(count - 1, 1)
        x = (t - 0.5) * spread + rng.uniform(-size * 0.3, size * 0.3)
        y = rng.uniform(-spread * 0.16, spread * 0.16)
        r = size * (0.55 + 0.45 * math.sin(t * math.pi)) * rng.uniform(0.85, 1.15)
        faces = m.ico(r, top, loc=(x, y, r * 0.3), subdiv=2, scale=(1.0, 0.9, 0.78),
                      rot=(0, 0, rng.uniform(0, math.tau)))
        m.jitter(faces, r * 0.06, rng)
        for v in m.verts_of(faces):
            if v.co.z < base_z:
                v.co.z = base_z + (v.co.z - base_z) * 0.08
        for f in faces:
            f.normal_update()
            if f.normal.z < -0.35:
                m.paint([f], under)


@asset("cloud_a")
def cloud_a():
    m = Mesh()
    _cloud(m, 1, 5, 26, 7)
    m.to_object("Cloud")


@asset("cloud_b")
def cloud_b():
    m = Mesh()
    _cloud(m, 2, 7, 38, 8)
    m.to_object("Cloud")


@asset("cloud_c")
def cloud_c():
    m = Mesh()
    _cloud(m, 3, 4, 18, 6)
    m.to_object("Cloud")


@asset("storm_cloud")
def storm_cloud():
    m = Mesh()
    _cloud(m, 4, 8, 46, 11, top="storm", under="storm_dark", flat=0.3)
    m.to_object("StormCloud")
    rng = random.Random(9)
    bolt = Mesh()
    p = Vector((0.0, 0.0, -3.0))
    pts = [p.copy()]
    for k in range(6):
        p += Vector((rng.uniform(-2.2, 2.2), rng.uniform(-1.0, 1.0), -4.2))
        pts.append(p.copy())
    bolt.tube(pts, 0.35, "bolt", segments=4, taper=0.3)
    branch = [pts[2], pts[2] + Vector((3.0, 0.5, -3.5)), pts[2] + Vector((4.5, 0.2, -8.0))]
    bolt.tube(branch, 0.2, "bolt", segments=4, taper=0.2)
    bolt.to_object("BOLT_Lightning")
    scene.empty("FX_Lightning", loc=(0, 0, -6), size=2)


@asset("balloon")
def balloon():
    m = Mesh()
    prof = [(0.9, 6.0), (2.2, 7.2), (5.4, 10.5), (7.0, 14.0), (6.7, 17.0), (5.0, 19.4), (2.4, 20.6), (0.0, 21.0)]
    m.lathe(prof, 16, "postal_red", seg_mats=["postal_red", "cream", "mustard", "cream"], stripe=1)
    m.lathe([(1.1, 5.4), (0.95, 6.1)], 16, "wood_dark")
    m.lathe([(1.25, 0.0), (1.35, 1.35), (1.4, 1.4)], 8, "wood_light")
    m.torus(1.38, 0.1, "wood_dark", loc=(0, 0, 1.4), major_seg=8, minor_seg=4)
    for k in range(4):
        a = math.pi * 0.25 + k * math.pi * 0.5
        m.rod((math.cos(a) * 1.25, math.sin(a) * 1.25, 1.4), (math.cos(a) * 0.95, math.sin(a) * 0.95, 5.5),
              0.04, "rope", segments=3)
        m.ico(0.28, "kraft", loc=(math.cos(a) * 1.5, math.sin(a) * 1.5, 0.9), subdiv=1, scale=(1, 1, 1.3))
    m.cylinder(0.35, 0.6, "metal", loc=(0, 0, 3.6), segments=8)
    m.cone(0.3, 0.6, "lamp", loc=(0, 0, 4.2), segments=6)
    m.to_object("Balloon")
    scene.empty("FX_Light_Burner", loc=(0, 0, 4.6), size=0.5)
