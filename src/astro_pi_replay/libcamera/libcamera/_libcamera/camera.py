import abc
import dataclasses
import enum
import errno
from typing import Optional
import inspect
import logging
from queue import Queue

from astro_pi_replay.executor import AstroPiExecutor
from . import pixel_format as pf
from .colorspace import ColorSpace
from .controls.controls import ControlInfoMap, ControlList
from .orientation import Orientation
from .rectangle import Rectangle
from .pipeline_handler import PipelineHandler
from .request import Request
from .size import Size, SizeRange
from .stream import Stream, StreamConfiguration, StreamFormats, StreamRole

logger = logging.getLogger(__name__)


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
        # src/libcamera/pipeline/rpi/common/pipeline_base.cpp
        status = Status.Valid

        # TODO this only works as expected if user
        # has already configured the camera with cam.create_still_configuration()
        # - should probably set this to happen only when that is called.

        # In the real RP implementation the stride is set
        # and the return status is set to Adjusted 

        for stream_config in self._stream_configurations:
            if stream_config.stride == 0 and \
                    stream_config.pixel_format == pf.BGR888:
                        stream_config.stride = 12192
                        status = Status.Adjusted
            elif stream_config.stride == 0 and \
                    stream_config.pixel_format == pf.SRGGB12_CSI2P:
                        stream_config.stride = 6112
                        status = Status.Adjusted
        return status


class State(enum.Enum):
    CameraAvailable = 0
    CameraAcquired = 1
    CameraConfigured = 2
    CameraStopping = 3
    CameraRunning = 4


"""
Based on:
 * include/libcamera/camera.h
 * src/libcamera/camera.cpp
"""
class Camera:
    # streams: set["Stream"]

    # pipeline_handler is not in the real signature...
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.controls: ControlInfoMap = {}
        self.properties: ControlInfoMap = {}
        self._state: State = State.CameraAvailable
        self._disconnected: bool = False
        # TODO may want to use something thread-safe here...
        self._queued_requests: Queue[Request] = Queue()
        self._pipeline_handler: Optional[PipelineHandler] = None

    def acquire(self) -> int:
        self._state = State.CameraAcquired
        return 0

    def configure(self, configuration: CameraConfiguration):
        self._state = State.CameraConfigured

    def _is_access_allowed(
            self, 
            low: State, 
            high: Optional[State] = None, 
            allowDisconnected: bool = False,
            from_: str = "") -> int:

        def get_from():
            _from_ = from_
            if from_ == "":
                frame = inspect.currentframe()
                if frame is None or \
                        frame.f_back is None or \
                        frame.f_back.f_code is None:
                    _from_ = "<UNKNOWN FUNCTION>"
                else:
                    _from_ = frame.f_back.f_code.co_name
            return f"{_from_}()"

        if not allowDisconnected and self._disconnected:
            return -errno.ENODEV

        if (high is None and self._state == low) or \
            (high is not None and self._state.value >= low.value and \
            self._state.value <= high.value):
                return 0
        elif high is None:
            print(self._state, low, self._state == low, self._state is low)

            logger.error(
        	    f"Camera in {self._state}" + \
			    f" state trying {get_from()}" + \
                f" requiring state {low}")
            return -errno.EACCES
        else:
            logger.error(
                f"Camera in {self._state}" + \
                f" state trying {get_from()} "  + \
                "requiring state between " + \
                f"{low} and {high}")
            return -errno.EACCES

    # See /src/py/libcamera/py_main.cpp
    # and src/libcamera/camera.cpp
    def create_request(self, cookie: int = 0) -> Request | None:
        ret: int = self._is_access_allowed(State.CameraConfigured, State.CameraRunning)
        if ret < 0:
            return
        req = Request(cookie)

        # the real implementation associates it with a PipelineHandler
        # for more info see libcamera's src/py/examples/simple_cam.py
        return req


    @abc.abstractmethod
    def generate_configuration(
            self, 
            roles: list[StreamRole]) -> CameraConfiguration:
        pass

    # based on src/libcamera/camera.cpp
    def queue_request(self, request: Request) -> int:
        # real implementation checks if camera is running
        ret: int = self._is_access_allowed(State.CameraRunning)
        if ret < 0:
            return ret

        # real implementation checks if request's camera pointer is this camera
        if request.status != Request.Status.RequestPending:
            raise ValueError(f"{request} is not valid")
        if len(request.buffers) == 0:
            raise ValueError("Request contains no buffers")

        # real implementation checks that all streams are active

        # real implementation calls PipelineHandler, which eventually
        # calls PipelineHandler.doQueueReqest, which puts the request
        # into Camera.queuedRequests_
        self._queued_requests.put(request)
        return 0

    def release(self) -> int:
        return 0

    def start(self, controls: ControlList) -> int:
        ret = self._is_access_allowed(State.CameraConfigured)
        if ret < 0:
            return ret

        if not self._pipeline_handler:
            print("NOT ALLOWED")
            return -errno.EAGAIN
        self._pipeline_handler.start()
        self._state = State.CameraRunning

        return 0

    def stop(self):
        if self._pipeline_handler:
            self._pipeline_handler.stop()

    def streams(self):
        pass


