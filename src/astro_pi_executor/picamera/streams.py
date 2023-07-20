import io
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class CircularIO(io.BytesIO):
    def __init__(self, size: int) -> None:
        self._size = size

    def lock(self) -> Lock:
        return Lock()

    def read_all(self) -> bytes:
        return bytes()

    def size(self) -> int:
        return self._size


# class PiCameraCircularIO(camera,
#                          size=None,
#                          seconds=None,
#                          bitrate=17000000,
#                          splitter_port=1):
#     pass
