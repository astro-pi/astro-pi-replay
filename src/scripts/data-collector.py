"""
Produces about 1.9G of yuv data per minute
at 3296x2464 resolution, fps of 15.

Convert with ffmpeg:

    ffmpeg -f rawvideo -pix_fmt yuv420p -s:v 3296,2464 -r 15 -i video.data \
            -c:v libx264 output.mp4
# Scale...
ffmpeg -s:v 1920x1080 -r 25 -i input.yuv -vf scale=960:540 \
        -c:v rawvideo -pix_fmt yuv420p out.yuv

"""
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from orbit import ISS, ephemeris
from picamera import PiCamera
from sense_hat import SenseHat
from skyfield.api import load

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
data_file: Path = Path(__file__).parent / "data.csv"

duration: timedelta = timedelta(minutes=1)
end_time: datetime = datetime.now() + duration


def record_sense_hat() -> None:
    """
    Records sense_hat data as fast as possible!
    """
    sh = SenseHat()
    header: str = ",".join(
        [
            "datetime",
            "humidity",
            "humidity",
            "temperature",
            "temperature_from_humidity",
            "temperature_from_pressure",
            "orientation_radians",
            "orientation_degrees",
            "orientation",
            "compass",
            "compass_raw",
            "gyroscope",
            "gyroscope_raw",
            "accelerometer",
            "accelerometer_raw",
            "red",
            "green",
            "blue",
            "clear",
            "red_raw",
            "green_raw",
            "blue_raw",
            "clear_raw",
        ]
    )
    with data_file.open("w") as f:
        f.write(header + "\n")
        while (now := datetime.now()) < end_time:
            line: str = ",".join(
                [
                    str(now),
                    str(sh.get_humidity()),
                    str(sh.get_temperature()),
                    str(sh.get_temperature_from_humidity()),
                    str(sh.get_temperature_from_pressure()),
                    str(sh.get_orientation_radians()),
                    str(sh.get_orientation_degrees()),
                    str(sh.get_orientation()),
                    str(sh.get_compass()),
                    str(sh.get_compass_raw()),
                    str(sh.get_gyroscope()),
                    str(sh.get_gyroscope_raw()),
                    str(sh.get_accelerometer()),
                    str(sh.get_accelerometer_raw()),
                    str(sh.colour.red),
                    str(sh.colour.green),
                    str(sh.colour.blue),
                    str(sh.colour.clear),
                    str(sh.colour.red_raw),
                    str(sh.colour.green_raw),
                    str(sh.colour.blue_raw),
                    str(sh.colour.clear_raw),
                ]
            )
            f.write(f"{line}\n")
            f.flush()


def record_video() -> None:
    cam = PiCamera()
    # maximum native resolution of V2 camera
    cam.resolution = (3280, 2464)
    cam.framerate = 15
    cam.start_recording("video.data", format="yuv")
    remaining: timedelta = end_time - datetime.now()
    cam.wait_recording(round(remaining.total_seconds()))
    cam.stop_recording()


def main() -> None:
    timescale = load.timescale()
    t = timescale.now()
    if not ISS.at(t).is_sunlit(ephemeris):
        logger.warning("Calculated that the ISS is in darkness")

    t1 = threading.Thread(target=record_video)
    t2 = threading.Thread(target=record_sense_hat)
    logger.info("Starting video recording")
    t1.start()
    logger.info("Starting sense hat recording")
    t2.start()
    # wait for the threads to finish
    # t1.join()
    # t2.join()
    while t1.is_alive() or t2.is_alive():
        logger.info(f"Waiting {round(duration.total_seconds()/60)} until completion...")
        sleep(10)


if __name__ == "__main__":
    main()
