"""Floating island generator.

An island is one watertight loft: a gently bumpy grass top, an overhanging soil
lip, then jagged rock strata narrowing to a tip, plus optional stalactites.
Around it: hanging roots, crystal clusters, waterfalls, floating debris.
`Placer` hands out ground positions for dressing so nothing overlaps.
"""

import math
import random

from mathutils import Vector

from kit import nature
from lib import scene
from lib.geo import Mesh, fbm

# Rock bands from just under the soil down to the tip.
STRATA = ("sandstone", "clay", "sandstone", "rock", "rock_light", "rock", "rock_dark", "deep_rock")
# (depth fraction, radius factor) for each strata ring.
UNDERSIDE = ((0.07, 0.93), (0.15, 0.87), (0.25, 0.78), (0.36, 0.67), (0.48, 0.55),
             (0.61, 0.42), (0.74, 0.29), (0.86, 0.16))
TOP_RINGS = (0.2, 0.38, 0.55, 0.7, 0.82, 0.92, 1.0)


class IslandShape:
    """Outline, ground height and depth of one island. Units in meters, top near z=0."""

    def __init__(self, radius, seed, depth=None, segs=36, bumpiness=0.5, wobble=0.13):
        self.radius = radius
        self.seed = seed
        self.segs = segs
        self.depth = depth if depth is not None else radius * 1.25
        self.bumpiness = bumpiness
        self.edge = []
        for i in range(segs):
            a = math.tau * i / segs
            n = fbm((math.cos(a) * 1.3 + seed * 0.37, math.sin(a) * 1.3, 0.5), seed=seed, octaves=3)
            self.edge.append(radius * (1.0 + wobble * n * 1.8))

    def edge_radius(self, angle):
        t = (angle % math.tau) / math.tau * self.segs
        i = int(t)
        f = t - i
        return self.edge[i % self.segs] * (1 - f) + self.edge[(i + 1) % self.segs] * f

    def height(self, x, y):
        r = math.hypot(x, y)
        u = min(r / max(self.edge_radius(math.atan2(y, x)), 0.01), 1.0)
        dome = self.bumpiness * 1.2 * (1.0 - u * u)
        bumps = self.bumpiness * fbm((x * 0.07, y * 0.07, self.seed * 0.13), self.seed + 5, octaves=2)
        return dome + bumps * (1.0 - u ** 4)

    def inside(self, x, y, margin=0.0):
        return math.hypot(x, y) < self.edge_radius(math.atan2(y, x)) - margin

    def rim_point(self, angle, out=0.0):
        r = self.edge_radius(angle) + out
        x, y = math.cos(angle) * r, math.sin(angle) * r
        return Vector((x, y, self.height(x * 0.98, y * 0.98)))


