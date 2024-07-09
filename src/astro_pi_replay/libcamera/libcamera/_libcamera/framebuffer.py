from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import enum
import dataclasses


if TYPE_CHECKING:
    from libcamera._libcamera.request import Request


class Plane:

    def __init__(self):
        self.fd: int = -1
        self.length: int = 0
        self.offset: int = 4294967295


class FrameMetadata:
    class Status(enum.Enum):
        FrameSuccess = 0
        FrameError = 1
        FrameCancelled = 2

    @dataclasses.dataclass
    class Plane:
        bytesused: int

    planes: list[Plane] = []

class FrameBuffer:

    Plane = Plane

    def __init__(self, planes: list[Plane], cookie: int = 0) -> None:
        self.planes: list[Plane] = planes
        self.cookie_: int = cookie
        self._request: Optional[Request] = None
        self.metadata = FrameMetadata()

    def set_request(self, request: Request):
        self._request = request

