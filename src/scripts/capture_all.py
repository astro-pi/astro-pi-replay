"""
This script collects data on behalf of the
Raspberry Pi Foundation for future use by the Astro Pi Replay
tool and Mission Space Lab.

It collects every possible data point available on the sense hat
and camera as fast as possible.
"""
import logging
import time
import traceback
import os
from datetime import datetime, timedelta
from multiprocessing import Process, Event
from multiprocessing.synchronize import Event as EventT
from pathlib import Path
from typing import Union, TypeVar, Callable, Optional

from gpiozero import MotionSensor, CPUTemperature
from orbit import ISS
from picamera import PiCamera
from sense_hat import SenseHat
from skyfield.units import Angle


#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


CURRENT_DIR: Path = Path(__file__).parent
IMAGES_DIR: Path = CURRENT_DIR / "images"
CAM_DATA_FILE: Path = CURRENT_DIR / "camdata.csv"
SENSE_HAT_DATA_FILE: Path = CURRENT_DIR / "sense_hat_data.csv"
GPIOZERO_DATA_FILE: Path = CURRENT_DIR / "gpiozero_data.csv"
DELIMITER: str = ","
NUM_MINUTES: int = 11
MINUTES: int = 60
iss: ISS = ISS()


def convert(angle: Angle) -> tuple[bool, str]:
    """
    Convert a `skyfield` Angle to an EXIF-appropriate
    representation (positive rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"

    Return a tuple containing a boolean and the converted angle,
    with the boolean indicating if the angle is negative.
    """
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle

def capture(camera: PiCamera, image: str) -> None:
    """
    Use `camera` to capture an `image` file with lat/long EXIF data.
    """
    subpoint = iss.coordinates()

    # Convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(subpoint.latitude)
    west, exif_longitude = convert(subpoint.longitude)

    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"
    # Altitude is a RATIONAL type according to the TIFF specs
    camera.exif_tags['GPS.GPSAltitude'] = f"{round(subpoint.elevation.m)}/1"
    camera.exif_tags['GPS.GPSAltitudeRef'] = "0" # above sea-level

    # Log additional information for the mock picamera library
    row: list[str] = [
        datetime.now().isoformat(),
        str(camera.awb_gains),
        str(camera.annotate_text_size),
        str(camera.awb_mode),
        str(camera.brightness),
        str(camera.clock_mode),
        str(camera.closed),
        str(camera.color_effects),
        str(camera.contrast),
        str(camera.crop),
        str(camera.digital_gain),
        str(camera.drc_strength),
        str(camera.exposure_compensation),
        str(camera.exposure_mode),
        str(camera.exposure_speed),
        str(camera.flash_mode),
        str(camera.framerate),
        str(camera.framerate_delta),
        str(camera.framerate_range),
        str(camera.image_denoise),
        str(camera.image_effect),
        str(camera.image_effect_params),
        str(camera.iso),
        str(camera.meter_mode),
        str(camera.overlays),
        str(camera.raw_format),
        str(camera.saturation),
        str(camera.sensor_mode),
        str(camera.sharpness),
        str(camera.shutter_speed),
        str(camera.still_stats),
        str(camera.timestamp),
        str(camera.video_denoise),
        str(camera.video_stabilization),
        str(camera.zoom),
    ]
    with CAM_DATA_FILE.open("a") as f:
        f.write(DELIMITER.join(row) + os.linesep)

    # Capture the image
    camera.capture(str(IMAGES_DIR / image))

T1 = TypeVar("T1")
T2 = TypeVar("T2")

def try_except_runtime_error(success: Callable[[],T1], 
                             failure: Optional[Union[T2,Callable[[],T2]]]=None) -> Union[T1,T2, str]:
    try:
        return success()
    except RuntimeError:
        traceback.print_exc()
        if failure is None:
            return ""
        if callable(failure):
            return failure()
        return failure

def run_camera(event: EventT) -> None:
    logger.debug("Camera process started")
    # expecting ~1fps
    # one process takes photos continuously and marks the location
    # in the exif tags

    # Initialise camera
    cam: PiCamera = PiCamera()
    cam.resolution = (4056,3040) # full resolution

    header: list[str] = [
        "datetime",
        "awb_gains",
        "annotate_text_size",
        "awb_mode",
        "brightness",
        "clock_mode",
        "closed",
        "color_effects",
        "contrast",
        "crop",
        "digital_gain",
        "drc_strength",
        "exposure_compensation",
        "exposure_mode",
        "exposure_speed",
        "flash_mode",
        "framerate",
        "framerate_delta",
        "framerate_range",
        "image_denoise",
        "image_effect",
        "image_effect_params",
        "iso",
        "meter_mode",
        "overlays",
        "raw_format",
        "saturation",
        "sensor_mode",
        "sharpness",
        "shutter_speed",
        "still_stats",
        "timestamp",
        "video_denoise",
        "video_stabilization",
        "zoom",
    ]

    if not CAM_DATA_FILE.exists():
        logger.debug(f"Creating {CAM_DATA_FILE}...")
        CAM_DATA_FILE.write_text(DELIMITER.join(header) + os.linesep)

    logger.info("Starting camera capture loop...")
    i: int = 0
    while not event.is_set():
        capture(cam, f"img_{i}.jpg")
        i += 1
    logger.debug("Event is set - stopping camera capture")

