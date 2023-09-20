from astro_pi_executor.picamera import PiCamera
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

cam = PiCamera()

stem = "example"
formats = ["h264", "mjpeg", "rgb", "rgba", "yuv", "bgr", "bgra"]
for fmt in formats:
    name: str = f"{stem}.{fmt}"
    logger.info(f"Recording into {name}")
    cam.start_recording(name)
    cam.wait_recording(5)
    cam.stop_recording()
logger.info("Complete")
# TODO convert into tests :)
