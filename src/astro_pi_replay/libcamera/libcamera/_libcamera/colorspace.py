"""
Derived from include/libcamera/color_space.h and
src/libcamera/color_space.cpp
"""
import enum
from typing import Any

class Primaries(enum.Enum):
    Raw = 0
    Smpte170m = 1
    Rec709 = 2
    Rec2020 = 3

class TransferFunction(enum.Enum):
    Linear = 0
    Srgb = 1
    Rec709 = 2

class YcbcrEncoding(enum.Enum):
    Null = 0,
    Rec601 = 1
    Rec709 = 2
    Rec2020 = 3

class Range(enum.Enum):
    Full = 0
    Limited = 1

class ColorSpaceMeta(type):

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Enables (limited) multi-dispatch for ColorSpace:
            ColorSpace(ColorSpace.Sycc())
            ColorSpace(ColorSpace.Primaries.Raw,
                       ColorSpace.TransferFunction.Srgb,
                       ColorSpace.YcbcrEncoding.Null,
                       ColorSpace.Range.Full)
        """
        if args and isinstance(args[0], ColorSpace):
            return args[0]
        return super().__call__(*args, **kwds)


class ColorSpace(metaclass=ColorSpaceMeta):
    Primaries = Primaries
    TransferFunction = TransferFunction
    YcbcrEncoding = YcbcrEncoding
    Range = Range

    @staticmethod
    def Raw() -> "ColorSpace":
        return ColorSpace(
                Primaries.Raw,
                TransferFunction.Linear,
                YcbcrEncoding.Null,
                Range.Full
        )

    @staticmethod
    def Srgb() -> "ColorSpace":
        return ColorSpace(
            Primaries.Rec709,
            TransferFunction.Srgb,
            YcbcrEncoding.Null,
            Range.Full
        )

    @staticmethod
    def Sycc() -> "ColorSpace":
        return ColorSpace(
            Primaries.Rec709,
            TransferFunction.Srgb,
            YcbcrEncoding.Rec601,
            Range.Full
        )

    @staticmethod
    def Smpte170m() -> "ColorSpace":
        return ColorSpace(
            Primaries.Smpte170m,
            TransferFunction.Rec709,
            YcbcrEncoding.Rec601,
            Range.Limited
        )

    @staticmethod
    def Rec709() -> "ColorSpace":
        return ColorSpace(
            Primaries.Rec709,
            TransferFunction.Rec709,
            YcbcrEncoding.Rec709,
            Range.Limited
        )

    @staticmethod
    def Rec2020() -> "ColorSpace" :
        return ColorSpace(
            Primaries.Rec2020,
            TransferFunction.Rec709,
            YcbcrEncoding.Rec2020,
            Range.Limited
        )

    def __init__(self, p: Primaries, t: TransferFunction,
                 e: YcbcrEncoding, r: Range):
        self.primaries: Primaries = p
        self.transferFunction: TransferFunction = t
        self.ycbcrEncoding: YcbcrEncoding = e
        self.range: Range = r

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, "ColorSpace"):
            return False
        return self.primaries == other.primaries and \
                self.transferFunction == other.transferFunction and \
                self.ycbcrEncoding == other.ycbcrEncoding and \
                self.range == other.range

    def __hash__(self) -> int:
        return super().__hash__()

#    def __repr__(self) -> str:
#        return f"<libcamera.ColorSpace '{self.name}'>"
