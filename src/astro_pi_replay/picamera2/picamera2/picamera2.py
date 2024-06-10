import abc
from pathlib import Path
import sys
from threading import Lock
from typing import cast, Optional, Union, Callable, Any, TypedDict, Literal
import time
import logging
from functools import partial

from PIL import Image

from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import get_replay_sequence_dir
#. import picamera2.formats as formats
#from . import formats
import astro_pi_replay.picamera2.picamera2.formats as formats
import astro_pi_replay.picamera2.picamera2.utils as utils
from .configuration import CameraConfiguration
from .request import CompletedRequest
from .job import Job
from .sensor_format import SensorFormat
import libcamera


_log = logging.getLogger(__name__)
Config = dict

UseCaseString = Literal["still"] | Literal["preview"] | Literal["video"]
class _ConfigurationDict(TypedDict):
    """
    Internal (to Astro-Pi-Replay tool implementation)
    type
    """
    use_case: UseCaseString
    transform: libcamera.Transform
    colour_space: libcamera.ColorSpace
    buffer_count: int
    queue: bool
    #"main": {
    #    "format": "BGR888",
    #    "size": (4056, 3040)
    #},
    main: dict
    lores: Optional[dict]
    #"raw": {
    #    "format": "SRGGB12_CSI2P",
    #    "size": (4056, 3040)
    #},
    raw: Optional[dict]
    #"controls": {
    #    "NoiseReductionMode":  libcamera._libcamera.NoiseReductionModeEnum.HighQuality,
    #    "FrameDurationLimits": (100, 1000000000)
    #},
    controls: dict
    sensor: Optional[dict]
    display: Optional[str]
    encode: Optional[str]


# class Controls:
#     # controls.AeConstraintModeEnum.Normal/Highlight/Shadows/Custom
#     AeConstraintMode: str
#     AeEnable: bool
#     AeExposureMode: str  # controls.AeExposureModeEnum.Normal/Short/Long/Custom
#     AeMeteringMode: str  # controls.AeMeteringModeEnum.CentreWeighted/Spot/Matrix/Custom
#     AfMetering: str  # controls.AfMeteringMode.Auto/Windows
#     AfMode: str  # controls.AfModeEnum.Manual/Auto/Continuous
#     AfPause: str  # contorls.AfPauseEnum.Deferred/Immediate/Resume
#     AfRange: str  # controls.AfRangeEnum.Normal/Macro/Full
#     AnalogueGain: float
#     ColourSaturation: str  # TODO
#     ExposureTime: int
#     FrameDurationLimits: tuple[int, int]
#     FrameRate: float
#     Gain: str  # TODO
#     LensPosition: float
#     Sharpness: str  # TODO

# class CameraConfiguration:
#     buffer_count: int
#     transform: str  # TODO Transform
#     colorspace: str  # ColorSpace
#     name_to_display: str
#     name_to_encode: str
#     controls: str  # TODO Controls
#     main: Optional[bytes]  # todo stream
#     lores: Optional[bytes]  # defaults to YUV420
#     raw: Optional[bytes]
#     # format ?

#     def align(self):
#         pass

#     def enable_lores(self):
#         pass

#     def enable_raw(self):
#         pass



