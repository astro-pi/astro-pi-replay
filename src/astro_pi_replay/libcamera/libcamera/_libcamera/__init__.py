"""
In the real picamera2 implementation, the _libcamera
module is compiled from cpp sources.

As it uses Linux only constructs (e.g. eventfd), we can't use it with
the Astro-Pi-Replay tool.
"""

from .camera import Camera
from .control_ids_draft import NoiseReductionModeEnum
from .control_ids_core import FrameDurationLimits

__all__ = [
    "Camera",
    "FrameDurationLimits",
    "NoiseReductionModeEnum"
]
