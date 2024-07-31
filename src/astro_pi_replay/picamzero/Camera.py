import functools
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Optional

from PIL import Image
import numpy as np

from astro_pi_replay.exception import AstroPiReplayException, AstroPiReplayRuntimeError
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import get_replay_sequence_dir
from astro_pi_replay.resources.utils import get_video

logger = logging.getLogger(__name__)


def run(cmd: list[str], **kwargs):
    cmd_string: str = " ".join(cmd)

    logger.debug(f"Executing {cmd_string}")
    proc = subprocess.run(cmd, text=True, capture_output=True, **kwargs)  # nosec B603
    if proc.returncode != 0:
        raise AstroPiReplayRuntimeError(
            os.linesep.join(["Encountered error:", proc.stderr])
        )


def CameraAdapter(maybe_executor: Optional[AstroPiExecutor] = None, *args, **kwargs):
    executor: AstroPiExecutor
    if maybe_executor is None:
        executor = AstroPiExecutor()
    else:
        executor = maybe_executor

    class _CameraAdapter:
        _SUPPORTED_VIDEO_FORMATS: list[str] = ["mp4"]
        _SUPPORTED_PHOTO_FORMATS: list[str] = ["jpg", "jpeg", "png"]

        def __init__(self):
            """
            Creates a Camera object based on a Picamera2 object

            :param Picamera2 pc2:
                An internal Picamera2 object. This can be accessed by
                advanced users who want to use methods we have not
                wrapped from the Picamera2 library.
            """
            self._recording: Optional[str] = None
            self._recording_start: Optional[datetime] = None
            # try:
            #     self.pc2 = Picamera2()
            # except RuntimeError:
            #     print("Could not connect to the camera!")
            #     print("Please check all connections")
            #     exit()
            #
            ## Camera
            #self.hflip = False
            #self.vflip = False

            ## Annotation
            #self._text = None
            #self._text_properties = {
            #    "font": utils.check_font_in_dict("plain1"),
            #    "color": (255, 255, 255, 255),
            #    "position": (0, 0),
            #    "scale": 3,
            #    "thickness": 3,
            #    "bgcolor": None,
            #    "position": (0, 0),
            #}

            #self.pc2.start()
            self._preview_size: tuple[int, int] = (4056,3040)
            self._still_size: tuple[int, int] = (4056,3040)
            self._video_size: tuple[int, int] = (4056,3040)
            self._brightness: float = 0.
            self._contrast: float = 1.
            self._exposure: Optional[int] = None
            self._gain: Optional[float] = None
            self._white_balance: int = 0
            self._greyscale: bool = False


        # PRIVATE METHODS
        # ----------------------------------

        def _create_video(
            self, final_filename: str, start: datetime, duration: float
        ) -> None:
            # calculate the time since the replay started
            delta: timedelta = start - executor._state._start_time
            video: Path = get_video()
            cmd: list[str] = [
                "ffmpeg",
                "-ss",
                str(delta.total_seconds()),
                "-to",
                str(delta.total_seconds() + duration),
                # input
                "-i",
                str(video),
                "-c",
                "copy",
                str(final_filename),
            ]
            logger.debug(" ".join(cmd))
            run(cmd)

        def _detect_format(
            self,
            filename: Optional[str],
            allowed_formats: list[str],
            default_format: str,
        ) -> str:
            if filename is None:
                raise RuntimeError("Please specify a filename")

            split_filename = filename.split(".")
            last = split_filename[-1]
            if len(split_filename) == 1:
                final_filename = f"{last}.{default_format}"
            elif last == default_format:
                final_filename = filename
            else:
                raise RuntimeError(
                    f"Unsupported format: {last}. "
                    + "Supported formats are: "
                    + f"'{', '.join(allowed_formats)}'"
                )

            return final_filename


        def log_warning(self):
            logger.warning(
                "Setting this attribute has no effect when running " +
                "using the replay tool, since the data has been collected " + 
                "already and is just being replayed. It will have the desired " + 
                "effect when run on the ISS")

        # ----------------------------------
        # PROPERTIES
        # ----------------------------------
        @property
        def preview_size(self) -> tuple[int,int]:
            return self._preview_size
    
        @preview_size.setter
        def preview_size(self, size: tuple[int, int]):
            self.log_warning()
            self._preview_size = size
    
        @property
        def still_size(self) -> tuple[int, int]:
            return self._still_size
    
        @still_size.setter
        def still_size(self, size: tuple[int,int]):
            self.log_warning()
            self._still_size = size
    
        @property
        def video_size(self) -> tuple[int,int]:
            return self._video_size
    
        @video_size.setter
        def video_size(self, size: tuple[int, int]):
            self.log_warning()
            self._video_size = size
    
        # Brightness
        @property
        def brightness(self) -> float:
            """
            Get the brightness
    
            :return float:
            Brightness value between -1.0 and 1.0
            """
            return self._brightness
    
        @brightness.setter
        def brightness(self, bvalue: float):
            """
            Set the brightness
    
            :param float bvalue:
                Floating point number between -1.0 and 1.0
            """
            self.log_warning()
            self._brightness = bvalue
    
        # Contrast
        @property
        def contrast(self) -> float:
            """
            Get the contrast
    
            :return float:
                Contrast value between 0.0 and 32.0
            """
            return self._contrast
    
        @contrast.setter
        def contrast(self, cvalue: float):
            """
            Set the contrast
    
            :param float cvalue:
                Floating point number between 0.0 and 32.0
                Normal value is 1.0
            """
            self.log_warning()
            self._contrast = cvalue
    
        @property
        def exposure(self) -> Optional[int]:
            """
            Get the exposure
    
            :returns int:
                Exposure value (max and min depend on mode)
            """
            return self._exposure
    
        @exposure.setter
        def exposure(self, etime: int):
            """
            Set the exposure
    
            :param int etime:
                The exposure time (max and min depend on mode)
            """
            self.log_warning()
            self._exposure = etime
    
        @property
        def gain(self) -> Optional[float]:
            """
            Get the gain
    
            :returns float:
                Gain value (max and min depend on mode)
            """
            return self._gain
    
        @gain.setter
        def gain(self, gvalue: float):
            """
            Set the analogue gain
    
            :param float gvalue:
                The analogue gain (max and min depend on mode)
            """
            self.log_warning()
            self._gain = gvalue
    
        @property
        def white_balance(self) -> str:
            """
            Get the white balance mode
    
            :return str:
                The selected white balance mode as a string
            """
            return self._white_balance
    
        @white_balance.setter
        def white_balance(self, wbmode: str):
            """
            Set the white balance mode
    
            :param str wbmode:
                A white balance mode from the allowed list
                (at present, Custom is not allowed)
            """
            self.log_warning()
            self._white_balance = wbmode
    
        @property
        def greyscale(self) -> bool:
            return self._greyscale
    
        @greyscale.setter
        def greyscale(self, on: bool) -> None:
            """
            Apply greyscale to the preview and image
            You have to call this _after_ the preview has started or it wont apply
            Does NOT apply to video
    
            :param bool on:
                Whether greyscale should be on
            """
            self.log_warning()
            self._greyscale = on

        # ----------------------------------
        # METHODS
        # ----------------------------------

        def flip_camera(self, vflip=False, hflip=False):
            """
            Flip the image horizontally or vertically
            """
            self.log_warning()
            self.vflip = vflip
            self.hflip = hflip
    
        def start_preview(self):
            """
            Show a preview of the camera
            """
            self.log_warning()
    
        def stop_preview(self):
            """
            Stop the preview
            """
            pass
    
        #def annotate(
        #    self,
        #    text="Default Text",
        #    font="plain1",
        #    color=(255, 255, 255, 255),
        #    scale=3,
        #    thickness=3,
        #    position=(0, 0),
        #    bgcolor=None,
        #):
        #    """
        #    Set a text overlay on the preview and on images
        #    """
        #    self._text = text
    
        #    font = utils.check_font_in_dict(font)
        #    color = utils.convert_color(color)
    
        #    self._text_properties = {
        #        "font": font,
        #        "color": color,
        #        "scale": scale,
        #        "thickness": thickness,
        #        "bgcolor": bgcolor,
        #        "position": position,
        #    }
    
        #    def annotation_callback(request):
        #        """
        #        Annotate before taking a photo etc.
        #        """
        #        text_prop = self._text_properties
        #        # Create the background
        #        x, y = text_prop["position"]
        #        text_size, _ = cv2.getTextSize(
        #            text, text_prop["font"], text_prop["scale"], text_prop["thickness"]
        #        )
        #        text_w, text_h = text_size
    
        #        with MappedArray(request, "main") as m:
        #            if text_prop["bgcolor"] is not None:
        #                cv2.rectangle(
        #                    m.array,
        #                    text_prop["position"],
        #                    (x + text_w, y + text_h),
        #                    text_prop["bgcolor"],
        #                    -1,
        #                )
        #            cv2.putText(
        #                m.array,
        #                self._text,
        #                (x, y + text_h + text_prop["scale"] - 4),
        #                text_prop["font"],
        #                text_prop["scale"],
        #                text_prop["color"],
        #                text_prop["thickness"],
        #            )
    
        #    # Add the annotation as a callback when any pics are taken
        #    self.pc2.pre_callback = annotation_callback
    
        ## Image overlay
        #def add_image_overlay(self, image_path, position=(0, 0), transparency=0.5):
        #    overlay_img, position, transparency = utils.check_image_overlay(
        #        image_path, position, transparency
        #    )
    
        #    # Ensure the image is in BGRA format (with alpha channel)
        #    if overlay_img.shape[2] == 3:  # If no alpha channel, add one
        #        overlay_img = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2BGRA)
    
        #    overlay_h, overlay_w = overlay_img.shape[:2]
    
        #    def overlay_callback(request):
        #        with MappedArray(request, "main") as m:
        #            frame_h, frame_w = m.array.shape[:2]
    
        #            x, y = position
    
        #            # Ensure the region we overlay onto matches the overlay image's size
        #            roi = m.array[y : y + overlay_h, x : x + overlay_w]
    
        #            # Combine the images
        #            overlay_img_resized = cv2.resize(
        #                overlay_img, (roi.shape[1], roi.shape[0])
        #            )
        #            overlay_alpha = overlay_img_resized[:, :, 3] / 255.0 * transparency
        #            background_alpha = 1.0 - overlay_alpha
    
        #            for c in range(0, 3):
        #                roi[:, :, c] = (
        #                    overlay_alpha * overlay_img_resized[:, :, c]
        #                    + background_alpha * roi[:, :, c]
        #                )
    
        #    # Add the overlay as a callback when any pics are taken or preview is shown
        #    self.pc2.pre_callback = overlay_callback
    
        def take_video_and_still(
                self, 
                filename: Optional[str]=None, 
                duration:int=20,
                still_interval: int=4):
            """
            Take video for <duration> and take a still every <interval> seconds?
            """
            if filename is None:
                raise RuntimeError("Must provide filename")
            split_filename = filename.split(".")
            if len(split_filename) > 1:
                raise RuntimeError("Can only specify basename")

            self.start_recording(filename)
            i: int = 1
            while (
                self._recording_start is not None
                and (datetime.now() - self._recording_start).total_seconds() < duration
            ):
                before_photo: datetime = datetime.now()
                self.take_photo(f"{filename}-{i}.jpg")
                i += 1
                after_photo: datetime = datetime.now()
                still_duration = (after_photo - before_photo).total_seconds()
                if still_duration > still_interval:
                    logger.warning(
                        "Image capture took longer than "
                        + "still interval specified - this happens "
                        + "the replay tool replays old data "
                        + "which cannot be changed."
                    )
                video_duration = (after_photo - self._recording_start).total_seconds()
                seconds_until_video_finished = duration - video_duration
                if seconds_until_video_finished < still_interval:
                    sleep(still_interval - seconds_until_video_finished)
                elif still_interval > still_duration:
                    sleep(still_interval - still_duration)

            self.stop_recording()

        def capture_array(self) -> np.ndarray:
            """
            Takes a photo at full resolution and saves it as an
            (RGB) numpy array.
    
            This can be used in further processing using libraries
            like opencv.
    
            :return np.ndarray:
                A full resolution image as a raw RGB numpy array
            """

            name: str = str(
                executor._replay_next(
                    str(get_replay_sequence_dir() / "photos" / "photo_index.csv"),
                    "datetime",
                    ["name"],
                    allow_interpolation=False,
                )
            )

            image_path: Path = get_replay_sequence_dir() / "photos" / name
            im = Image.open(image_path)
            return np.asarray(im)

        def take_photo(self, filename=None, gps_coordinates=None):
            """
            Takes a jpeg image using the camera
            :param str filename: The name of the file to save the photo.
            If it doesn't end with '.jpg', the ending '.jpg' is added.
            :param tuple[tuple[float, float, float, float],
                         tuple[float, float, float, float]] gps_coordinate:
            The gps coordinates to be associated
            with the image, specified as a (latitude, longitude) tuple where
            both latitude and longitude are themselves tuples of the
            form (sign, degrees, minutes, seconds). This format
            can be generated from the skyfield library's signed_dms
            function.
            """
            final_filename = self._detect_format(
                filename,
                self._SUPPORTED_PHOTO_FORMATS,
                self._SUPPORTED_PHOTO_FORMATS[0],
            )

            name: str = str(
                executor._replay_next(
                    str(get_replay_sequence_dir() / "photos" / "photo_index.csv"),
                    "datetime",
                    ["name"],
                    allow_interpolation=False,
                )
            )
            #    # Capture the image
            #    kwargs: dict = {}
            #    if gps_coordinates is not None:
            #        kwargs["exif_data"] = utils.signed_dms_coordinates_to_exif_dict(
            #            gps_coordinates
            #        )
            image_path: Path = get_replay_sequence_dir() / "photos" / name
            im = Image.open(image_path)
            im.save(final_filename)
            return final_filename
    
        def capture_image(self, filename: Optional[str]=None):
            return self.take_photo(filename)
    
        def capture_sequence(
            self, 
            filename: Optional[str] = None,
            num_images: int = 10,
            interval: float = 0.01,
            make_video: bool = False,
        ):
            """
            Take a series of <num_images> and save them as
            <filename> with auto-number, also set the interval between
            """
            if filename is None:
                raise RuntimeError("Please specify a filename")
            split_filename = filename.split(".")
            last = split_filename[-1]
            if len(split_filename) == 1:
                final_format = "jpg"
                final_filename = filename
            elif last in self._SUPPORTED_PHOTO_FORMATS:
                final_format = last
                final_filename = "".join(split_filename[:-1])
            else:
                raise RuntimeError(
                    f"Unknown format '{last}'. "
                    + "Valid formats are '"
                    + ", ".join(self._SUPPORTED_PHOTO_FORMATS)
                    + "'"
                )

            start_time: datetime = datetime.now()
            for i in range(num_images):
                name = f"{final_filename}-{i+1}.{final_format}"
                # the take_photo method sleeps until the next
                # frame is available
                self.take_photo(name)
                time_after = datetime.now()
                delta = (time_after - start_time).total_seconds()
                if delta > interval:
                    logger.warning(
                        "Slept longer than interval because "
                        + "the interval between photos from the "
                        + "replayed dataset is longer. On the ISS, "
                        + "the actual interval may be closer to "
                        + "the value you have specified."
                    )
                else:
                    remainder = interval - delta
                    logger.debug("Sleeping an additional " + f"{remainder} seconds")
                    sleep(remainder)

            if make_video:
                if not executor._has_ffmpeg:
                    raise AstroPiReplayException("Please install ffmpeg to make videos")
                cmd: list[str] = [
                    "ffmpeg",
                    "-framerate",
                    "1",
                    "-i",
                    f"{final_filename}-%d.{final_format}",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    f"{final_filename}.mp4",
                ]
                cmd_as_string: str = " ".join(cmd)
                logger.debug(f"Running {cmd_as_string}")
                run(cmd)
    
        def record_video(self, 
                         filename: Optional[str] = None, 
                         duration: int = 5):
            """
            Record a video
            """
            start_time: datetime = datetime.now()
            final_filename: str = self._detect_format(
                filename,
                self._SUPPORTED_VIDEO_FORMATS,
                self._SUPPORTED_VIDEO_FORMATS[0],
            )

            if not executor._has_ffmpeg:
                raise AstroPiReplayException(
                    "Please install ffmpeg to capture videos " + "using the replay tool"
                )

            video: Path = get_video()

            # calculate the time since the replay started
            delta: timedelta = datetime.now() - executor._state._start_time
            cmd: list[str] = [
                "ffmpeg",
                "-ss",
                str(delta.total_seconds()),
                "-to",
                str(delta.total_seconds() + duration),
                # input
                "-i",
                str(video),
                "-c",
                "copy",
                str(final_filename),
            ]
            logger.debug(" ".join(cmd))
            run(cmd)
            elapsed: float = (datetime.now() - start_time).total_seconds()
            remainder: float = duration - elapsed
            if remainder > 0:
                sleep(remainder)

    
        def start_recording(self, 
                            filename: Optional[str]=None, 
                            preview: bool =False):
            """
            Record a video of undefined length
            """
            if self._recording or self._recording_start:
                raise RuntimeError("Already recording")
            self._recording = self._detect_format(
                filename,
                self._SUPPORTED_VIDEO_FORMATS,
                self._SUPPORTED_VIDEO_FORMATS[0],
            )
            self._recording_start = datetime.now()

        def stop_recording(self):
            """
            Stop recording video
            """
            if not self._recording or not self._recording_start:
                raise RuntimeError("Recording not started")

            duration: float = (datetime.now() - self._recording_start).total_seconds()
            self._create_video(
                final_filename=self._recording,
                start=self._recording_start,
                duration=duration,
            )
            self._recording = None
            self._recording_start = None

    return _CameraAdapter(*args, **kwargs)
