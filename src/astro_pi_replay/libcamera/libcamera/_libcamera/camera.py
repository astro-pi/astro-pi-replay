import abc
import dataclasses
import enum
from typing import Iterator

from . import pixel_format
from .colorspace import ColorSpace
from .controls.controls import ControlInfoMap
from .orientation import Orientation
from .rectangle import Rectangle
from .size import Size, SizeRange
from .stream import Stream, StreamConfiguration, StreamFormats, StreamRole


@dataclasses.dataclass
class SensorConfiguration:
    bitDepth: int = 0
    analogCrop: Rectangle = Rectangle(0, 0, 0, 0)
    binning: tuple[int, int] = (1, 1)
    skipping: tuple[int, int, int, int] = (1, 1, 1, 1)
    output_size: Size = Size(0, 0)

    def isValid(self) -> bool:
        return False


class Status(enum.Enum):
    Valid = 0
    Adjusted = 1
    Invalid = 2


class CameraConfiguration:
    Status = Status

    def __init__(self):
        # technically, there is no constructor exposed by libcamera
        self.orientation: Orientation = Orientation.Rotate0
        self._stream_configurations: list[StreamConfiguration] = []
        self.sensor_config = None

    def __iter__(self):
        return self._stream_configurations.__iter__()

    @property
    def size(self) -> int:
        return len(self._stream_configurations)

    @property
    def empty(self) -> bool:
        return len(self._stream_configurations) == 0

    def at(self, index: int) -> StreamConfiguration:
        return self._stream_configurations[index]

    def validate(self) -> Status:
        # TODO copy implementation from libcamera?
        return Status.Valid


class Camera:
    # streams: set["Stream"]

    def __init__(self, id: str) -> None:
        self.id: str = id
        self.controls: ControlInfoMap = {}
        self.properties: ControlInfoMap = {}

    def acquire(self) -> int:
        return 0

    def configure(self, configuration: CameraConfiguration):
        pass

    def create_request(self):
        pass

    @abc.abstractmethod
    def generate_configuration(self, roles: list[StreamRole]) -> CameraConfiguration:
        pass

    def queue_request(self):
        pass

    def release(self) -> int:
        return 0

    def start(self):
        pass

    def stop(self):
        pass

    def streams(self):
        pass


class HQCameraAdapter(Camera):
    def generate_configuration(self, roles: list[StreamRole]) -> CameraConfiguration:
        if len(roles) == 0:
            raise RuntimeError("Must provide a StreamRole")

        camera_configuration = CameraConfiguration()

        for role in roles:
            stream_configuration = StreamConfiguration()
            if role == StreamRole.Viewfinder:
                # this is the main one
                stream_configuration.buffer_count = 1
                stream_configuration.frame_size = 1920000
                stream_configuration.size = Size(4056, 3040)
                stream_configuration.stride = 0
                stream_configuration.stream = None
                stream_configuration.color_space = ColorSpace.Srgb()
                stream_configuration.pixel_format = pixel_format.BGR888
                stream_configuration.formats = StreamFormats(
                    {
                        pixel_format.NV21: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.YUV420: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.NV12: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.YVU420: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.XBGR8888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pixel_format.BGR888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pixel_format.RGB888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pixel_format.XRGB8888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pixel_format.RGB565: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pixel_format.YVYU: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.YUYV: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.VYUY: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pixel_format.UYVY: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                    }
                )
            elif role == StreamRole.Raw:
                stream_configuration.buffer_count = 2
                stream_configuration.size = Size(4056, 3040)
                stream_configuration.stride = 6112
                stream_configuration.stream = None
                stream_configuration.color_space = ColorSpace.Raw()
                stream_configuration.pixel_format = pixel_format.SBGGR12
                stream_configuration.frame_size = 18580480
                stream_configuration.formats = StreamFormats(
                    {
                        pixel_format.SRGGB10_CSI2P: [
                            SizeRange(Size(1332, 990), Size(1332, 990), 1, 1)
                        ],
                        pixel_format.SRGGB12_CSI2P: [
                            SizeRange(Size(2028, 1080), Size(4056, 3040))
                        ],
                    }
                )
            else:
                raise RuntimeError("I need implementing for non-Raw")

            camera_configuration._stream_configurations.append(stream_configuration)
        return camera_configuration
