from __future__ import annotations
import atexit
import os
from typing import Any, Optional
from pathlib import Path
from queue import Queue



from astro_pi_replay.utils import nonblocking_pipe
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import get_replay_sequence_dir

from .camera import Camera, HQCameraAdapter
from .controls.controls import (
    ControlId,
    ControlInfo,
    ControlInfoMap,
    ControlType,
    ControlValue,
)
from .rectangle import Rectangle
from .request import Request
from .size import Size
from .stream import Stream
from .pipeline_handler import PipelineHandler

_RPI4_HQ_CAM_PROPERTIES: dict[ControlId, Any] = {
    ControlId(3, "Model", ControlType.String): "imx477",
    ControlId(4, "UnitCellSize", ControlType.Size): Size(1550, 1550),
    ControlId(10001, "ColorFilterArrangement", ControlType.Integer32): 0,
    ControlId(1, "Location", ControlType.Integer32): 2,
    ControlId(2, "Rotation", ControlType.Integer32): 180,
    ControlId(5, "PixelArraySize", ControlType.Size): Size(4056, 3040),
    ControlId(7, "PixelArrayActiveAreas", ControlType.Rectangle): (
        Rectangle(8, 16, 4056, 3040),
    ),
    ControlId(8, "ScalerCropMaximum", ControlType.Rectangle): Rectangle(0, 0, 0, 0),
    ControlId(10, "SystemDevices", ControlType.Integer64): (
        20750,
        20751,
        20737,
        20738,
        20739,
    ),
}

_RPI4_HQ_CAM_CONTROLS: ControlInfoMap = {
    ControlId(22, "Sharpness", ControlType.Float): ControlInfo(
        ControlValue(0.000000), ControlValue(16.000000)
    ),
    ControlId(15, "AwbEnable", ControlType.Bool): ControlInfo(
        ControlValue(False), ControlValue(True)
    ),
    ControlId(13, "Contrast", ControlType.Float): ControlInfo(
        ControlValue(0.000000), ControlValue(32.000000)
    ),
    ControlId(20, "Saturation", ControlType.Float): ControlInfo(
        ControlValue(0.000000), ControlValue(32.000000)
    ),
    ControlId(12, "Brightness", ControlType.Float): ControlInfo(
        ControlValue(-1.000000), ControlValue(1.000000)
    ),
    ControlId(10, "AeFlickerPeriod", ControlType.Integer32): ControlInfo(
        ControlValue(100), ControlValue(1000000)
    ),
    ControlId(41, "HdrMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(4)
    ),
    ControlId(6, "ExposureValue", ControlType.Float): ControlInfo(
        ControlValue(-8.000000), ControlValue(8.000000)
    ),
    ControlId(18, "ColourGains", ControlType.Float): ControlInfo(
        ControlValue(0.000000), ControlValue(32.000000)
    ),
    ControlId(20001, "StatsOutputEnable", ControlType.Bool): ControlInfo(
        ControlValue(False), ControlValue(True)
    ),
    ControlId(25, "ScalerCrop", ControlType.Rectangle): ControlInfo(
        ControlValue(Rectangle(0, 0, 0, 0)),
        ControlValue(Rectangle(65535, 65535, 65535, 65535)),
    ),
    ControlId(7, "ExposureTime", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(66666)
    ),
    ControlId(1, "AeEnable", ControlType.Bool): ControlInfo(
        ControlValue(False), ControlValue(True)
    ),
    ControlId(10002, "NoiseReductionMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(4)
    ),
    ControlId(4, "AeConstraintMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(3)
    ),
    ControlId(28, "FrameDurationLimits", ControlType.Integer64): ControlInfo(
        ControlValue(33333), ControlValue(120000)
    ),
    ControlId(8, "AnalogueGain", ControlType.Float): ControlInfo(
        ControlValue(1.000000), ControlValue(16.000000)
    ),
    ControlId(9, "AeFlickerMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(1)
    ),
    ControlId(16, "AwbMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(7)
    ),
    ControlId(3, "AeMeteringMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(3)
    ),
    ControlId(5, "AeExposureMode", ControlType.Integer32): ControlInfo(
        ControlValue(0), ControlValue(3)
    ),
}

# TODO - stub this method


def _build_camera(executor: AstroPiExecutor, 
                  pipeline_handler: PipelineHandler) -> Camera:
    cam = HQCameraAdapter(executor, 
                          pipeline_handler,
                          "/base/soc/i2c0mux/i2c@1/imx477@1a")
    cam.properties = _RPI4_HQ_CAM_PROPERTIES
    cam.controls = _RPI4_HQ_CAM_CONTROLS
    return cam


class CameraManager:
    #
    # Rpi 4 stub
    #
    _instance: Optional["CameraManager"] = None

    # def __init__(self, id: str, streams: set[Stream]) -> None:
    #     self.id = id
    #     self.streams = streams


    def __init__(self, executor: AstroPiExecutor) -> None:
        r, w = nonblocking_pipe()
        self._w = os.fdopen(w, 'wb')
        atexit.register(self._close)
        self.event_fd: int = r
        self._completed_requests: Queue[Request] = Queue()
        self.cameras: list[Camera] = [_build_camera(
            executor, 
            PipelineHandler(self, executor))]
        self._executor: AstroPiExecutor = executor

    def _close(self):
        if self._w.closed:
            self._w.close()

    @staticmethod
    def singleton(executor: Optional[AstroPiExecutor] = None) -> "CameraManager":
        instance: "CameraManager"
        if CameraManager._instance is None:
            if executor is None:
                executor = AstroPiExecutor()
            _instance = CameraManager(executor)
            instance = _instance
        else:
            instance = CameraManager._instance
        return instance

    # def _read(fd, dest, max_size) -> int:
    #     """
    #     mimics the read sys command
    #     """
    #     try:
    #         buf = os.read(self.event_fd, 8)
    #         if not buf:
    #             print("EOF")
    #         else:
    #             pass
    #     finally:
    #         pass

    def _process_requests(self):
        """Approximation of what might be running in the background... """

        for camera in self.cameras:
            while len(camera._queued_requests) > 0:
                request: Request = camera._queued_requests.popleft()

                _name: str = str(
                    self._executor._replay_next(
                        str(get_replay_sequence_dir() / "photos" / "photo_index.csv"),
                        "datetime",
                        ["name"],
                        allow_interpolation=False,
                    )
                )

                image_path: Path = get_replay_sequence_dir() / "photos" / _name
                # im: Image.Image = Image.open(image_path)
                # TODO put the image into the relevant bit of the request
                
                request.status = Request.Status.Complete
                self._completed_requests.put(request)

    def get_ready_requests(self) -> list[Request]:
        # this has to be a side-effect in Pyodide since
        # there is no threading and multi-processing.

        to_return: list[Request] = []
        try:
            while True:
                to_return.append(self._completed_requests.get_nowait())
        finally:
            return to_return

