from typing import Optional, Any
from .camera import Camera, HQCameraAdapter
from .stream import Stream, StreamRole
from .controls.controls import (
    ControlInfoMap, ControlList, ControlId, ControlType,
    ControlInfo, ControlValue
)
from .size import Size
from .rectangle import Rectangle
import os


_RPI4_HQ_CAM_PROPERTIES: dict[ControlId, Any] = {
    ControlId(3, "Model", ControlType.String): 'imx477',
    ControlId(4, "UnitCellSize", ControlType.Size): 
        Size(1550,1550),
    ControlId(10001, "ColorFilterArrangement", ControlType.Integer32): 
        0,
    ControlId(1, "Location", ControlType.Integer32): 
        2,
    ControlId(2, "Rotation", ControlType.Integer32): 
        180,
    ControlId(5, "PixelArraySize", ControlType.Size): 
        Size(4056,3040),
    ControlId(7, "PixelArrayActiveAreas", ControlType.Rectangle): 
        (Rectangle(8, 16, 4056, 3040),),
    ControlId(8, "ScalerCropMaximum", ControlType.Rectangle): 
        Rectangle(0,0,0,0),
    ControlId(10, "SystemDevices", ControlType.Integer64): 
        (20750, 20751, 20737, 20738, 20739),
}

_RPI4_HQ_CAM_CONTROLS: ControlInfoMap = {
    ControlId(22, "Sharpness", ControlType.Float):
        ControlInfo(ControlValue(0.000000), ControlValue(16.000000)),
    ControlId(15, "AwbEnable", ControlType.Bool):
        ControlInfo(ControlValue(False), ControlValue(True)),
    ControlId(13, "Contrast", ControlType.Float):
        ControlInfo(ControlValue(0.000000), ControlValue(32.000000)),
    ControlId(20, "Saturation", ControlType.Float):
        ControlInfo(ControlValue(0.000000), ControlValue(32.000000)),
    ControlId(12, "Brightness", ControlType.Float):
        ControlInfo(ControlValue(-1.000000), ControlValue(1.000000)),
    ControlId(10, "AeFlickerPeriod", ControlType.Integer32):
        ControlInfo(ControlValue(100), ControlValue(1000000)),
    ControlId(41, "HdrMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(4)),
    ControlId(6, "ExposureValue", ControlType.Float):
        ControlInfo(ControlValue(-8.000000), ControlValue(8.000000)),
    ControlId(18, "ColourGains", ControlType.Float):
        ControlInfo(ControlValue(0.000000), ControlValue(32.000000)),
    ControlId(20001, "StatsOutputEnable", ControlType.Bool):
        ControlInfo(ControlValue(False), ControlValue(True)),
    ControlId(25, "ScalerCrop", ControlType.Rectangle):
        ControlInfo(ControlValue(Rectangle(0,0,0,0)),
                    ControlValue(Rectangle(65535, 65535, 65535, 65535))),
    ControlId(7, "ExposureTime", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(66666)),
    ControlId(1, "AeEnable", ControlType.Bool):
        ControlInfo(ControlValue(False), ControlValue(True)),
    ControlId(10002, "NoiseReductionMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(4)),
    ControlId(4, "AeConstraintMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(3)),
    ControlId(28, "FrameDurationLimits", ControlType.Integer64):
        ControlInfo(ControlValue(33333), ControlValue(120000)),
    ControlId(8, "AnalogueGain", ControlType.Float):
        ControlInfo(ControlValue(1.000000), ControlValue(16.000000)),
    ControlId(9, "AeFlickerMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(1)),
    ControlId(16, "AwbMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(7)),
    ControlId(3, "AeMeteringMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(3)),
    ControlId(5, "AeExposureMode", ControlType.Integer32):
        ControlInfo(ControlValue(0), ControlValue(3)),
}

# TODO - stub this method

def _build_camera() -> Camera:
    cam = HQCameraAdapter("/base/soc/i2c0mux/i2c@1/imx477@1a")
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

    cameras: list[Camera] = [_build_camera()]

    def __init__(self) -> None:
        _, w = os.pipe()
        self.event_fd: int = w

    @staticmethod
    def singleton() -> "CameraManager":
        instance: "CameraManager"
        if CameraManager._instance is None:
            _instance = CameraManager()
            instance = _instance
        else:
            instance = CameraManager._instance
        return instance

