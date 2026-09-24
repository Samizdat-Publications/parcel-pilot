"""Asset registry: asset scripts register build functions with @asset("name")."""

ASSETS = {}


def asset(name, preview=True, icon=None):
    """Register `fn` as the builder for game/assets/models/<name>.glb.

    The function builds objects into the (already reset) scene. Whatever ends
    up at the scene root is exported. `icon=(azimuth, elevation)` also renders a
    transparent UI icon to game/assets/icons/<name>.png from that angle.
    """
    def wrap(fn):
        if name in ASSETS:
            raise ValueError(f"asset '{name}' registered twice")
        ASSETS[name] = {"build": fn, "preview": preview, "icon": icon, "module": fn.__module__}
        return fn
    return wrap
