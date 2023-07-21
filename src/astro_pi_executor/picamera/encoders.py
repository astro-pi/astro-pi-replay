import logging
from threading import Event, Lock
from typing import BinaryIO, Optional

from astro_pi_executor.picamera.frames import PiVideoFrameType
from astro_pi_executor.picamera.mmalobj import (
    MMALBuffer,
    MMALComponent,
    MMALPort,
    MMALResizer,
    MMALVideoPort,
)
from astro_pi_executor.picamera.picamera_public_api import PiCamera

logger = logging.getLogger(__name__)


class PiEncoder:
    def __init__(
        self,
        parent: PiCamera,
        camera_port: MMALVideoPort,
        input_port: MMALVideoPort,
        format: str,
        resize: Optional[tuple[int, int]],
        **options,
    ) -> None:
        self.parent = parent
        self.camera_port = camera_port
        self.input_port = input_port
        self.format = format
        self.resize = resize
        self.output_port = MMALVideoPort()
        self._event = Event()
        self._outputs_lock = Lock()

    def _callback(self, port: MMALPort, buf: MMALBuffer):
        pass

    def _callback_write(self, buf, key=PiVideoFrameType.frame):
        pass

    def _close_output(self, key=PiVideoFrameType.frame):
        pass

    def _create_encoder(self, format):
        pass

    def _create_resizer(self, width, height):
        pass

    def _open_output(self, output, key=PiVideoFrameType.frame):
        pass

    def close(self) -> None:
        pass

    @property
    def encoder(self) -> Optional[MMALComponent]:
        pass

    @property
    def exception(self) -> Optional[Exception]:
        pass

    @property
    def event(self) -> Event:
        return self._event

    @property
    def outputs(self) -> dict[str, tuple[BinaryIO, bool]]:
        return {}

    @property
    def outputs_lock(self):
        return self._outputs_lock

    @property
    def pool(self) -> None:
        # TODO this hsould be a pointer...
        pass

    @property
    def resizer(self) -> Optional[MMALResizer]:
        pass

    def start(self, output) -> None:
        pass

    def stop(self) -> None:
        pass

    def wait(self, timeout: Optional[int] = None) -> None:
        pass