def build_body(shape, name="Island-col", top="grass", strata=STRATA, stalactites=True):
    """The island itself as one mesh object with trimesh collision."""
    rng = random.Random(shape.seed + 1)
    m = Mesh()
    segs = shape.segs
    rings = [[(0.0, 0.0, shape.height(0.0, 0.0))]]
    for t in TOP_RINGS:
        ring = []
        for i in range(segs):
            a = math.tau * i / segs + (0.5 / segs * math.tau if t < 1.0 and len(rings) % 2 else 0.0)
            r = shape.edge_radius(a) * t
            x, y = math.cos(a) * r, math.sin(a) * r
            ring.append((x, y, shape.height(x, y)))
        rings.append(ring)
    edge_z = [p[2] for p in rings[-1]]

    def ring_at(factor, z_of, jitter_r=0.0, jitter_z=0.0):
        ring = []
        for i in range(segs):
            a = math.tau * i / segs
            n = fbm((math.cos(a) * 2.1, math.sin(a) * 2.1, factor * 3.0 + shape.seed * 0.1),
                    seed=shape.seed + 9, octaves=2)
            r = shape.edge[i] * factor * (1.0 + jitter_r * n) * (1.0 + rng.uniform(-0.03, 0.03))
            z = z_of(i) + rng.uniform(-jitter_z, jitter_z)
            ring.append((math.cos(a) * r, math.sin(a) * r, z))
        return ring

    rings.append(ring_at(1.035, lambda i: edge_z[i] - 0.35))            # grass lip
    rings.append(ring_at(1.0, lambda i: edge_z[i] - 1.2, 0.02))         # soil under the lip
    rings.append(ring_at(0.975, lambda i: -2.6, 0.04, 0.2))             # soil band
    mats = [top] * len(TOP_RINGS) + [top, "dirt_dark", "dirt"]
    for k, (dz, fr) in enumerate(UNDERSIDE):
        rings.append(ring_at(fr, lambda i, dz=dz: -2.6 - dz * (shape.depth - 2.6), 0.16, 0.9))
        mats.append(strata[min(k, len(strata) - 1)])
    rings.append([(rng.uniform(-1, 1), rng.uniform(-1, 1), -shape.depth)])
    mats.append(strata[-1])
    faces = m.loft(rings, mats)

    top_faces = faces[: segs * len(TOP_RINGS)]
    m.speckle(top_faces, "grass_dark", 0.1, rng)
    m.speckle(top_faces, "grass_light", 0.06, rng)

    if stalactites and shape.radius > 14:
        for k in range(rng.randint(2, 3)):
            a = rng.uniform(0, math.tau)
            d = shape.radius * rng.uniform(0.25, 0.45)
            length = shape.depth * rng.uniform(0.62, 0.85)
            r0 = shape.radius * rng.uniform(0.13, 0.2)
            m.lathe([(r0, -shape.depth * 0.35), (r0 * 0.75, -length * 0.8), (0.0, -length)], 7,
                    ["rock_dark", "deep_rock"], loc=(math.cos(a) * d, math.sin(a) * d, 0),
                    jitter=r0 * 0.12, rng=rng)
    return m.to_object(name)


def build_roots(shape, count=10, seed=0, name="Roots"):
    rng = random.Random(shape.seed + 200 + seed)
    m = Mesh()
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        base = shape.edge_radius(a) * 0.985
        out = Vector((math.cos(a), math.sin(a), 0))
        start = out * base + Vector((0, 0, -1.4))
        length = rng.uniform(3.5, 9.0)
        pts = [start]
        for k in range(1, 5):
            t = k / 4
            pts.append(start + out * (0.5 * math.sin(t * 2.2)) +
                       Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), -length * t)))
        m.tube(pts, rng.uniform(0.1, 0.18), rng.choice(["bark", "moss", "bark"]), segments=4,
               taper=0.15)
    return m.to_object(name) if not m.is_empty() else None


def build_crystals(shape, count=3, seed=0, name="Crystals"):
    rng = random.Random(shape.seed + 300 + seed)
    m = Mesh()
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        dz = rng.uniform(0.2, 0.45)
        fr = 0.93 - dz * 0.75
        z = -2.6 - dz * (shape.depth - 2.6)
        base = Vector((math.cos(a), math.sin(a), 0)) * shape.edge_radius(a) * fr + Vector((0, 0, z))
        out = Vector((math.cos(a), math.sin(a), -0.6)).normalized()
        for _ in range(rng.randint(3, 5)):
            d = (out + Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.2)))).normalized()
            length = rng.uniform(1.2, 2.8)
            w = length * 0.22
            m.tube([base - d * 0.6, base + d * (length * 0.7), base + d * length], w, "crystal",
                   segments=5, radii=[w * 0.8, w, 0.0])
    return m.to_object(name) if not m.is_empty() else None


def build_debris(shape, count=5, seed=0, name="Debris"):
    rng = random.Random(shape.seed + 400 + seed)
    m = Mesh()
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        r = shape.edge_radius(a) * rng.uniform(0.9, 1.4)
        c = Vector((math.cos(a) * r, math.sin(a) * r, -shape.depth * rng.uniform(0.15, 0.6)))
        nature.floating_rock(m, c, rng.uniform(0.8, 2.2), rng,
                             mat=rng.choice(["rock", "rock_dark", "sandstone"]))
    return m.to_object(name)