def run_gpiozero_data_collection(event: EventT) -> None:
    logger.debug("gpiozero process started")
    pir_sensor: MotionSensor = MotionSensor(12)
    cpu_temp: CPUTemperature = CPUTemperature()

    header: list[str] = [
        "datetime",
        "pir_sensor.active_time",
        "pir_sensor.close",
        "pir_sensor.inactive_time",
        "pir_sensor.is_active",
        "pir_sensor.motion_detected",
        "pir_sensor.partial",
        "pir_sensor.pin",
        "pir_sensor.pin_factory",
        "pir_sensor.pull_up",
        "pir_sensor.queue_len",
        "pir_sensor.threshold",
        "pir_sensor.value",
        "pir_sensor.when_activated",
        "pir_sensor.when_deactivated",
        "pir_sensor.when_motion",
        "pir_sensor.when_no_motion",
        "cpu_temp.active_time",
        "cpu_temp.closed",
        "cpu_temp.event_delay",
        "cpu_temp.inactive_time",
        "cpu_temp.is_active",
        "cpu_temp.max_temp",
        "cpu_temp.min_temp",
        "cpu_temp.pin_factory",
        "cpu_temp.sensor_file",
        "cpu_temp.temperature",
        "cpu_temp.threshold",
        "cpu_temp.value",
        "cpu_temp.when_activated",
        "cpu_temp.when_deactivated"
    ]
    if not GPIOZERO_DATA_FILE.exists():
        logger.debug(f"Creating {GPIOZERO_DATA_FILE}...")
        GPIOZERO_DATA_FILE.write_text(DELIMITER.join(header) + os.linesep)
    
    logger.info("Starting gpiozero capture loop...")
    while not event.is_set():
        row: list[str] = [
            datetime.now().isoformat(),
            str(pir_sensor.active_time),
            str(pir_sensor.close),
            str(pir_sensor.inactive_time),
            str(try_except_runtime_error(lambda: pir_sensor.is_active)),
            str(try_except_runtime_error(lambda: pir_sensor.motion_detected)),
            str(pir_sensor.partial),
            str(pir_sensor.pin),
            str(pir_sensor.pin_factory),
            str(pir_sensor.pull_up),
            str(pir_sensor.queue_len),
            str(pir_sensor.threshold),
            str(try_except_runtime_error(lambda: pir_sensor.value)),
            str(pir_sensor.when_activated),
            str(pir_sensor.when_deactivated),
            str(pir_sensor.when_motion),
            str(pir_sensor.when_no_motion),
            str(cpu_temp.active_time),
            str(cpu_temp.closed),
            str(cpu_temp.event_delay),
            str(cpu_temp.inactive_time),
            str(try_except_runtime_error(lambda: cpu_temp.is_active)),
            str(cpu_temp.max_temp),
            str(cpu_temp.min_temp),
            str(cpu_temp.pin_factory),
            str(cpu_temp.sensor_file),
            str(try_except_runtime_error(lambda: cpu_temp.temperature)),
            str(cpu_temp.threshold),
            str(try_except_runtime_error(lambda: cpu_temp.value)),
            str(cpu_temp.when_activated),
            str(cpu_temp.when_deactivated)
        ]
        with GPIOZERO_DATA_FILE.open("a") as f:
            f.write(DELIMITER.join(row) + os.linesep)
    logger.debug("Event is set - stopping gpiozero capture")