class Picamera2(abc.ABC):
    #
    # Abstract class - includes the interface as well
    # methods directly copied from the real implementation
    #

    _raw_stream_ignore_list: list[str] = [
        "bit_depth", "crop_limits", "exposure_limits",
        "fps", "unpacked"]

    def __init__(self) -> None:
        self._job_list: list[Job] = []
        self.lock: Lock = Lock()
        self.request_lock: Lock = Lock()
        self._requestslock: Lock = Lock()
        self.frames: int = 0
        self.completed_requests: list[CompletedRequest] = []
        self.pre_callback = None
        self.post_callback = None
        self._encoders = set()
        self.stream_map = None
        self._max_queue_len: int = 0
        self.configure_count: int = 0
        self.camera_config: Optional[Config] = None
        self.camera: Optional[libcamera._libcamera.Camera] = None
        self.sensor_resolution: tuple = (4056, 3040)
        self.sensor_format: str = 'SRGGB12_CSI2P'
        self.camera = libcamera.Camera()
        self.camera_ctrl_info: dict[str, \
                tuple[libcamera.ControlId, libcamera.ControlInfo]] = {}

        # TODO set in libcamera later...
        self.camera_properties_: dict = {
            'Model': 'imx477',
            'UnitCellSize': (1550, 1550),
            'ColorFilterArrangement': 0,
            'Location': 2,
            'Rotation': 180,
            'PixelArraySize': (4056, 3040),
            'PixelArrayActiveAreas': [(8, 16, 4056, 3040)],
            'ScalerCropMaximum': (0, 0, 0, 0),
            'SystemDevices': (20750, 20751, 20737, 20738, 20739)
        }

        # TODO set all controls in libcamera stubs later...
        self.camera_ctrl_info["NoiseReductionMode"] = (
            libcamera.ControlId(
                10002,
                "NoiseReductionMode",
                libcamera.ControlType.Integer32), 
            libcamera.ControlInfo(
                libcamera.ControlValue(0),
                libcamera.ControlValue(4)
        ))
        self.camera_ctrl_info["FrameDurationLimits"] = (
            libcamera.ControlId(
                28, 
                "FrameDurationLimits",
                libcamera.ControlType.Integer64), 
            libcamera.ControlInfo(
                libcamera.ControlValue(33333),
                libcamera.ControlValue(120000)
        ))


    @property
    def camera_controls(self) -> dict:
        return {k: (utils.convert_from_libcamera_type(v[1].min),
                    utils.convert_from_libcamera_type(v[1].max),
                    utils.convert_from_libcamera_type(v[1].default)) for k, v in self.camera_ctrl_info.items()}

    @property
    def camera_properties(self) -> dict:
        """Camera properties

        :return: Camera properties
        :rtype: dict
        """
        return {} if self.camera is None else self.camera_properties_

    def _is_rpi_camera(self):
        """Is this camera handled by Raspberry Pi code or not (e.g. a USB cam)"""
        return 'ColorFilterArrangement' in self.camera_properties

    @staticmethod
    def _add_display_and_encode(config, display, encode) -> None:
        if display is not None and config.get(display, None) is None:
            raise RuntimeError(f"Display stream {display} was not defined")
        if encode is not None and config.get(encode, None) is None:
            raise RuntimeError(f"Encode stream {encode} was not defined")
        config['display'] = display
        config['encode'] = encode


    @staticmethod
    def _make_initial_stream_config(stream_config: dict, updates: Optional[dict], ignore_list=[]) -> Optional[dict]:
        """Take an initial stream_config and add any user updates.

        :param stream_config: Stream configuration
        :type stream_config: dict
        :param updates: Updates
        :type updates: dict
        :raises ValueError: Invalid key
        :return: Dictionary of stream config
        :rtype: dict
        """
        if updates is None:
            return None
        valid = ("format", "size", "stride")
        for key, value in updates.items():
            if isinstance(value, SensorFormat):
                value = str(value)
            if key in valid:
                stream_config[key] = value
            elif key in ignore_list:
                pass  # allows us to pass items from the sensor_modes as a raw stream
            else:
                raise ValueError(f"Bad key {key!r}: valid stream configuration keys are {valid}")
        return stream_config

    @staticmethod
    def align_stream(stream_config: dict, optimal=True) -> None:
        if optimal:
            # Adjust the image size so that all planes are a mutliple of 32 bytes wide.
            # This matches the hardware behaviour and means we can be more efficient.
            align = 32
            if stream_config["format"] in ("YUV420", "YVU420"):
                align = 64  # because the UV planes will have half this alignment
            elif stream_config["format"] in ("XBGR8888", "XRGB8888"):
                align = 16  # 4 channels per pixel gives us an automatic extra factor of 2
        else:
            align = 2
        size = stream_config["size"]
        stream_config["size"] = (size[0] - size[0] % align, size[1] - size[1] % 2)

    def _run_process_requests(self):
        pass


    @abc.abstractmethod
    def create_preview_configuration(
        self,
        main: dict = {},
        lores: Optional[dict] = None,
        raw: Optional[dict] = {},
        transform: libcamera.Transform = libcamera.Transform(),
        colour_space: libcamera.ColorSpace = libcamera.ColorSpace.Sycc(),
        buffer_count: int = 4,
        controls: dict = {},
        display: str = "main",
        encode: str = "main",
        queue: bool = True,
        sensor: Optional[dict] = {},
        use_case: UseCaseString =  "preview"
    ) -> dict:
        pass

    @abc.abstractmethod
    def create_still_configuration(
        self, 
        main: dict = {},
        lores: Optional[dict] = None,
        raw: Optional[dict] = {},
        transform: libcamera.Transform =libcamera.Transform(),
        colour_space: libcamera.ColorSpace = libcamera.ColorSpace.Sycc(),
        buffer_count: int =1,
        controls: dict = {},
        display: Optional[str] = None,
        encode: Optional[str] = None,
        queue: bool = True,
        sensor: Optional[dict] = {},
        use_case: UseCaseString = "still") -> dict:
        """Make a configuration suitable for still image capture. Default to 2 buffers, as the Gl preview would need them."""
        pass

    @abc.abstractmethod
    def create_video_configuration(
        self,
        main: dict = {},
        lores: Optional[dict] = None,
        raw: Optional[dict] = {},
        transform: libcamera.Transform = libcamera.Transform(),
        colour_space: Optional[libcamera.ColorSpace] = None,
        buffer_count: int = 6,
        controls: dict = {},
        display: str = "main",
        encode: str = "main",
        queue: bool = True,
        sensor: Optional[dict] = {},
        use_case: UseCaseString =  "video"
    ) -> dict:
        """Make a configuration suitable for camera preview."""
        pass
    
    def dispatch_functions(self,
        functions: list[Callable],
        wait: Optional[bool],
        signal_function: Optional[Callable]=None,
        immediate: bool=False) -> Any:
        """
        Run function in the event loop
        """
        if sys.platform == "emscripten":
            # there is no threading in emscripten, so the
            # best we can do is run the functions immediately
            for function in functions:
                function()
                # TODO need to return the result of the final
                # function
        else:
            # code copied from original picamera2
            if wait is None:
                wait = signal_function is None
            with self.lock:
                only_job = not self._job_list
                job: Job = Job(functions, signal_function)
                self._job_list.append(job)
                # If we're the only job now, and there are completed_requests queued up, then
                # it's worth prodding the event loop immediately as that request may be all we
                # need. We also prod the event loop if "immediate" is set, which can happen for
                # operations that begin by stopping the camera (such as mode switches, or simple
                # stop commands, for which no requests are needed).
                if only_job and (self.completed_requests or immediate):
                    self._run_process_requests()
            return job.get_result() if wait else job

    def process_requests(self, display) -> None:
        # This is the function that the event loop, which runs externally to us, must
        # call.
        requests = []
        with self._requestslock:
            requests = self._requests
            self._requests = []
        self.frames += len(requests)
        # It works like this:
        # * We maintain a list of the requests that libcamera has completed (completed_requests).
        #   But we keep only a minimal number here so that we have one available to "return
        #   quickly" if an application asks for it, but the rest get recycled to libcamera to
        #   keep the camera system running.
        # * The lock here protects the completed_requests list (because if it's non-empty, an
        #   application can pop a request from it asynchronously), and the _job_list. If
        #   we don't have a request immediately available, the application will queue a
        #   "job" for us to execute here in order to accomplish what it wanted.

        with self.lock:
            # These new requests all have one "use" recorded, which is the one for
            # being in this list.  Increase by one, so it cant't get discarded in
            # self.functions block.
            for req in requests:
                req.acquire()
            self.completed_requests += requests

            # This is the request we'll hand back to be displayed. This counts as a "use" too.
            display_request = None
            if requests:
                display_request = requests[-1]
                display_request.acquire()
                display_request.display = True  # display requests by default

            if self.pre_callback:
                for req in requests:
                    # Some applications may (for example) want us to draw something onto these images before
                    # encoding or copying them for an application.
                    self.pre_callback(req)

            # See if we have a job to do. When executed, if it returns True then it's done and
            # we can discard it. Otherwise it remains here to be tried again next time.
            finished_jobs = []
            while self._job_list:
                _log.debug(f"Execute job: {self._job_list[0]}")
                if self._job_list[0].execute():
                    finished_jobs.append(self._job_list.pop(0))
                else:
                    break

            for req in requests:
                # Some applications may want to do something to the image after they've had a change
                # to copy it, but before it goes to the video encoder.
                if self.post_callback:
                    self.post_callback(req)

                for encoder in self._encoders:
                    if encoder.name in self.stream_map:
                        encoder.encode(encoder.name, req)

                req.release()

            # We hang on to the last completed request if we have been asked to.
            while len(self.completed_requests) > self._max_queue_len:
                self.completed_requests.pop(0).release()

        # If one of the functions we ran reconfigured the camera since this request came out,
        # then we don't want it going back to the application as the memory is not valid.
        if display_request is not None:
            if display_request.configure_count == self.configure_count and \
               display_request.config['display'] is not None and display_request.display:
                display.render_request(display_request)
            display_request.release()

        for job in finished_jobs:
            job.signal()

    def start_and_capture_file(
        self,
        name="image.jpg",
        delay=1,
        preview_mode="preview",
        capture_mode="still",
        show_preview=True,
        exif_data=None,
    ) -> None:
        pass

    def start_and_capture_files(
        self,
        name: str = "image{:03d}.jpg",
        initial_delay=1,
        preview_mode="preview",
        capture_mode="still",
        num_files=1,
        delay=1,
        show_preview=True,
        exif_data=None,
    ):
        pass


    def switch_mode_and_capture_file(self,
        camera_config: Config,
        file_output,
        name="main", 
        format=None,
        wait=None,
        signal_function=None,
        exif_data=None, delay=0):
        pass


def Picamera2Adapter(
    maybe_executor: Optional[AstroPiExecutor], *args, **kwargs
) -> Picamera2:
    executor: AstroPiExecutor
    if maybe_executor is None:
        executor = AstroPiExecutor()
    else:
        executor = maybe_executor

    class _Picamera2Adapter(Picamera2):
        title_fields: list[
            str
        ]  # picam2.title_fields = ["ExposureTime", "AnalogueGain"]
        # picam2.create_video_configuration()["controls"]

        camera_controls: str  # TODO Controls
        preview_configuration: Optional[CameraConfiguration]
        still_configuration: Optional[CameraConfiguration]
        video_configuration: Optional[CameraConfiguration]

        def autofocus_cycle(self) -> Union[bool, Lock]:
            return bool()

        def capture_buffer(self):
            pass

        def capture_file_(
            self,
            file_output,
            name: str,
            format=None,
            exif_data=None) -> tuple[bool,Optional[dict]]:

            # TODO  get the next image...
            # I suppose if it 

            if not self.completed_requests:
                return (False, None)
            request = self.completed_requests.pop(0)

            if name == "raw" and self.camera_config and \
                formats.is_raw(self.camera_config["raw"]["format"]):
                request.save_dng(file_output)
            else:
                request.save(name, file_output, format=format, exif_data=exif_data)

            result = request.get_metadata()
            request.release()
            return (True, result)

        def capture_file(
            self,
            file_output,
            name: str = "main",
            format: Optional[str]=None,
            wait: Optional[bool]=None,
            signal_function=None,
            exif_data: Optional[dict]=None) -> dict:
            """Capture an image to a file in the current camera mode.

            Return the metadata for the frame captured.

            exif_data - dictionary containing user defined exif data (based on `piexif`). This will
                overwrite existing exif information generated by picamera2.
            """
            functions = [partial(self.capture_file_, file_output, name, format=format,
                                 exif_data=exif_data)]
            return self.dispatch_functions(functions, wait, signal_function)

        def create_preview_configuration(
            self,
            main: dict = {},
            lores: Optional[dict] = None,
            raw: Optional[dict] = {},
            transform: libcamera.Transform = libcamera.Transform(),
            colour_space: libcamera.ColorSpace = libcamera.ColorSpace.Sycc(),
            buffer_count: int = 4,
            controls: dict = {},
            display: str = "main",
            encode: str = "main",
            queue: bool = True,
            sensor: Optional[dict] = {},
            use_case: UseCaseString =  "preview"
        ) -> dict:
            if self.camera is None:
                raise RuntimeError("Camera not opened")
            # USB cams can't deliver a raw stream.
            if not self._is_rpi_camera():
                raw = None
                sensor = None
            main = cast(dict, self._make_initial_stream_config({"format": "XBGR8888", "size": (640, 480)}, main))
            self.align_stream(main, optimal=False)
            lores = self._make_initial_stream_config({"format": "YUV420", "size": main["size"]}, lores)
            if lores is not None:
                self.align_stream(lores, optimal=False)
            raw = self._make_initial_stream_config({"format": self.sensor_format, "size": main["size"]},
                                                   raw, self._raw_stream_ignore_list)
            # Let the framerate vary from 12fps to as fast as possible.
            if "NoiseReductionMode" in self.camera_controls and "FrameDurationLimits" in self.camera_controls:
                controls = {"NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.Minimal,
                            "FrameDurationLimits": (100, 83333)} | controls
            config = {"use_case": use_case,
                      "transform": transform,
                      "colour_space": colour_space,
                      "buffer_count": buffer_count,
                      "queue": queue,
                      "main": main,
                      "lores": lores,
                      "raw": raw,
                      "controls": controls,
                      "sensor": sensor}
            self._add_display_and_encode(config, display, encode)
            return config

        def create_still_configuration(
            self, 
            main: dict = {},
            lores: Optional[dict] = None,
            raw: Optional[dict] = {},
            transform: libcamera.Transform =libcamera.Transform(),
            colour_space: libcamera.ColorSpace = libcamera.ColorSpace.Sycc(),
            buffer_count: int =1,
            controls: dict = {},
            display: Optional[str] = None,
            encode: Optional[str] = None,
            queue: bool = True,
            sensor: Optional[dict] = {},
            use_case: UseCaseString = "still") -> dict:
            """Make a configuration suitable for still image capture. Default to 2 buffers, as the Gl preview would need them."""

            if self.camera is None:
                raise RuntimeError("Camera not opened")
            # USB cams can't deliver a raw stream.
            if not self._is_rpi_camera():
                raw = None
                sensor = None
            main = cast(dict, self._make_initial_stream_config({"format": "BGR888", "size": self.sensor_resolution}, main))
            if main is None:
                raise RuntimeError("main cannot be None")
            self.align_stream(main, optimal=False)
            lores = self._make_initial_stream_config({"format": "YUV420", "size": main["size"]}, lores)
            if lores is not None:
                self.align_stream(lores, optimal=False)
            raw = self._make_initial_stream_config({"format": self.sensor_format, "size": main["size"]},
                                                   raw, self._raw_stream_ignore_list)
            # Let the framerate span the entire possible range of the sensor.
            if "NoiseReductionMode" in self.camera_controls and "FrameDurationLimits" in self.camera_controls:
                controls = {"NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.HighQuality,
                            "FrameDurationLimits": (100, 1000000 * 1000)} | controls

            config: _ConfigurationDict = {
              "use_case": use_case,
              "transform": transform, # identity
              "colour_space": colour_space,
              "buffer_count": buffer_count,
              "queue": queue,
              "main": main,
              "lores": lores,
              "raw": raw,
              "controls": controls,
              "sensor": sensor, 
              "display": display,
              "encode": encode
            }

            self._add_display_and_encode(config, display, encode)
            return cast(dict, config)

        def create_video_configuration(
            self,
            main: dict = {},
            lores: Optional[dict] = None,
            raw: Optional[dict] = {},
            transform: libcamera.Transform = libcamera.Transform(),
            colour_space: Optional[libcamera.ColorSpace] = None,
            buffer_count: int = 6,
            controls: dict = {},
            display: str = "main",
            encode: str = "main",
            queue: bool = True,
            sensor: Optional[dict] = {},
            use_case: UseCaseString =  "video"
        ) -> dict:

            if self.camera is None:
                raise RuntimeError("Camera not opened")
            # USB cams can't deliver a raw stream.
            if not self._is_rpi_camera():
                raw = None
                sensor = None
            main = cast(dict, self._make_initial_stream_config({"format": "XBGR8888", "size": (1280, 720)}, main))
            self.align_stream(main, optimal=False)
            lores = self._make_initial_stream_config({"format": "YUV420", "size": main["size"]}, lores)
            if lores is not None:
                self.align_stream(lores, optimal=False)
            raw = self._make_initial_stream_config({"format": self.sensor_format, "size": main["size"]},
                                                   raw, self._raw_stream_ignore_list)
            if colour_space is None:
                # Choose default colour space according to the video resolution.
                if main["size"][0] < 1280 or main["size"][1] < 720:
                    colour_space = libcamera.ColorSpace.Smpte170m()
                else:
                    colour_space = libcamera.ColorSpace.Rec709()
            if "NoiseReductionMode" in self.camera_controls and "FrameDurationLimits" in self.camera_controls:
                controls = {"NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.Fast,
                            "FrameDurationLimits": (33333, 33333)} | controls
            config = {"use_case": use_case,
                      "transform": transform,
                      "colour_space": colour_space,
                      "buffer_count": buffer_count,
                      "queue": queue,
                      "main": main,
                      "lores": lores,
                      "raw": raw,
                      "controls": controls,
                      "sensor": sensor}
            self._add_display_and_encode(config, display, encode)
            return config

        def configure(
            self,
            config_type: Optional[str] = None,
            config: Optional[CameraConfiguration] = None,
        ):
            pass

        def set_controls(self, controls: dict):
            pass

        def start(self):
            pass

        def start_and_capture_file(
            self,
            name="image.jpg",
            delay=1,
            preview_mode="preview",
            capture_mode="still",
            show_preview=True,
            exif_data=None,
        ):
            _name: str = str(
                executor._replay_next(
                    str(get_replay_sequence_dir() / "photos" \
                            / "photo_index.csv"),
                    "datetime",
                    ["name"],
                    allow_interpolation=False,
                )
            )

            image_path: Path = get_replay_sequence_dir() / "photos" / _name
            im = Image.open(image_path)
            im.save(name)

        def start_and_capture_files(
            self,
            name: str = "image{:03d}.jpg",
            initial_delay=1,
            preview_mode="preview",
            capture_mode="still",
            num_files=1,
            delay=1,
            show_preview=True,
            exif_data=None,
        ):
            if initial_delay:
                time.sleep(initial_delay)

            for i in range(num_files):
                self.start_and_capture_file(
                    name.format(i),
                )

        def start_and_record_video(self, output, duration=5):
            pass

        def start_preview(self):
            pass

        def stop_preview(self):
            pass

        def switch_mode_and_capture_file(self,
            camera_config: Config,
            file_output,
            name="main", 
            format=None,
            wait=None,
            signal_function=None,
            exif_data=None, delay=0):
            pass

        def wait(self, job: Lock):
            pass

    return _Picamera2Adapter(*args, **kwargs)


class Preview:
    pass
