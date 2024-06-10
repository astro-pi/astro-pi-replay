def maybe_error():
    # Only throw error if configured to
    if True:
        raise RuntimeError("Not implemented")

class Transform:
    """
    Derived from:
        * src/py/py_transform.cpp
        * src/libcamera/transform.cpp
        * include/libcamera/transform.h
    """
    def __init__(self, 
        rotation: int = 0,
        vflip: bool = False,
        hflip: bool = False,
        transpose: bool = False):
        self.rotation: int = rotation
        self.vflip: bool = vflip
        self.hflip: bool = hflip
        self.transpose: bool = transpose

    def __repr__(self):
        if not self.vflip and not self.hflip:
            sub = "identity"
        elif self.vflip and self.hflip:
            sub = "hvflip"
        elif self.hflip:
            sub = "hflip"
        elif self.vflip:
            sub = "vflip"
        else:
            sub = ""

        classname: str = "libcamera.Transform"
        if len(sub) > 0:
            return f"<{classname} '{sub}'>"
        return f"<{classname} >"

    def compose(self):
        maybe_error()

    def invert(self):
        maybe_error()

    def inverse(self):
        maybe_error()
