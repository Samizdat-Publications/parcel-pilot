"""Small rocky islets: scenery and obstacles between the destinations."""

from kit import nature
from kit.build import IslandBuild
from lib.registry import asset


def _islet(seed, radius, depth, trees=(), pines=(), rocks=2, crystals=0):
    b = IslandBuild(radius=radius, seed=seed, depth=depth, bumpiness=0.3, segs=16)
    for (x, y, h) in trees:
        _, _, z = b.spot(x, y, 2.0)
        nature.round_tree(b.dress, x, y, z, b.rng, h, "summer")
        b.proxy_cyl((x, y, z - 0.5), h * 0.3, h)
    for (x, y, h) in pines:
        _, _, z = b.spot(x, y, 2.0)
        nature.pine(b.dress, x, y, z, b.rng, h)
        b.proxy_cyl((x, y, z - 0.5), h * 0.15, h)
    b.scatter_small(bushes=1, rocks=rocks, flowers=1, tufts=5)
    b.finish(roots=4, debris=2, crystals=crystals, body_kwargs={"stalactites": False})


@asset("islet_a")
def islet_a():
    _islet(101, 8.0, 15.0, trees=[(0.5, 0.0, 5.0)])


@asset("islet_b")
def islet_b():
    _islet(102, 6.0, 12.0, rocks=3, crystals=2)


@asset("islet_c")
def islet_c():
    _islet(103, 10.0, 19.0, pines=[(-3.0, 2.0, 7.0), (3.0, -2.0, 5.5)])
