"""Clouds, storm cloud, and hot air balloon (milestone 1 blockouts)."""

import math
import random

from lib import scene
from lib.geo import Mesh
from lib.registry import asset


def _puffs(m, seed, count, spread, size, mat):
    rng = random.Random(seed)
    for i in range(count):
        t = i / max(count - 1, 1)
        x = (t - 0.5) * spread + rng.uniform(-2, 2)
        y = rng.uniform(-spread * 0.18, spread * 0.18)
        r = size * (0.6 + 0.4 * math.sin(t * math.pi)) * rng.uniform(0.85, 1.15)
        m.ico(r, mat, loc=(x, y, r * 0.35), subdiv=1, scale=(1.0, 0.85, 0.75))


@asset("cloud_a")
def cloud_a():
    m = Mesh()
    _puffs(m, 1, 5, 26, 7, "cloud")
    m.to_object("Cloud")


@asset("cloud_b")
def cloud_b():
    m = Mesh()
    _puffs(m, 2, 7, 38, 8, "cloud")
    m.to_object("Cloud")


@asset("cloud_c")
def cloud_c():
    m = Mesh()
    _puffs(m, 3, 4, 18, 6, "cloud")
    m.to_object("Cloud")


@asset("storm_cloud")
def storm_cloud():
    m = Mesh()
    _puffs(m, 4, 8, 46, 11, "storm")
    m.to_object("StormCloud")
    scene.empty("FX_Lightning", loc=(0, 0, -6), size=2)


@asset("balloon")
def balloon():
    m = Mesh()
    m.sphere(7.0, "grey_accent", loc=(0, 0, 14), u=12, v=10, scale=(1, 1, 1.15))
    m.box((2.4, 2.4, 1.6), "grey_dark", loc=(0, 0, 2.2), base=True)
    for (x, y) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        m.cylinder(0.06, 4.6, "grey_dark", loc=(x * 1.1, y * 1.1, 3.8), segments=4)
    m.to_object("Balloon")
