class ColorSpace:
    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def Sycc() -> "ColorSpace":
        return ColorSpace(name="sYCC")

    @staticmethod
    def Smpte170m() -> "ColorSpace":
        return ColorSpace(name="SMPTE170M")

    @staticmethod
    def Rec709() -> "ColorSpace":
        return ColorSpace(name="Rec709")

    def __repr__(self) -> str:
        return f"<libcamera.ColorSpace '{self.name}'>"
