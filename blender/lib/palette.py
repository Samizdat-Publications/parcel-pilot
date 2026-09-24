"""The one color palette every asset draws from.

Materials are created lazily by name and shared across all objects in the
current build, so a model never invents its own colors. Tweak a hex value
here, rebuild, and the whole world shifts together.

Entry format: name -> (sRGB hex, roughness, metallic, emission strength, flags)
flags: "2s" = double sided (thin geometry such as flags, sails, leaves)
"""

import bpy

PALETTE = {
    # Greens
    "grass":        ("#8CBF4E", 0.95, 0.0, 0.0, ""),
    "grass_dark":   ("#679E3F", 0.95, 0.0, 0.0, ""),
    "grass_light":  ("#B5D65F", 0.95, 0.0, 0.0, ""),
    "leaf":         ("#4E9A48", 0.90, 0.0, 0.0, ""),
    "leaf_dark":    ("#3A7B3F", 0.90, 0.0, 0.0, ""),
    "leaf_light":   ("#8FC456", 0.90, 0.0, 0.0, ""),
    "leaf_autumn":  ("#E3A33B", 0.90, 0.0, 0.0, ""),
    "pine":         ("#2F6B4F", 0.90, 0.0, 0.0, ""),
    "pine_dark":    ("#245843", 0.90, 0.0, 0.0, ""),
    "moss":         ("#6F9140", 0.95, 0.0, 0.0, ""),
    "hedge":        ("#4F8A3C", 0.95, 0.0, 0.0, ""),
    # Earth and rock (the island undersides use these in strata bands)
    "dirt":         ("#9A6B45", 0.95, 0.0, 0.0, ""),
    "dirt_dark":    ("#77502F", 0.95, 0.0, 0.0, ""),
    "path":         ("#D9C3A0", 0.95, 0.0, 0.0, ""),
    "rock":         ("#A99585", 0.90, 0.0, 0.0, ""),
    "rock_light":   ("#CBB9A6", 0.90, 0.0, 0.0, ""),
    "rock_dark":    ("#7C6A62", 0.90, 0.0, 0.0, ""),
    "sandstone":    ("#D9A86C", 0.90, 0.0, 0.0, ""),
    "clay":         ("#C4744D", 0.90, 0.0, 0.0, ""),
    "deep_rock":    ("#5F4C55", 0.90, 0.0, 0.0, ""),
    "crystal":      ("#7FE6E0", 0.20, 0.0, 2.0, ""),
    # Wood
    "wood":         ("#9C6B3F", 0.85, 0.0, 0.0, ""),
    "wood_dark":    ("#6D4527", 0.85, 0.0, 0.0, ""),
    "wood_light":   ("#C99B64", 0.85, 0.0, 0.0, ""),
    "bark":         ("#7A5236", 0.95, 0.0, 0.0, ""),
    "birch":        ("#EDE6D6", 0.90, 0.0, 0.0, ""),
    # Buildings
    "plaster":      ("#F4E7D0", 0.90, 0.0, 0.0, ""),
    "plaster_warm": ("#F1D6B2", 0.90, 0.0, 0.0, ""),
    "plaster_blue": ("#CFE0E8", 0.90, 0.0, 0.0, ""),
    "plaster_pink": ("#F2CFC4", 0.90, 0.0, 0.0, ""),
    "stone":        ("#BEB4A8", 0.90, 0.0, 0.0, ""),
    "stone_dark":   ("#8F877F", 0.90, 0.0, 0.0, ""),
    "brick":        ("#B95D45", 0.90, 0.0, 0.0, ""),
    "roof_red":     ("#D4553F", 0.80, 0.0, 0.0, ""),
    "roof_blue":    ("#4F80A9", 0.80, 0.0, 0.0, ""),
    "roof_teal":    ("#3E9C92", 0.80, 0.0, 0.0, ""),
    "roof_slate":   ("#5C6577", 0.80, 0.0, 0.0, ""),
    "thatch":       ("#D8B66A", 0.95, 0.0, 0.0, ""),
    "door":         ("#7B4A2E", 0.80, 0.0, 0.0, ""),
    "window":       ("#FFD58A", 0.40, 0.0, 1.6, ""),
    "window_dark":  ("#3F4B5E", 0.30, 0.0, 0.0, ""),
    "lamp":         ("#FFE3A3", 0.30, 0.0, 4.0, ""),
    # Accents and props
    "postal_red":   ("#D9412F", 0.60, 0.0, 0.0, ""),
    "cream":        ("#FFF1D8", 0.80, 0.0, 0.0, ""),
    "mustard":      ("#E8B83A", 0.70, 0.0, 0.0, ""),
    "teal":         ("#2F9C95", 0.70, 0.0, 0.0, ""),
    "navy":         ("#2E3E5C", 0.70, 0.0, 0.0, ""),
    "white":        ("#F7F4EE", 0.80, 0.0, 0.0, ""),
    "charcoal":     ("#2C2C33", 0.80, 0.0, 0.0, ""),
    "metal":        ("#A9B1BA", 0.35, 0.8, 0.0, ""),
    "brass":        ("#CDA24C", 0.30, 0.9, 0.0, ""),
    "rope":         ("#CDB48A", 0.95, 0.0, 0.0, ""),
    "kraft":        ("#C99C63", 0.90, 0.0, 0.0, ""),
    "paper":        ("#EFE2C4", 0.90, 0.0, 0.0, ""),
    "cloth_red":    ("#D8483B", 0.90, 0.0, 0.0, "2s"),
    "cloth_cream":  ("#FFF1D8", 0.90, 0.0, 0.0, "2s"),
    "cloth_teal":   ("#2F9C95", 0.90, 0.0, 0.0, "2s"),
    "cloth_mustard":("#E8B83A", 0.90, 0.0, 0.0, "2s"),
    "leather":      ("#8A5A34", 0.80, 0.0, 0.0, ""),
    "skin":         ("#F1C29C", 0.80, 0.0, 0.0, ""),
    "glass":        ("#A9DCE8", 0.10, 0.0, 0.0, ""),
    "water":        ("#63C6DA", 0.10, 0.0, 0.0, ""),
    "hay":          ("#E6C361", 0.95, 0.0, 0.0, ""),
    "pumpkin":      ("#E8872E", 0.80, 0.0, 0.0, ""),
    "apple":        ("#D9402E", 0.60, 0.0, 0.0, ""),
    "flower_pink":  ("#F28FB1", 0.90, 0.0, 0.0, ""),
    "flower_yellow":("#F6D55C", 0.90, 0.0, 0.0, ""),
    "flower_white": ("#FFF8F0", 0.90, 0.0, 0.0, ""),
    "flower_purple":("#A98BD9", 0.90, 0.0, 0.0, ""),
    "cloud":        ("#FFFFFF", 1.00, 0.0, 0.0, ""),
    "cloud_shade":  ("#E3DEF0", 1.00, 0.0, 0.0, ""),
    "storm":        ("#6A6680", 1.00, 0.0, 0.0, ""),
    "storm_dark":   ("#4B4760", 1.00, 0.0, 0.0, ""),
    "gold":         ("#FFC93D", 0.25, 0.9, 0.6, ""),
    "boost":        ("#5FE0F0", 0.30, 0.0, 2.5, ""),
    "beacon":       ("#FFB547", 0.30, 0.0, 3.0, ""),
    "bolt":         ("#FFF4B8", 0.20, 0.0, 8.0, ""),
    "nav_red":      ("#FF4A3D", 0.30, 0.0, 3.0, ""),
    "nav_green":    ("#46D86A", 0.30, 0.0, 3.0, ""),
    # Greybox blockout colors (milestone 1 only)
    "grey_light":   ("#D8D8D8", 0.90, 0.0, 0.0, ""),
    "grey_mid":     ("#A8A8A8", 0.90, 0.0, 0.0, ""),
    "grey_dark":    ("#707070", 0.90, 0.0, 0.0, ""),
    "grey_accent":  ("#E07A5F", 0.90, 0.0, 0.0, ""),
}


def hex_to_linear(hex_color):
    """sRGB hex string to a linear RGBA tuple (what Principled BSDF expects)."""
    h = hex_color.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (lin(srgb[0]), lin(srgb[1]), lin(srgb[2]), 1.0)


def _find_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def material(name):
    """Return the shared material for a palette entry, creating it on first use."""
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    if name not in PALETTE:
        raise KeyError(f"'{name}' is not in the palette (blender/lib/palette.py)")
    hex_color, roughness, metallic, emission, flags = PALETTE[name]
    color = hex_to_linear(hex_color)

    mat = bpy.data.materials.new(name)
    tree = mat.node_tree
    bsdf = _find_bsdf(mat)
    if bsdf is None:
        tree.nodes.clear()
        out = tree.nodes.new("ShaderNodeOutputMaterial")
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emission

    # Viewport/Workbench color so preview renders match the export.
    mat.diffuse_color = color
    mat.roughness = roughness
    mat.metallic = metallic
    # glTF doubleSided follows backface culling: closed meshes cull, thin ones do not.
    mat.use_backface_culling = "2s" not in flags
    return mat
