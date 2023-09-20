from time import sleep
from astro_pi_executor.picamera import PiCamera
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    cam = PiCamera()
    cam.start_preview()
    sleep(20)
    cam.stop_preview()
