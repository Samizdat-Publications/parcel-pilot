"""Geometry kit: a thin, deterministic layer over bmesh.

A `Mesh` accumulates primitives, each painted with a palette material, and is
turned into a Blender object at the end. Conventions for the whole project:

* Meters. Blender Z is up. Models face +Y (exports to Godot -Z, i.e. forward).
* Every primitive is a closed shell, so face normals can always be recalculated
  safely when the object is finalized.
* Every primitive takes `loc`/`rot` plus an optional parent matrix `m`, so
  sub-assemblies (a roof on a house on an island) compose by matrix product.
* With `base=True` the `loc` is the bottom center, so things sit on the ground.
* All randomness comes from a `random.Random(seed)` passed in by the caller.
"""

import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector, noise

from . import palette

IDENTITY = Matrix.Identity(4)


def trs(loc=(0.0, 0.0, 0.0), rot=None, scale=(1.0, 1.0, 1.0)):
    """Build a 4x4 matrix from translation, XYZ euler rotation (radians), scale."""
    if rot is None:
        rot_m = Matrix.Identity(4)
    elif isinstance(rot, Matrix):
        rot_m = rot.to_4x4()
    else:
        rot_m = Euler(rot, "XYZ").to_matrix().to_4x4()
    return Matrix.Translation(Vector(loc)) @ rot_m @ Matrix.Diagonal((*scale, 1.0))


def ring_points(radius, segments, z=0.0, phase=0.0, radii=None):
    """Points on a horizontal circle; `radii` optionally varies radius per point."""
    pts = []
    for i in range(segments):
        a = phase + 2.0 * math.pi * i / segments
        r = radii[i] if radii is not None else radius
        pts.append(Vector((math.cos(a) * r, math.sin(a) * r, z)))
    return pts