class HQCameraAdapter(Camera):

    def __init__(self, executor: AstroPiExecutor, 
                 pipeline_handler: PipelineHandler,
                 *args, **kwargs):
        self.executor: AstroPiExecutor = executor
        super().__init__(*args, **kwargs)
        self._pipeline_handler = pipeline_handler

    # This is a stub for the default create_still_configuration
    #
    # see src/libcamera/pipeline/rpi/common/pipeline_base.cpp
    def generate_configuration(self, roles: list[StreamRole]) -> CameraConfiguration:
        if len(roles) == 0:
            raise RuntimeError("Must provide a StreamRole")

        camera_configuration = CameraConfiguration()

        for role in roles:
            stream_configuration = StreamConfiguration()
            if role == StreamRole.Viewfinder:
                # this is the main one
                stream_configuration.buffer_count = 1
                stream_configuration.frame_size = 37063680
                stream_configuration.size = Size(4056, 3040)
                stream_configuration.stride = 12192
                stream_configuration.stream = Stream(stream_configuration)
                stream_configuration.color_space = ColorSpace.Srgb()
                stream_configuration.pixel_format = pf.BGR888
                stream_configuration.formats = StreamFormats(
                    {
                        pf.NV21: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.YUV420: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.NV12: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.YVU420: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.XBGR8888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pf.BGR888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pf.RGB888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pf.XRGB8888: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pf.RGB565: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 1, 1)
                        ],
                        pf.YVYU: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.YUYV: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.VYUY: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                        pf.UYVY: [
                            SizeRange(Size(64, 64), Size(4056, 3040), 2, 2)
                        ],
                    }
                )
            elif role == StreamRole.Raw:
                stream_configuration.buffer_count = 2
                stream_configuration.size = Size(4056, 3040)
                stream_configuration.stride = 6112
                stream_configuration.stream = Stream(stream_configuration)
                stream_configuration.color_space = ColorSpace.Raw()
                # pf.SRGGB12_CSI2P if not configured
                stream_configuration.pixel_format = pf.SBGGR12

                stream_configuration.frame_size = 18580480
                stream_configuration.formats = StreamFormats(
                    {
                        pf.SRGGB10_CSI2P: [
                            SizeRange(Size(1332, 990), Size(1332, 990), 1, 1)
                        ],
                        pf.SRGGB12_CSI2P: [
                            SizeRange(Size(2028, 1080), Size(4056, 3040))
                        ],
                    }
                )
                def stubbed_sizes(pixel_format: pf.PixelFormat) -> Optional[list[Size]]:
                    """
                    sizes are populated in pipeline_base.cpp registerCamera method.
                    """
                    if pixel_format == pf.SRGGB10_CSI2P:
                        return [Size(1332,990)]
                    elif pixel_format == pf.SRGGB12_CSI2P:
                        return [Size(2028, 1080), Size(2028, 1520), Size(4056, 3040)]
                    else:
                        raise RuntimeError("Not yet supported")
                stream_configuration.formats.sizes = stubbed_sizes
            else:
                raise RuntimeError("I need implementing for non-Raw")

            camera_configuration._stream_configurations.append(stream_configuration)
        return camera_configuration