def run_sense_hat_data_collection(event: EventT) -> None:
    logger.debug("sense hat process started")
    sense_hat: SenseHat = SenseHat()

    header: list[str] = [
        "datetime",
        "red", 
        "green", 
        "blue", 
        "clear", 
        "gain",
        "red_raw", 
        "green_raw", 
        "blue_raw", 
        "clear_raw",
        "integration_time", 
        "integration_cycles",
        "temperature_from_humidity",
        "temperature_from_pressure",
        "temp",
        "pressure",
        "temperature",
        "humidity",
        "compass",
        "accelerometer_roll",
        "accelerometer_pitch",
        "accelerometer_yaw",
        "gyroscope_roll",
        "gyroscope_pitch",
        "gyroscope_yaw",
        "orientation_roll",
        "orientation_pitch",
        "orientation_yaw",
        "orientation_radians_roll",
        "orientation_radians_pitch",
        "orientation_radians_yaw",
        "compass_raw_x",
        "compass_raw_y",
        "compass_raw_z",
        "accelerometer_raw_x",
        "accelerometer_raw_y",
        "accelerometer_raw_z",
        "gyroscope_raw_x",
        "gyroscope_raw_y",
        "gyroscope_raw_z"
    ]

    if not SENSE_HAT_DATA_FILE.exists():
        logger.debug(f"Creating {SENSE_HAT_DATA_FILE}...")
        SENSE_HAT_DATA_FILE.write_text(DELIMITER.join(header) + os.linesep)

    logger.info("Starting sense hat capture loop")
    while not event.is_set():

        compass_raw = sense_hat.compass_raw
        accelerometer = sense_hat.accelerometer
        accelerometer_raw = sense_hat.accelerometer_raw
        gyroscope = sense_hat.gyroscope
        gyroscope_raw = sense_hat.gyroscope_raw
        orientation = sense_hat.orientation
        orientation_radians = sense_hat.orientation_radians

        row: list[str] = [
            datetime.now().isoformat(),
            str(sense_hat.colour.red),
            str(sense_hat.colour.green),
            str(sense_hat.colour.blue),
            str(sense_hat.colour.clear),
            str(sense_hat.colour.gain),
            str(sense_hat.colour.red_raw),
            str(sense_hat.colour.green_raw),
            str(sense_hat.colour.blue_raw),
            str(sense_hat.colour.clear_raw),
            str(sense_hat.colour.integration_time),
            str(sense_hat.colour.integration_cycles),
            str(sense_hat.get_temperature_from_humidity()),
            str(sense_hat.get_temperature_from_pressure()),
            str(sense_hat.temp),
            str(sense_hat.pressure),
            str(sense_hat.temperature),
            str(sense_hat.humidity),
            str(sense_hat.compass),
            str(accelerometer["roll"]),
            str(accelerometer["pitch"]),
            str(accelerometer["yaw"]),
            str(gyroscope["roll"]),
            str(gyroscope["pitch"]),
            str(gyroscope["yaw"]),
            str(orientation["roll"]),
            str(orientation["pitch"]),
            str(orientation["yaw"]),
            str(orientation_radians["roll"]),
            str(orientation_radians["pitch"]),
            str(orientation_radians["yaw"]),
            str(compass_raw["x"]),
            str(compass_raw["y"]),
            str(compass_raw["z"]),
            str(accelerometer_raw["x"]),
            str(accelerometer_raw["y"]),
            str(accelerometer_raw["z"]),
            str(gyroscope_raw["x"]),
            str(gyroscope_raw["y"]),
            str(gyroscope_raw["z"]),
        ]

        with SENSE_HAT_DATA_FILE.open("a") as f:
            f.write(DELIMITER.join(row) + os.linesep)
    logger.debug("Event is set - stopping sense hat capture")

def main():
    start_time: datetime = datetime.now()
    logger.info(f"Start time: {start_time.isoformat()}")

    if not IMAGES_DIR.exists():
        logger.debug(f"Creating {IMAGES_DIR} and parents")
        IMAGES_DIR.mkdir(parents=True)

    children: list[Process] = []
    try:
        event: EventT = Event()
        camera_process: Process = Process(
                target=run_camera, args=(event,))
        children.append(camera_process)
        logger.debug("Spawned camera process")
        sense_hat_data_collection_process: Process = Process(
            target=run_sense_hat_data_collection, args=(event,))
        children.append(sense_hat_data_collection_process)
        logger.debug("Spawned sense hat process")
        gpiozero_data_collection_process: Process = Process(
            target=run_gpiozero_data_collection, args=(event,))
        children.append(gpiozero_data_collection_process)
        logger.debug("Spawned gpiozero process")

        # start the processes
        for child in children: child.start()

        sleep_seconds: int = ((NUM_MINUTES - 1) * MINUTES + 30)
        logger.debug(f"Main process is sleeping for {sleep_seconds} seconds")
        time.sleep(sleep_seconds)

        logger.debug("Main process awoken")
        logger.debug(f"{sleep_seconds} minutes have elapsed.")

        # wake in the last 30 seconds and wait until 15 seconds left
        while datetime.now() < (start_time + 
            timedelta(seconds=(NUM_MINUTES*MINUTES) - 15)):
            pass

        # in the last 15 seconds - send kill signal to processes
        # by setting the event
        logger.info("Main process setting event")
        event.set()

        # Wait until each process has finished
        for child in children: child.join()
        logger.debug("Waiting for child processes to complete")

    except InterruptedError:
        logger.debug("Interrupt received - sending kill signal to child processes")
        for child in children: child.kill()
        # wait a couple of seconds for the processes to deal with the kill
        # signal
        time.sleep(5)
        for child in children:
            if child.exitcode is None:
                logger.debug(f"process {child.name} not stopped - " + 
                             "sending terminate signal")
                # escalate if they have ignored the signal
                child.terminate()
    finally:
        logger.debug("Exiting")

if __name__ == "__main__":
    main()