class Mesh:
    """Accumulates painted geometry, then becomes one Blender object."""

    def __init__(self):
        self.bm = bmesh.new()
        self.slots = []

    # ----------------------------------------------------------- materials
    def slot(self, mat_name):
        if mat_name not in self.slots:
            palette.material(mat_name)  # fail fast on typos
            self.slots.append(mat_name)
        return self.slots.index(mat_name)

    def paint(self, faces, mat):
        idx = self.slot(mat)
        for f in faces:
            f.material_index = idx
        return faces

    @staticmethod
    def faces_of(verts):
        faces = set()
        for v in verts:
            faces.update(v.link_faces)
        return list(faces)

    @staticmethod
    def verts_of(faces):
        verts = set()
        for f in faces:
            verts.update(f.verts)
        return list(verts)

    @staticmethod
    def _base(m, loc, rot):
        return (m if m is not None else IDENTITY) @ trs(loc, rot)

    # ---------------------------------------------------------- primitives
    def box(self, size, mat, loc=(0, 0, 0), rot=None, base=False, m=None):
        """Box of `size` (x, y, z). `base=True` puts `loc` at the bottom center."""
        offset = Matrix.Translation((0, 0, size[2] * 0.5)) if base else IDENTITY
        mm = self._base(m, loc, rot) @ offset @ Matrix.Diagonal((*size, 1.0))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=mm)
        return self.paint(self.faces_of(res["verts"]), mat)

    def cylinder(self, radius, height, mat, loc=(0, 0, 0), rot=None, segments=12,
                 radius_top=None, base=True, phase=0.0, m=None):
        """Cylinder (or frustum when `radius_top` differs) along local Z."""
        r2 = radius if radius_top is None else radius_top
        offset = Matrix.Translation((0, 0, height * 0.5)) if base else IDENTITY
        mm = self._base(m, loc, rot) @ offset @ Matrix.Rotation(phase, 4, "Z")
        res = bmesh.ops.create_cone(
            self.bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=radius, radius2=r2, depth=height, matrix=mm,
        )
        return self.paint(self.faces_of(res["verts"]), mat)

    def cone(self, radius, height, mat, loc=(0, 0, 0), rot=None, segments=10, base=True,
             phase=0.0, m=None):
        return self.cylinder(radius, height, mat, loc, rot, segments, radius_top=0.0,
                             base=base, phase=phase, m=m)

    def ico(self, radius, mat, loc=(0, 0, 0), rot=None, subdiv=1, scale=(1, 1, 1), m=None):
        mm = self._base(m, loc, rot) @ Matrix.Diagonal((*scale, 1.0))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=radius, matrix=mm)
        return self.paint(self.faces_of(res["verts"]), mat)

    def sphere(self, radius, mat, loc=(0, 0, 0), rot=None, u=12, v=8, scale=(1, 1, 1),
               m=None):
        mm = self._base(m, loc, rot) @ Matrix.Diagonal((*scale, 1.0))
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=u, v_segments=v, radius=radius,
                                        matrix=mm)
        return self.paint(self.faces_of(res["verts"]), mat)

    def loft(self, rings, mats, loc=(0, 0, 0), rot=None, m=None):
        """Skin consecutive closed rings with an equal point count, capping both ends.

        `mats` is one material or a list with one entry per band (len(rings) - 1).
        A ring may be a single point to close the shape to a tip.
        """
        if isinstance(mats, str):
            mats = [mats] * (len(rings) - 1)
        mm = self._base(m, loc, rot)
        bm = self.bm
        vrings = [[bm.verts.new(mm @ Vector(p)) for p in ring] for ring in rings]
        return self._skin(vrings, mats)

    def lathe(self, profile, segments, mats, loc=(0, 0, 0), rot=None, phase=0.0,
              jitter=0.0, rng=None, m=None):
        """Surface of revolution around local Z.

        `profile` is [(radius, z), ...] from bottom to top. A radius of 0 at
        either end collapses to a point (a tip), otherwise that end is capped.
        `jitter` (meters) nudges ring vertices for an organic, hand-cut look.
        """
        if isinstance(mats, str):
            mats = [mats] * (len(profile) - 1)
        mm = self._base(m, loc, rot)
        bm = self.bm
        vrings = []
        for (r, z) in profile:
            if r <= 1e-6:
                vrings.append([bm.verts.new(mm @ Vector((0, 0, z)))])
                continue
            ring = []
            for i in range(segments):
                a = phase + 2.0 * math.pi * i / segments
                p = Vector((math.cos(a) * r, math.sin(a) * r, z))
                if jitter and rng is not None:
                    p += Vector((rng.uniform(-jitter, jitter), rng.uniform(-jitter, jitter),
                                 rng.uniform(-jitter, jitter) * 0.5))
                ring.append(bm.verts.new(mm @ p))
            vrings.append(ring)
        return self._skin(vrings, mats)

    def _skin(self, vrings, mats):
        bm = self.bm
        faces = []
        for band in range(len(vrings) - 1):
            a, b = vrings[band], vrings[band + 1]
            band_faces = []
            if len(a) == 1 and len(b) > 1:
                n = len(b)
                band_faces = [bm.faces.new((a[0], b[(i + 1) % n], b[i])) for i in range(n)]
            elif len(b) == 1 and len(a) > 1:
                n = len(a)
                band_faces = [bm.faces.new((a[i], a[(i + 1) % n], b[0])) for i in range(n)]
            elif len(a) > 1:
                n = len(a)
                band_faces = [bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
                              for i in range(n)]
            self.paint(band_faces, mats[band])
            faces += band_faces
        if len(vrings[0]) > 2:
            faces += self.paint([bm.faces.new(list(reversed(vrings[0])))], mats[0])
        if len(vrings[-1]) > 2:
            faces += self.paint([bm.faces.new(vrings[-1])], mats[-1])
        return faces

    def prism(self, outline, z0, z1, mat, top_mat=None, bottom_mat=None, loc=(0, 0, 0),
              rot=None, m=None):
        """Extrude a counter-clockwise 2D outline [(x, y), ...] from z0 to z1 (local Z)."""
        mm = self._base(m, loc, rot)
        bm = self.bm
        bottom = [bm.verts.new(mm @ Vector((x, y, z0))) for (x, y) in outline]
        top = [bm.verts.new(mm @ Vector((x, y, z1))) for (x, y) in outline]
        n = len(outline)
        sides = [bm.faces.new((bottom[i], bottom[(i + 1) % n], top[(i + 1) % n], top[i]))
                 for i in range(n)]
        self.paint(sides, mat)
        f_top = bm.faces.new(top)
        f_bot = bm.faces.new(list(reversed(bottom)))
        self.paint([f_top], top_mat or mat)
        self.paint([f_bot], bottom_mat or mat)
        return sides + [f_top, f_bot]

    def torus(self, major, minor, mat, loc=(0, 0, 0), rot=None, major_seg=24, minor_seg=8,
              m=None):
        """Torus lying in the local XY plane (its axis is local Z)."""
        mm = self._base(m, loc, rot)
        rings = []
        for i in range(major_seg):
            a = 2.0 * math.pi * i / major_seg
            center = Vector((math.cos(a) * major, math.sin(a) * major, 0.0))
            outward = Vector((math.cos(a), math.sin(a), 0.0))
            ring = []
            for j in range(minor_seg):
                b = 2.0 * math.pi * j / minor_seg
                p = center + outward * (math.cos(b) * minor) + Vector((0, 0, math.sin(b) * minor))
                ring.append(self.bm.verts.new(mm @ p))
            rings.append(ring)
        faces = []
        for i in range(major_seg):
            a, b = rings[i], rings[(i + 1) % major_seg]
            for j in range(minor_seg):
                k = (j + 1) % minor_seg
                faces.append(self.bm.faces.new((a[j], b[j], b[k], a[k])))
        return self.paint(faces, mat)

    def gable_roof(self, width, depth, height, mat, loc=(0, 0, 0), rot=None, overhang=0.3,
                   thickness=0.2, gable_mat=None, m=None):
        """Pitched roof: two slabs meeting at a ridge along local Y, plus the gable wall.

        `width` spans X (the slope direction), `depth` spans Y (the ridge).
        `loc` is the center of the wall top the roof sits on.
        """
        mm = self._base(m, loc, rot)
        half = width * 0.5
        theta = math.atan2(height, half)
        slope_len = (half + overhang) / math.cos(theta) + thickness
        faces = []
        for side in (-1, 1):
            d = Vector((side * math.cos(theta), 0.0, -math.sin(theta)))
            n = Vector((side * math.sin(theta), 0.0, math.cos(theta)))
            center = (Vector((0.0, 0.0, height)) + d * (slope_len * 0.5 - thickness)
                      + n * (thickness * 0.5))
            faces += self.box((slope_len, depth + 2 * overhang, thickness), mat,
                              loc=center, rot=(0.0, side * theta, 0.0), m=mm)
        # Triangular gable wall under the slabs (outline in XZ, extruded along Y).
        tri = [(-half, 0.0), (half, 0.0), (0.0, height)]
        faces += self.prism(tri, -depth * 0.5, depth * 0.5, gable_mat or mat,
                            rot=(math.pi * 0.5, 0.0, 0.0), m=mm)
        return faces

    # ------------------------------------------------------------ deformers
    def jitter(self, faces_or_verts, amount, rng, z_scale=1.0):
        verts = faces_or_verts
        if verts and isinstance(verts[0], bmesh.types.BMFace):
            verts = self.verts_of(verts)
        for v in verts:
            v.co += Vector((rng.uniform(-amount, amount), rng.uniform(-amount, amount),
                            rng.uniform(-amount, amount) * z_scale))

    def displace(self, verts, fn):
        for v in verts:
            v.co = fn(v.co.copy())

    def transform(self, faces, matrix):
        bmesh.ops.transform(self.bm, matrix=matrix, verts=self.verts_of(faces))

    # --------------------------------------------------------------- output
    def is_empty(self):
        return len(self.bm.faces) == 0

    def to_object(self, name, parent=None, loc=(0, 0, 0), rot=None, smooth=False):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        for s in self.slots:
            me.materials.append(palette.material(s))
        if smooth:
            me.shade_smooth()
        else:
            me.shade_flat()
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = Vector(loc)
        if rot is not None:
            obj.rotation_euler = Euler(rot, "XYZ")
        if parent is not None:
            obj.parent = parent
        return obj


def fbm(p, seed=0, octaves=3, lacunarity=2.0, gain=0.5):
    """Deterministic fractal noise, roughly in [-1, 1] (Blender's Perlin)."""
    noise.seed_set(seed)
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * noise.noise(Vector(p) * freq, noise_basis="PERLIN_ORIGINAL")
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm
