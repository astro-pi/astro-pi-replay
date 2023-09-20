from threading import Lock
from typing import Optional, Union

# from libcamera import controls


class Controls:
    # controls.AeConstraintModeEnum.Normal/Highlight/Shadows/Custom
    AeConstraintMode: str
    AeEnable: bool
    AeExposureMode: str  # controls.AeExposureModeEnum.Normal/Short/Long/Custom
    AeMeteringMode: str  # controls.AeMeteringModeEnum.CentreWeighted/Spot/Matrix/Custom
    AfMetering: str  # controls.AfMeteringMode.Auto/Windows
    AfMode: str  # controls.AfModeEnum.Manual/Auto/Continuous
    AfPause: str  # contorls.AfPauseEnum.Deferred/Immediate/Resume
    AfRange: str  # controls.AfRangeEnum.Normal/Macro/Full
    AnalogueGain: float
    ColourSaturation: str  # TODO
    ExposureTime: int
    FrameDurationLimits: tuple[int, int]
    FrameRate: float
    Gain: str  # TODO
    LensPosition: float
    Sharpness: str  # TODO

    def __enter__(self):
        pass

    def __exit__(self):
        pass


class CameraConfiguration:
    buffer_count: int
    transform: str  # TODO Transform
    colorspace: str  # ColorSpace
    name_to_display: str
    name_to_encode: str
    controls: str  # TODO Controls
    main: Optional[bytes]  # todo stream
    lores: Optional[bytes]  # defaults to YUV420
    raw: Optional[bytes]
    # format ?

    def align(self):
        pass

    def enable_lores(self):
        pass

    def enable_raw(self):
        pass


class Picamera2:
    title_fields: list[str]  # picam2.title_fields = ["ExposureTime", "AnalogueGain"]
    # picam2.create_video_configuration()["controls"]

    camera_controls: str  # TODO Controls
    preview_configuration: Optional[CameraConfiguration]
    still_configuration: Optional[CameraConfiguration]
    video_configuration: Optional[CameraConfiguration]

    def __init__(self):
        pass

    def autofocus_cycle(self) -> Union[bool, Lock]:
        return bool()

    def capture_buffer(self):
        pass

    def create_preview_configuration(
        self, colour_space, transform, queue, lores, raw, **options
    ):
        pass

    def create_still_configuration(self, buffer_count, lores, display):
        pass

    def create_video_configuration(self, main, lores, encode, controls):
        pass

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

    def start_and_capture_file(self):
        pass

    def start_and_record_video(self, output, duration=5):
        pass

    def start_preview(self):
        pass

    def stop_preview(self):
        pass

    def wait(self, job: Lock):
        pass


class Preview:
    pass
