"""Asset registry: asset scripts register build functions with @asset("name")."""

ASSETS = {}


def asset(name, preview=True):
    """Register `fn` as the builder for game/assets/models/<name>.glb.

    The function builds objects into the (already reset) scene. Whatever ends
    up at the scene root is exported.
    """
    def wrap(fn):
        if name in ASSETS:
            raise ValueError(f"asset '{name}' registered twice")
        ASSETS[name] = {"build": fn, "preview": preview, "module": fn.__module__}
        return fn
    return wrap
