"""
Based on:
 * src/libcamera/pixel_format.cpp
 * include/libcamera/formats.h
 * include/libcamera/internal/formats.h
 * include/libcamera/formats.h
 * src/libcamera/formats.cpp
"""

import dataclasses
import enum
from typing import Any, overload


def __fourcc(a, b, c, d):
    return (ord(a) << 0) | (ord(b) << 8) | (ord(c) << 16) | (ord(d) << 24)


def __mod(vendor, mod):
    return (vendor << 56) | (mod << 0)


pixelFormatInfo: dict["PixelFormat", "PixelFormatInfo"] = {}


class PixelFormatSingleton(type):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Ensures the following initialisations are valid:
            PixelFormat(123,456)
            PixelFormat("BGR888")
        """
        if args and type(args[0]) == str:
            # lookup in info map
            name: str = args[0]
            for pfi in pixelFormatInfo.values():
                if pfi.name == name:
                    return pfi.format
            raise RuntimeError(f"Format {name} not found")
        return super().__call__(*args, **kwds)


class PixelFormat(metaclass=PixelFormatSingleton):
    def __init__(self, fourcc: int, modifier: int) -> None:
        self.fourcc: int = fourcc
        self.modifier: int = modifier

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PixelFormat):
            return False
        return self.fourcc == other.fourcc and self.modifier == other.modifier

    def __hash__(self) -> int:
        return hash((self.fourcc, self.modifier))

    def __str__(self) -> str:
        info = pixelFormatInfo.get(self)
        if not info:
            raise RuntimeError(f"Could not get name")
        return info.name


@dataclasses.dataclass
class PixelFormatInfo:
    class ColourEncoding(enum.Enum):
        RGB = 0
        YUV = 1
        RAW = 2

    @dataclasses.dataclass
    class Plane:
        bytesPerGroup: int
        verticalSubSampling: int

    name: str
    format: PixelFormat
    bitsPerPixel: int
    colourEncoding: ColourEncoding
    packed: bool
    pixelsPerGroup: int
    planes: list[Plane]


R8 = PixelFormat(__fourcc("R", "8", " ", " "), __mod(0, 0))
R10 = PixelFormat(__fourcc("R", "1", "0", " "), __mod(0, 0))
R12 = PixelFormat(__fourcc("R", "1", "2", " "), __mod(0, 0))
R16 = PixelFormat(__fourcc("R", "1", "6", " "), __mod(0, 0))
RGB565 = PixelFormat(__fourcc("R", "G", "1", "6"), __mod(0, 0))
RGB565_BE = PixelFormat(__fourcc("R", "G", "1", "6"), __mod(0, 0))
RGB888 = PixelFormat(__fourcc("R", "G", "2", "4"), __mod(0, 0))
BGR888 = PixelFormat(__fourcc("B", "G", "2", "4"), __mod(0, 0))
XRGB8888 = PixelFormat(__fourcc("X", "R", "2", "4"), __mod(0, 0))
XBGR8888 = PixelFormat(__fourcc("X", "B", "2", "4"), __mod(0, 0))
RGBX8888 = PixelFormat(__fourcc("R", "X", "2", "4"), __mod(0, 0))
BGRX8888 = PixelFormat(__fourcc("B", "X", "2", "4"), __mod(0, 0))
ARGB8888 = PixelFormat(__fourcc("A", "R", "2", "4"), __mod(0, 0))
ABGR8888 = PixelFormat(__fourcc("A", "B", "2", "4"), __mod(0, 0))
RGBA8888 = PixelFormat(__fourcc("R", "A", "2", "4"), __mod(0, 0))
BGRA8888 = PixelFormat(__fourcc("B", "A", "2", "4"), __mod(0, 0))
RGB161616 = PixelFormat(__fourcc("R", "G", "4", "8"), __mod(0, 0))
BGR161616 = PixelFormat(__fourcc("B", "G", "4", "8"), __mod(0, 0))
YUYV = PixelFormat(__fourcc("Y", "U", "Y", "V"), __mod(0, 0))
YVYU = PixelFormat(__fourcc("Y", "V", "Y", "U"), __mod(0, 0))
UYVY = PixelFormat(__fourcc("U", "Y", "V", "Y"), __mod(0, 0))
VYUY = PixelFormat(__fourcc("V", "Y", "U", "Y"), __mod(0, 0))
AVUY8888 = PixelFormat(__fourcc("A", "V", "U", "Y"), __mod(0, 0))
XVUY8888 = PixelFormat(__fourcc("X", "V", "U", "Y"), __mod(0, 0))
NV12 = PixelFormat(__fourcc("N", "V", "1", "2"), __mod(0, 0))
NV21 = PixelFormat(__fourcc("N", "V", "2", "1"), __mod(0, 0))
NV16 = PixelFormat(__fourcc("N", "V", "1", "6"), __mod(0, 0))
NV61 = PixelFormat(__fourcc("N", "V", "6", "1"), __mod(0, 0))
NV24 = PixelFormat(__fourcc("N", "V", "2", "4"), __mod(0, 0))
NV42 = PixelFormat(__fourcc("N", "V", "4", "2"), __mod(0, 0))
YUV420 = PixelFormat(__fourcc("Y", "U", "1", "2"), __mod(0, 0))
YVU420 = PixelFormat(__fourcc("Y", "V", "1", "2"), __mod(0, 0))
YUV422 = PixelFormat(__fourcc("Y", "U", "1", "6"), __mod(0, 0))
YVU422 = PixelFormat(__fourcc("Y", "V", "1", "6"), __mod(0, 0))
YUV444 = PixelFormat(__fourcc("Y", "U", "2", "4"), __mod(0, 0))
YVU444 = PixelFormat(__fourcc("Y", "V", "2", "4"), __mod(0, 0))
MJPEG = PixelFormat(__fourcc("M", "J", "P", "G"), __mod(0, 0))
SRGGB8 = PixelFormat(__fourcc("R", "G", "G", "B"), __mod(0, 0))
SGRBG8 = PixelFormat(__fourcc("G", "R", "B", "G"), __mod(0, 0))
SGBRG8 = PixelFormat(__fourcc("G", "B", "R", "G"), __mod(0, 0))
SBGGR8 = PixelFormat(__fourcc("B", "A", "8", "1"), __mod(0, 0))
SRGGB10 = PixelFormat(__fourcc("R", "G", "1", "0"), __mod(0, 0))
SGRBG10 = PixelFormat(__fourcc("B", "A", "1", "0"), __mod(0, 0))
SGBRG10 = PixelFormat(__fourcc("G", "B", "1", "0"), __mod(0, 0))
SBGGR10 = PixelFormat(__fourcc("B", "G", "1", "0"), __mod(0, 0))
SRGGB12 = PixelFormat(__fourcc("R", "G", "1", "2"), __mod(0, 0))
SGRBG12 = PixelFormat(__fourcc("B", "A", "1", "2"), __mod(0, 0))
SGBRG12 = PixelFormat(__fourcc("G", "B", "1", "2"), __mod(0, 0))
SBGGR12 = PixelFormat(__fourcc("B", "G", "1", "2"), __mod(0, 0))
SRGGB14 = PixelFormat(__fourcc("R", "G", "1", "4"), __mod(0, 0))
SGRBG14 = PixelFormat(__fourcc("B", "A", "1", "4"), __mod(0, 0))
SGBRG14 = PixelFormat(__fourcc("G", "B", "1", "4"), __mod(0, 0))
SBGGR14 = PixelFormat(__fourcc("B", "G", "1", "4"), __mod(0, 0))
SRGGB16 = PixelFormat(__fourcc("R", "G", "B", "6"), __mod(0, 0))
SGRBG16 = PixelFormat(__fourcc("G", "R", "1", "6"), __mod(0, 0))
SGBRG16 = PixelFormat(__fourcc("G", "B", "1", "6"), __mod(0, 0))
SBGGR16 = PixelFormat(__fourcc("B", "Y", "R", "2"), __mod(0, 0))
R10_CSI2P = PixelFormat(__fourcc("R", "1", "0", " "), __mod(11, 1))
SRGGB10_CSI2P = PixelFormat(__fourcc("R", "G", "1", "0"), __mod(11, 1))
SGRBG10_CSI2P = PixelFormat(__fourcc("B", "A", "1", "0"), __mod(11, 1))
SGBRG10_CSI2P = PixelFormat(__fourcc("G", "B", "1", "0"), __mod(11, 1))
SBGGR10_CSI2P = PixelFormat(__fourcc("B", "G", "1", "0"), __mod(11, 1))
SRGGB12_CSI2P = PixelFormat(__fourcc("R", "G", "1", "2"), __mod(11, 1))
SGRBG12_CSI2P = PixelFormat(__fourcc("B", "A", "1", "2"), __mod(11, 1))
SGBRG12_CSI2P = PixelFormat(__fourcc("G", "B", "1", "2"), __mod(11, 1))
SBGGR12_CSI2P = PixelFormat(__fourcc("B", "G", "1", "2"), __mod(11, 1))
SRGGB14_CSI2P = PixelFormat(__fourcc("R", "G", "1", "4"), __mod(11, 1))
SGRBG14_CSI2P = PixelFormat(__fourcc("B", "A", "1", "4"), __mod(11, 1))
SGBRG14_CSI2P = PixelFormat(__fourcc("G", "B", "1", "4"), __mod(11, 1))
SBGGR14_CSI2P = PixelFormat(__fourcc("B", "G", "1", "4"), __mod(11, 1))
SRGGB10_IPU3 = PixelFormat(__fourcc("R", "G", "1", "0"), __mod(1, 13))
SGRBG10_IPU3 = PixelFormat(__fourcc("B", "A", "1", "0"), __mod(1, 13))
SGBRG10_IPU3 = PixelFormat(__fourcc("G", "B", "1", "0"), __mod(1, 13))
SBGGR10_IPU3 = PixelFormat(__fourcc("B", "G", "1", "0"), __mod(1, 13))
RGGB_PISP_COMP1 = PixelFormat(__fourcc("R", "G", "B", "6"), __mod(12, 1))
GRBG_PISP_COMP1 = PixelFormat(__fourcc("G", "R", "1", "6"), __mod(12, 1))
GBRG_PISP_COMP1 = PixelFormat(__fourcc("G", "B", "1", "6"), __mod(12, 1))
BGGR_PISP_COMP1 = PixelFormat(__fourcc("B", "Y", "R", "2"), __mod(12, 1))
MONO_PISP_COMP1 = PixelFormat(__fourcc("R", "1", "6", " "), __mod(12, 1))


pixelFormatInfo = {
    # RGB formats.
    RGB565: PixelFormatInfo(
        name="RGB565",
        format=RGB565,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGB565), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGB565_BE: PixelFormatInfo(
        name="RGB565_BE",
        format=RGB565_BE,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGB565X), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    BGR888: PixelFormatInfo(
        name="BGR888",
        format=BGR888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGB24), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGB888: PixelFormatInfo(
        name="RGB888",
        format=RGB888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_BGR24), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    XRGB8888: PixelFormatInfo(
        name="XRGB8888",
        format=XRGB8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_XBGR32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    XBGR8888: PixelFormatInfo(
        name="XBGR8888",
        format=XBGR8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGBX32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGBX8888: PixelFormatInfo(
        name="RGBX8888",
        format=RGBX8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_BGRX32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    BGRX8888: PixelFormatInfo(
        name="BGRX8888",
        format=BGRX8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_XRGB32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    ABGR8888: PixelFormatInfo(
        name="ABGR8888",
        format=ABGR8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGBA32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    ARGB8888: PixelFormatInfo(
        name="ARGB8888",
        format=ARGB8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_ABGR32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    BGRA8888: PixelFormatInfo(
        name="BGRA8888",
        format=BGRA8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_ARGB32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGBA8888: PixelFormatInfo(
        name="RGBA8888",
        format=RGBA8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_BGRA32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    BGR161616: PixelFormatInfo(
        name="BGR161616",
        format=BGR161616,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_RGB48), },
        bitsPerPixel=48,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGB161616: PixelFormatInfo(
        name="RGB161616",
        format=RGB161616,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_BGR48), },
        bitsPerPixel=48,
        colourEncoding=PixelFormatInfo.ColourEncoding.RGB,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    # YUV packed formats.
    YUYV: PixelFormatInfo(
        name="YUYV",
        format=YUYV,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YUYV), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    YVYU: PixelFormatInfo(
        name="YVYU",
        format=YVYU,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YVYU), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    UYVY: PixelFormatInfo(
        name="UYVY",
        format=UYVY,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_UYVY), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    VYUY: PixelFormatInfo(
        name="VYUY",
        format=VYUY,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_VYUY), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    AVUY8888: PixelFormatInfo(
        name="AVUY8888",
        format=AVUY8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YUVA32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    XVUY8888: PixelFormatInfo(
        name="XVUY8888",
        format=XVUY8888,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YUVX32), },
        bitsPerPixel=32,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    # YUV planar formats.
    NV12: PixelFormatInfo(
        name="NV12",
        format=NV12,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV12),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV12M),
        # },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(2, 2),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    NV21: PixelFormatInfo(
        name="NV21",
        format=NV21,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV21),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV21M),
        # },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(2, 2),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    NV16: PixelFormatInfo(
        name="NV16",
        format=NV16,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV16),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV16M),
        # },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    NV61: PixelFormatInfo(
        name="NV61",
        format=NV61,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV61),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_NV61M),
        # },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    NV24: PixelFormatInfo(
        name="NV24",
        format=NV24,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_NV24), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    NV42: PixelFormatInfo(
        name="NV42",
        format=NV42,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_NV42), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    YUV420: PixelFormatInfo(
        name="YUV420",
        format=YUV420,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YUV420),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YUV420M),
        # },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(1, 2),
            PixelFormatInfo.Plane(1, 2),
        ],
    ),
    YVU420: PixelFormatInfo(
        name="YVU420",
        format=YVU420,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YVU420),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YVU420M),
        # },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(1, 2),
            PixelFormatInfo.Plane(1, 2),
        ],
    ),
    YUV422: PixelFormatInfo(
        name="YUV422",
        format=YUV422,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YUV422P),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_YUV422M),
        # },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
        ],
    ),
    YVU422: PixelFormatInfo(
        name="YVU422",
        format=YVU422,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YVU422M), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
        ],
    ),
    YUV444: PixelFormatInfo(
        name="YUV444",
        format=YUV444,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YUV444M), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
        ],
    ),
    YVU444: PixelFormatInfo(
        name="YVU444",
        format=YVU444,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_YVU444M), },
        bitsPerPixel=24,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(1, 1),
        ],
    ),
    # Greyscale formats.
    R8: PixelFormatInfo(
        name="R8",
        format=R8,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_GREY), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    R10: PixelFormatInfo(
        name="R10",
        format=R10,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_Y10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    R10_CSI2P: PixelFormatInfo(
        name="R10_CSI2P",
        format=R10_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_Y10P), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(5, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    R12: PixelFormatInfo(
        name="R12",
        format=R12,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_Y12), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    R16: PixelFormatInfo(
        name="R16",
        format=R16,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_Y16), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    MONO_PISP_COMP1: PixelFormatInfo(
        name="MONO_PISP_COMP1",
        format=MONO_PISP_COMP1,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_PISP_COMP1_MONO), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=True,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    # Bayer formats.
    SBGGR8: PixelFormatInfo(
        name="SBGGR8",
        format=SBGGR8,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR8), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG8: PixelFormatInfo(
        name="SGBRG8",
        format=SGBRG8,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG8), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG8: PixelFormatInfo(
        name="SGRBG8",
        format=SGRBG8,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG8), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB8: PixelFormatInfo(
        name="SRGGB8",
        format=SRGGB8,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB8), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR10: PixelFormatInfo(
        name="SBGGR10",
        format=SBGGR10,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG10: PixelFormatInfo(
        name="SGBRG10",
        format=SGBRG10,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG10: PixelFormatInfo(
        name="SGRBG10",
        format=SGRBG10,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB10: PixelFormatInfo(
        name="SRGGB10",
        format=SRGGB10,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR10_CSI2P: PixelFormatInfo(
        name="SBGGR10_CSI2P",
        format=SBGGR10_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR10P), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(5, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG10_CSI2P: PixelFormatInfo(
        name="SGBRG10_CSI2P",
        format=SGBRG10_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG10P), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(5, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG10_CSI2P: PixelFormatInfo(
        name="SGRBG10_CSI2P",
        format=SGRBG10_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG10P), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(5, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB10_CSI2P: PixelFormatInfo(
        name="SRGGB10_CSI2P",
        format=SRGGB10_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB10P), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(5, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR12: PixelFormatInfo(
        name="SBGGR12",
        format=SBGGR12,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR12), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG12: PixelFormatInfo(
        name="SGBRG12",
        format=SGBRG12,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG12), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG12: PixelFormatInfo(
        name="SGRBG12",
        format=SGRBG12,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG12), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB12: PixelFormatInfo(
        name="SRGGB12",
        format=SRGGB12,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB12), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR12_CSI2P: PixelFormatInfo(
        name="SBGGR12_CSI2P",
        format=SBGGR12_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR12P), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG12_CSI2P: PixelFormatInfo(
        name="SGBRG12_CSI2P",
        format=SGBRG12_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG12P), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG12_CSI2P: PixelFormatInfo(
        name="SGRBG12_CSI2P",
        format=SGRBG12_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG12P), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB12_CSI2P: PixelFormatInfo(
        name="SRGGB12_CSI2P",
        format=SRGGB12_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB12P), },
        bitsPerPixel=12,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(3, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR14: PixelFormatInfo(
        name="SBGGR14",
        format=SBGGR14,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR14), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG14: PixelFormatInfo(
        name="SGBRG14",
        format=SGBRG14,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG14), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG14: PixelFormatInfo(
        name="SGRBG14",
        format=SGRBG14,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG14), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB14: PixelFormatInfo(
        name="SRGGB14",
        format=SRGGB14,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB14), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR14_CSI2P: PixelFormatInfo(
        name="SBGGR14_CSI2P",
        format=SBGGR14_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR14P), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(7, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG14_CSI2P: PixelFormatInfo(
        name="SGBRG14_CSI2P",
        format=SGBRG14_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG14P), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(7, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG14_CSI2P: PixelFormatInfo(
        name="SGRBG14_CSI2P",
        format=SGRBG14_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG14P), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(7, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB14_CSI2P: PixelFormatInfo(
        name="SRGGB14_CSI2P",
        format=SRGGB14_CSI2P,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB14P), },
        bitsPerPixel=14,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=4,
        planes=[
            PixelFormatInfo.Plane(7, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR16: PixelFormatInfo(
        name="SBGGR16",
        format=SBGGR16,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SBGGR16), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG16: PixelFormatInfo(
        name="SGBRG16",
        format=SGBRG16,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGBRG16), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG16: PixelFormatInfo(
        name="SGRBG16",
        format=SGRBG16,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SGRBG16), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB16: PixelFormatInfo(
        name="SRGGB16",
        format=SRGGB16,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_SRGGB16), },
        bitsPerPixel=16,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=False,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(4, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SBGGR10_IPU3: PixelFormatInfo(
        name="SBGGR10_IPU3",
        format=SBGGR10_IPU3,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_IPU3_SBGGR10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=25,
        planes=[
            PixelFormatInfo.Plane(32, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGBRG10_IPU3: PixelFormatInfo(
        name="SGBRG10_IPU3",
        format=SGBRG10_IPU3,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_IPU3_SGBRG10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=25,
        planes=[
            PixelFormatInfo.Plane(32, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SGRBG10_IPU3: PixelFormatInfo(
        name="SGRBG10_IPU3",
        format=SGRBG10_IPU3,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_IPU3_SGRBG10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=25,
        planes=[
            PixelFormatInfo.Plane(32, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    SRGGB10_IPU3: PixelFormatInfo(
        name="SRGGB10_IPU3",
        format=SRGGB10_IPU3,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_IPU3_SRGGB10), },
        bitsPerPixel=10,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=25,
        planes=[
            PixelFormatInfo.Plane(32, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    BGGR_PISP_COMP1: PixelFormatInfo(
        name="BGGR_PISP_COMP1",
        format=BGGR_PISP_COMP1,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_PISP_COMP1_BGGR), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    GBRG_PISP_COMP1: PixelFormatInfo(
        name="GBRG_PISP_COMP1",
        format=GBRG_PISP_COMP1,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_PISP_COMP1_GBRG), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    GRBG_PISP_COMP1: PixelFormatInfo(
        name="GRBG_PISP_COMP1",
        format=GRBG_PISP_COMP1,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_PISP_COMP1_GRBG), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    RGGB_PISP_COMP1: PixelFormatInfo(
        name="RGGB_PISP_COMP1",
        format=RGGB_PISP_COMP1,
        # v4l2Formats = { V4L2PixelFormat(V4L2_PIX_FMT_PISP_COMP1_RGGB), },
        bitsPerPixel=8,
        colourEncoding=PixelFormatInfo.ColourEncoding.RAW,
        packed=True,
        pixelsPerGroup=2,
        planes=[
            PixelFormatInfo.Plane(2, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
    # Compressed formats.
    MJPEG: PixelFormatInfo(
        name="MJPEG",
        format=MJPEG,
        # v4l2Formats = {
        # 	V4L2PixelFormat(V4L2_PIX_FMT_MJPEG),
        # 	V4L2PixelFormat(V4L2_PIX_FMT_JPEG),
        # },
        bitsPerPixel=0,
        colourEncoding=PixelFormatInfo.ColourEncoding.YUV,
        packed=False,
        pixelsPerGroup=1,
        planes=[
            PixelFormatInfo.Plane(1, 1),
            PixelFormatInfo.Plane(0, 0),
            PixelFormatInfo.Plane(0, 0),
        ],
    ),
}
