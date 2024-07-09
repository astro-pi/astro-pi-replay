import enum
import logging
from typing import Iterable, Optional

from .colorspace import ColorSpace
from .pixel_format import PixelFormat
from .size import Size, SizeRange

log = logging.getLogger(__name__)


class Stream:
    pass


class StreamRole(enum.Enum):
    Raw = 0
    StillCapture = 1
    VideoRecording = 2
    Viewfinder = 3


class StreamFormats:
    """
    Derived from src/libcamera/stream.cpp
    """

    def __init__(self, formats: dict[PixelFormat, list[SizeRange]] = {}):
        self.formats: dict[PixelFormat, list[SizeRange]] = formats

    @property
    def pixel_formats(self) -> list[PixelFormat]:
        return list(self.formats.keys())

        #        pixel_formats=[libcamera.PixelFormat('SRGGB10_CSI2P'), libcamera.PixelFormat('SRGGB12_CSI2P')]

    def range(self, pixel_format: PixelFormat) -> Optional[SizeRange]:
        ranges = self.formats[pixel_format]
        if len(ranges) == 0:
            return
        if len(ranges) == 1:
            return ranges[0]
        range_ = SizeRange()
        for limit in ranges:
            if range_.min is None or limit.min < range_.min:
                range_.min = limit.min
            if range_.max is None or limit.max > range_.max:
                range_.max = limit.max
        return range_

    # [(libcamera.PixelFormat('SRGGB10_CSI2P'), [libcamera.Size(1332, 990)]),
    # (libcamera.PixelFormat('SRGGB12_CSI2P'), [libcamera.Size(2028, 1080), libcamera.Size(2028, 1520), libcamera.Size(4056, 3040)])]

    def sizes(self, pixel_format: PixelFormat) -> list[Size] | None:
        sizes: list[Size] = []

        rangeDiscreteSizes: list[Size] = [
            Size(160, 120),
            Size(240, 160),
            Size(320, 240),
            Size(400, 240),
            Size(480, 320),
            Size(640, 360),
            Size(640, 480),
            Size(720, 480),
            Size(720, 576),
            Size(768, 480),
            Size(800, 600),
            Size(854, 480),
            Size(960, 540),
            Size(960, 640),
            Size(1024, 576),
            Size(1024, 600),
            Size(1024, 768),
            Size(1152, 864),
            Size(1280, 1024),
            Size(1280, 1080),
            Size(1280, 720),
            Size(1280, 800),
            Size(1360, 768),
            Size(1366, 768),
            Size(1400, 1050),
            Size(1440, 900),
            Size(1536, 864),
            Size(1600, 1200),
            Size(1600, 900),
            Size(1680, 1050),
            Size(1920, 1080),
            Size(1920, 1200),
            Size(2048, 1080),
            Size(2048, 1152),
            Size(2048, 1536),
            Size(2160, 1080),
            Size(2560, 1080),
            Size(2560, 1440),
            Size(2560, 1600),
            Size(2560, 2048),
            Size(2960, 1440),
            Size(3200, 1800),
            Size(3200, 2048),
            Size(3200, 2400),
            Size(3440, 1440),
            Size(3840, 1080),
            Size(3840, 1600),
            Size(3840, 2160),
            Size(3840, 2400),
            Size(4096, 2160),
            Size(5120, 2160),
            Size(5120, 2880),
            Size(7680, 4320),
        ]

        if pixel_format not in self.formats:
            return []

        # Try creating a list of discrete sizes
        ranges: list[SizeRange] = self.formats[pixel_format]
        discrete: bool = True
        for _range in ranges:
            print(f"range: {_range}")
            print(f"min: {_range.min}")
            print(f"max: {_range.max}")

            if _range.min != _range.max:
                discrete = False
                break
            sizes.append(_range.min)

        # If discrete not possible generate from range.
        if not discrete:
            print("Not discrete")
            if len(ranges) != 1:
                log.error("Range format is ambiguous")
                return []
            limit: SizeRange = ranges[0]
            print(f"limit: {limit}")
            for size in rangeDiscreteSizes:
                if limit.contains(size):
                    print(f"adding {size}")
                    sizes.append(size)

        return sorted(sizes)


class StreamConfiguration:
    buffer_count: int
    size: Size
    stride: int
    stream: Optional[Stream]
    color_space: ColorSpace
    formats: StreamFormats
    frame_size: int
    pixel_format: PixelFormat