def build_waterfall(shape, angle, name="Waterfall", drop=30.0, width=2.4):
    """A stream sheet spilling over the rim, thinning into mist. Returns its mist point."""
    top = shape.rim_point(angle, -0.6)
    out = Vector((math.cos(angle), math.sin(angle), 0.0))
    side = Vector((-out.y, out.x, 0.0))
    path = [top + Vector((0, 0, 0.12)), top + out * 1.2 + Vector((0, 0, -0.2)),
            top + out * 2.0 + Vector((0, 0, -2.5)), top + out * 2.5 + Vector((0, 0, -9.0)),
            top + out * 2.8 + Vector((0, 0, -drop * 0.6)), top + out * 3.0 + Vector((0, 0, -drop))]
    widths = [width * 0.8, width, width, width * 0.9, width * 0.65, width * 0.3]
    rings = []
    for p, w in zip(path, widths):
        rings.append([p - side * w * 0.5 - out * 0.1, p + side * w * 0.5 - out * 0.1,
                      p + side * w * 0.5 + out * 0.1, p - side * w * 0.5 + out * 0.1])
    m = Mesh()
    m.loft(rings, "water")
    mist = Mesh()
    rng = random.Random(shape.seed + 500)
    end = path[-1]
    for _ in range(4):
        off = Vector((rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), rng.uniform(-1.0, 1.0)))
        mist.ico(rng.uniform(1.0, 1.8), "cloud", loc=end + off, subdiv=1)
    m.to_object(name)
    mist.to_object(name + "Mist")
    scene.empty("FX_Mist_" + name, loc=end, size=1.0)
    # A small pool feeding the fall.
    pond = Mesh()
    pond_center = shape.rim_point(angle, -3.5)
    pond.cylinder(2.6, 0.12, "water", loc=pond_center + Vector((0, 0, 0.05)), segments=10)
    pond.lathe([(2.9, 0.0), (3.2, 0.2), (2.7, 0.35)], 10, "stone",
               loc=pond_center + Vector((0, 0, -0.1)))
    pond.to_object(name + "Pond")
    return end


class Placer:
    """Hands out free, on-island ground spots for dressing."""

    def __init__(self, shape, rng):
        self.shape = shape
        self.rng = rng
        self.taken = []

    def ground(self, x, y):
        return self.shape.height(x, y)

    def free(self, x, y, r, edge_margin=1.5):
        if not self.shape.inside(x, y, r + edge_margin):
            return False
        return all(math.hypot(x - tx, y - ty) >= r + tr for (tx, ty, tr) in self.taken)

    def take(self, x, y, r):
        self.taken.append((x, y, r))
        return (x, y, self.ground(x, y))

    def reserve_path(self, points, width):
        """Keep a corridor clear, e.g. the walk from a door to the mail pier."""
        for a, b in zip(points[:-1], points[1:]):
            steps = max(1, int((Vector(b) - Vector(a)).length / width))
            for k in range(steps + 1):
                p = Vector(a).lerp(Vector(b), k / steps)
                self.taken.append((p.x, p.y, width * 0.5))

    def scatter(self, count, r, tries=60, min_r=0.0, max_r=None):
        out = []
        for _ in range(count):
            for _ in range(tries):
                a = self.rng.uniform(0, math.tau)
                lim = self.shape.edge_radius(a) if max_r is None else max_r
                d = self.rng.uniform(min_r, lim)
                x, y = math.cos(a) * d, math.sin(a) * d
                if self.free(x, y, r):
                    out.append(self.take(x, y, r))
                    break
        return out


def stepping_stones(m, points, rng, spacing=1.4, z_of=None):
    for a, b in zip(points[:-1], points[1:]):
        a, b = Vector(a), Vector(b)
        steps = max(1, int((b - a).length / spacing))
        for k in range(steps):
            p = a.lerp(b, (k + 0.5) / steps)
            p += Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), 0))
            z = z_of(p.x, p.y) if z_of else p.z
            m.cylinder(rng.uniform(0.45, 0.6), 0.14, "path", loc=(p.x, p.y, z - 0.06),
                       segments=6, phase=rng.uniform(0, 1))
