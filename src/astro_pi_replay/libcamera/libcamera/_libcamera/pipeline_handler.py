from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import logging
import threading
from queue import Empty

from .request import Request

if TYPE_CHECKING:
    from .cameramanager import CameraManager


logger = logging.getLogger(__name__)

NULL_BYTE: bytes = b"\x00"

class PipelineHandler:

    """
    In this stubbed approximation, this
    is where the requests get processed.
    """
    
    def __init__(self, camera_manager: CameraManager) -> None:
        self.manager: CameraManager = camera_manager
        self.__thread: Optional[threading.Thread] = None
        self.__stop: Optional[threading.Event] = None

    def _process_loop(self):
        """Approximation of what might be running in the background... """

        logger.info("Inside _process_loop")
        for camera in self.manager.cameras:

            try:
                while True:
                    request: Request = camera._queued_requests.get()

                    #_name: str = str(
                    #    self._executor._replay_next(
                    #        str(get_replay_sequence_dir() / "photos" / "photo_index.csv"),
                    #        "datetime",
                    #        ["name"],
                    #        allow_interpolation=False,
                    #    )
                    #)
                    # image_path: Path = get_replay_sequence_dir() / "photos" / _name
                    # im: Image.Image = Image.open(image_path)
                    # TODO put the image into the relevant bit of the request

                    request.status = Request.Status.Complete
                    self.manager._completed_requests.put(request)
                    
                    # write null byte to manager's event fd to signal
                    # a request is ready
                    logger.info("Sending null byte from pipeline_handler")
                    self.manager._w.write(NULL_BYTE)
                    self.manager._w.flush()
            except Empty:
                logger.info("Queue is currently empty")
                
        logger.info("Exiting _process_loop")

    def start(self):
        self.__thread = threading.Thread(target=self._process_loop, daemon=True)
        self.__thread.start()
        self.__stop = threading.Event()

    def stop(self):
        if self.__stop:
            self.__stop.set()

