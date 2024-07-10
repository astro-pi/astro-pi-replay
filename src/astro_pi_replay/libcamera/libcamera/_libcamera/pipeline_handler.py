from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import logging
import threading
from pathlib import Path
from queue import Empty
import os

from PIL import Image
import numpy as np

from .pixel_format import BGR888, SRGGB12_CSI2P
from .request import Request
from astro_pi_replay.resources import get_replay_sequence_dir
from astro_pi_replay.executor import AstroPiExecutor

if TYPE_CHECKING:
    from .cameramanager import CameraManager


logger = logging.getLogger(__name__)

NULL_BYTE: bytes = b"\x00"

class PipelineHandler:

    """
    In this stubbed approximation, this
    is where the requests get processed.
    """
    
    def __init__(self, camera_manager: CameraManager, 
                 executor: AstroPiExecutor) -> None:
        self.manager: CameraManager = camera_manager
        self._executor: AstroPiExecutor = executor
        self.__thread: Optional[threading.Thread] = None
        self.__stop: Optional[threading.Event] = None

    def _process_loop(self):
        """Approximation of what might be running in the background... """

        logger.info("Inside _process_loop")
        for camera in self.manager.cameras:

            try:
                while True:
                    request: Request = camera._queued_requests.get()

                    print("Probably waiting")
                    _name: str = str(
                        self._executor._replay_next(
                            str(get_replay_sequence_dir() / "photos" / "photo_index.csv"),
                            "datetime",
                            ["name"],
                            allow_interpolation=False,
                        )
                    )
                    image_path: Path = get_replay_sequence_dir() / "photos" / _name
                    im: Image.Image = Image.open(image_path)

                    for stream, fb in request.buffers.items():

                        arr: np.ndarray = np.asarray(im)

                        if stream.configuration.pixel_format == BGR888:
                            print("Converted to RGB")

                        elif stream.configuration.pixel_format == SRGGB12_CSI2P:
                            # TODO
                            pass
                        else:
                            print(f"Format {stream.configuration.pixel_format} " +
                                  "not supported by replay tool")
                            continue


                        if stream.configuration.pixel_format == BGR888 \
                                and len(arr.tobytes()) != \
                                stream.configuration.frame_size:
                            h,w,channels = arr.shape
                            assert h == stream.configuration.size.height
                            assert w == stream.configuration.size.width

                            calculated_stride = w * channels
                            print(f"stream.configuration.stride: {stream.configuration.stride}")
                            stride_diff = stream.configuration.stride - calculated_stride
                            print(f"arr.shape: {arr.shape}")
                            print(f"need to pad {stride_diff} bytes per row")
                            # numpy shapes are (height,width,bytes_per_pixel)
                            # so we pad the second dimension (width) to affect
                            # the stride
                            padding=[(0,0), (0,stride_diff // channels), (0,0)]
                            arr = np.pad(arr, padding, mode='constant')

                            print(f"Now arr has shape: {arr.shape} and " +
                                  f"length {len(arr.tobytes())}")
                            print(f"Desired frame_size: {stream.configuration.frame_size}")

                        for plane in fb.planes:
                            print(f"Writing {image_path} as {stream.configuration.pixel_format} " +
                                  f"image of length {len(arr.tobytes())} " +
                                  f"to fd {plane.fd}")
                            os.ftruncate(plane.fd, 0)
                            os.write(plane.fd, arr.tobytes())

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

