import datetime
import itertools
import logging
import multiprocessing
import re
import subprocess
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator, Optional, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from astro_pi_executor.executor import (
    AstroPiExecutor,
    AstroPiExecutorException,
    AstroPiExecutorRuntimeError,
)
from astro_pi_executor.picamera.exc import (
    PiCameraError,
    PiCameraRuntimeError,
    PiCameraValueError,
)
from astro_pi_executor.picamera.exif import modify_exif_tags
from astro_pi_executor.picamera.frames import PiVideoFrame
from astro_pi_executor.picamera.picamera_public_api import PiCamera
from astro_pi_executor.picamera.preview import CameraPreview
from astro_pi_executor.picamera.renderers import PiOverlayRenderer, PiRenderer
from astro_pi_executor.resources import get_resource

logger = logging.getLogger(__name__)
photo_formats = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "yuv",
    "rgb",
    "rgba",
    "bgr",
    "bgra",
]
video_formats = ["h264", "mjpeg", "yuv", "rgb", "rgba", "bgr", "bgra"]

index_file: Path = get_resource("OrbitAz") / "photo_index.csv"


def PiCameraAdapter(executor: AstroPiExecutor = AstroPiExecutor()) -> PiCamera:
    class _PiCameraAdapter(PiCamera):
        _preview_proc: Optional[multiprocessing.Process] = None
        _recording_proc: Optional[subprocess.Popen[bytes]] = None
        _frame_counter: Iterator[int] = itertools.count(0)
        _preview: Optional[PiRenderer] = None

        # TODO
        def __enter__(self):
            pass

        def __exit__(self):
            # TODO remove zombie processes
            self.close()

        # TODO make this more elegant... perhaps use the close method instead :)
        def _teardown(self):
            """
            Close any lingering processes
            """
            for process in [self._preview_proc, self._recording_proc]:
                if process is not None and process.poll() is None:
                    process.terminate()

        def _annotatate_text_in_image(self, img: Image.Image, frame_num) -> None:
            """
            Annotates the image with the annotation text inplace.
            """
            font_path: Path = get_resource("Share_Tech_Mono/ShareTechMono-Regular.ttf")
            font = ImageFont.truetype(str(font_path), self.annotate_text_size)
            draw_context: ImageDraw.ImageDraw = ImageDraw.Draw(img)

            text = self.annotate_text
            if self.annotate_frame_num:
                text += "\n" + str(frame_num)

            bbox = draw_context.multiline_textbbox((0, 0), text, font=font)
            _, _, box_width, box_height = bbox

            img_width, img_height = img.size
            coordinate: tuple[int, int] = (round((img_width / 2) - (box_width / 2)), 20)

            if self.annotate_background is not None:
                coords_box = (
                    coordinate[0],
                    coordinate[1],
                    coordinate[0] + box_width,
                    coordinate[1] + box_height,
                )
                draw_context.rectangle(
                    coords_box, fill=tuple(self.annotate_background.rgb_bytes)
                )

            draw_context.multiline_text(
                coordinate,
                text,
                font=font,
                fill=tuple(self.annotate_foreground.rgb_bytes),
            )

        def add_overlay(
            self,
            source: BinaryIO,
            size: Optional[tuple[int, int]] = None,
            format: Optional[str] = None,
            **options,
        ) -> PiOverlayRenderer:
            overlay = PiOverlayRenderer(self, source, size, format, **options)
            self.overlays.append(overlay)
            return overlay

        def _detect_format(
            self,
            output: Union[str, BinaryIO, np.ndarray],
            format: Optional[str],
            allowed_formats: list[str] = photo_formats,
        ) -> tuple[Union[str, BinaryIO, np.ndarray], Optional[str]]:
            final_output: Union[str, BinaryIO, np.ndarray]
            final_format: Optional[str]

            if format is None and isinstance(output, str):
                split: list[str] = output.split(".")
                if len(split) < 2 or split[-1] not in photo_formats:
                    raise PiCameraValueError()
                final_output = ".".join(split[:-1])
                final_format = split[-1]
            elif format not in allowed_formats and isinstance(output, str):
                raise PiCameraValueError()
            elif format is not None and isinstance(output, str) and format == "jpeg":
                # change format so it appears to not overwrite the suffix
                # given in the filename
                if output.endswith(".jpg"):
                    final_format = "jpg"
                else:
                    final_format = format

                final_output = re.sub(r"\.jpg$", "", output)
                final_output = re.sub(r"\.jpeg$", "", final_output)
            elif format is not None and isinstance(output, str):
                final_output = re.sub(r"\." + format + r"$", "", output)
                final_format = format
            else:
                final_output = output
                final_format = format

            if (
                not isinstance(final_output, str)
                and not hasattr(final_output, "write")
                and final_format is None
            ):
                raise PiCameraValueError("Must specify a format")

            return final_output, final_format

        # TODO test file conversions...
        # @executor.picamera_replay()
        def capture(
            self,
            output: Union[str, BinaryIO, np.ndarray],
            format: Optional[str] = None,
            use_video_port: bool = False,
            resize: Optional[tuple[int, int]] = None,
            splitter_port: int = 0,
            bayer: bool = False,
            **options,
        ) -> None:
            final_output, final_format = self._detect_format(output, format)

            name: str = str(
                executor._replay_next(str(index_file), "datetime", ["name"])
            )

            image_path: Path = get_resource("OrbitAz") / name
            im = Image.open(image_path)

            # Conditionally add text annotation
            if len(self.annotate_text) > 0:
                matches = re.search(r"\d+", name)
                frame_num: int = (
                    next(self._frame_counter)
                    if matches is None
                    else int(matches.group())
                )
                self._annotatate_text_in_image(im, frame_num)

            if resize is not None:
                im = im.resize(resize)
            save_kwargs = {}
            if final_format in ["jpeg", "jpg"] and len(self.exif_tags.keys()) > 0:
                # exif tags are only supported for jpeg in the original picamera
                exif = modify_exif_tags(im.getexif(), self.exif_tags)
                save_kwargs["exif"] = exif

            if isinstance(final_output, str):
                logger.debug("Path output detected")
                im = im.save(f"{final_output}.{final_format}", **save_kwargs)
            elif isinstance(final_output, np.ndarray):
                # TODO only supported in "raw" formats
                # modifies the array in-place
                np_image = np.array(im)
                if final_format is not None and final_format.startswith("bgr"):
                    np_image[:, :, [0, 1, 2]] = np_image[
                        :, :, [2, 1, 0]
                    ]  # type: ignore
                final_output[...] = np_image
            elif (
                hasattr(final_output, "write")
                and callable(final_output.write)
                and format in ["rgb", "rgba", "bgr", "bgra"]
            ):
                final_output.write(im.tobytes())
                final_output.flush()  # TODO decide if this should be here?
            elif hasattr(final_output, "write") and callable(final_output.write):
                im = im.save(final_output, final_format=format, **save_kwargs)
            else:
                logger.debug("File-like output object detected")
                im = im.save(final_output, **save_kwargs)

        def capture_continuous(
            self,
            output: Union[str, BinaryIO, np.ndarray],
            format: Optional[str] = None,
            use_video_port: bool = False,
            resize: Optional[tuple[int, int]] = None,
            splitter_port: int = 0,
            burst: bool = False,
            bayer: bool = False,
            **options,
        ) -> Iterable:
            final_output, final_format = self._detect_format(output, format)
            counter: int = 1
            while True:
                if isinstance(final_output, str):
                    filename: str = final_output.format(
                        counter=counter, timestamp=datetime.datetime.now()
                    )
                    self.capture(
                        filename,
                        final_format,
                        use_video_port,
                        resize,
                        splitter_port,
                        bayer,
                        **options,
                    )
                    yield f"{filename}.{final_format}"
                else:
                    self.capture(
                        output,
                        format,
                        use_video_port,
                        resize,
                        splitter_port,
                        bayer,
                        **options,
                    )
                    yield output
                counter += 1

        def capture_sequence(
            self,
            outputs: Iterable[Union[str, BinaryIO, np.ndarray]],
            format: str = "jpeg",
            use_video_port: bool = False,
            resize: Optional[tuple[int, int]] = None,
            splitter_port: int = 0,
            burst: bool = False,
            bayer: bool = False,
            **options,
        ) -> None:
            for output in outputs:
                self.capture(
                    output, format, use_video_port, resize, splitter_port, bayer
                )

        @staticmethod  # TODO this is actually implemented in arrays.py
        def convert_image_to_yuv() -> np.ndarray:
            # for yuv: https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion
            W = (
                np.array(
                    [
                        [65.738, 129.057, 25.064],
                        [-37.945, -74.494, 112.439],
                        [112.439, -94.154, -18.285],
                    ]
                )
                / 256
            )
            rgb_img = np.array(Image.open("image1.jpg"))
            # Transforms each width x height rgb vectors in the image into the YUV
            # space by multiplying the W matrix and adding it to the bias.
            bias = np.array([16, 128, 128])
            yuv = bias + np.tensordot(rgb_img, W, ([2], [1]))
            return yuv

        @staticmethod
        def bayer(img: Image) -> np.ndarray:
            """
            Pseudo-inverse of de-mosaicing aka
            un-demosaicing...
            """
            rgb_array: np.ndarray = np.array(img, dtype=np.uint8)
            width, height, _ = rgb_array.shape

            # Uses RGGB pattern:
            #
            # GB
            # RG

            bayered = np.zeros((2 * width, 2 * height), dtype=np.uint8)

            # green (top row)
            bayered[::2, ::2, 1] = rgb_array[:, :, 1]
            # blue (top row)
            bayered[::2, 1::2, 2] = rgb_array[:, :, 2]
            # red (bottom row)
            bayered[1::2, ::2, 0] = rgb_array[:, :, 0]
            # green (bottom row)
            bayered[1::2, 1::2, 1] = rgb_array[:, :, 1]

            return bayered

        @staticmethod
        def bayer_to_raw(bayered_arr: np.ndarray) -> bytes:
            """
            To raw of Sony IMX219 (V2 module)
            """
            # numpy doesn't have 10-bit integers, so use 16bit
            # data = np.uint16

            # The first 32,768 bytes is the header, which
            # starts with 'BRCM' - so we'll just fill the
            # rest of the header with blanks for now (TODO inspect the raw data)
            #
            # the last 10,270,208 bytes are the data itself

            # packed as 10-bit numbers over 5 bytes:
            # byte 1 (b1): MSB     MSB-1 MSB-2   MSB-3 MSB-4 LSB+4 LSB+3 LSB+2
            # byte 2 (b2): MSB     MSB-1 MSB-2   MSB-3 MSB-4 LSB+4 LSB+3 LSB+2
            # byte 3 (b3): MSB     MSB-1 MSB-2   MSB-3 MSB-4 LSB+4 LSB+3 LSB+2
            # byte 4 (b4): MSB     MSB-1 MSB-2   MSB-3 MSB-4 LSB+4 LSB+3 LSB+2
            # byte 5:      b1LSB+1 b1LSB b2LSB+1 b2LSB ...

            # reshape = (2480, 4128)
            # crop = (2464, 4100)
            # data = np.zeros(reshape, dtype=np.uint8)

            # max number can be 1023 (2**10 - 1)

            return bytes()

        # TODO
        @property
        def frame(self) -> Optional[PiVideoFrame]:
            if not self.recording:
                raise PiCameraRuntimeError(
                    "Cannot query frame information " + "when camera is not recording"
                )
            return None

        # TODO
        def record_sequence(
            self,
            outputs: Iterable[Union[str, BinaryIO, np.ndarray]],
            format: str = "h264",
            resize: Optional[tuple[int, int]] = None,
            splitter_port: int = 1,
            **option,
        ) -> None:
            return super().record_sequence(
                outputs, format, resize, splitter_port, **option
            )

        # TODO
        def remove_overlay(self, overlay: PiOverlayRenderer) -> None:
            return super().remove_overlay(overlay)

        # TODO
        def split_recording(self, output):
            return super().split_recording(output)

        # TODO
        def start_preview(self, **options) -> PiRenderer:
            if self._preview_proc is None:
                preview: CameraPreview = CameraPreview(
                    str(get_resource("OrbitAz/OrbitAz.mp4"))
                )
                self._preview_proc = preview
                preview.start()
                renderer = PiRenderer(self)
                self._preview = renderer
                return renderer
            elif self.preview is not None:
                return self.preview
            else:
                raise AstroPiExecutorRuntimeError("Invalid State")

        def start_recording(
            self,
            output: Union[str, BinaryIO],
            format: Optional[str] = None,
            resize: Optional[tuple[int, int]] = None,
            splitter_port: int = 1,
            **options,
        ):
            if self._recording_proc is not None:
                raise PiCameraError("Recording already started")

            # Determine the format
            final_output, final_format = self._detect_format(
                output, format, allowed_formats=video_formats
            )

            if not self._has_ffmpeg:
                raise AstroPiExecutorException("Please install ffmpeg")

            video: Path = get_resource("OrbitAz/OrbitAz.h264")

            # TODO add annotations
            # TODO add overlays

            # Start streaming to the output in real-time

            # - untested on Windows...!!!!

            # TODO maybe want to not start from the beginning - depends on the time
            # (using the -ss) option
            # TODO check if numpy arrays should be supported
            command_args: list[str]
            if isinstance(output, str):
                command_args = [
                    "ffmpeg",
                    "-re",
                    "-i",
                    str(video),
                    f"{final_output}.{final_format}",
                ]
                logger.debug(" ".join(command_args))

                # non-blocking.
                self._recording_proc = subprocess.Popen(command_args)  # nosec B603

            else:
                # output is a file-like object so run directly
                if final_format is None:
                    # TODO to _detect_format
                    raise ValueError("Must specify format")
                command_args = [
                    "ffmpeg",
                    "-re",
                    "-i",
                    str(video),
                    "-f",
                    final_format,
                    "pipe:1",
                ]
                logger.debug(" ".join(command_args))
                self._recording_proc = subprocess.Popen(  # nosec B603
                    command_args, stdout=output
                )

            # TODO add tear-down method (probably on the executor obj)
            # to avoid zombie processes-event-driven?

        # TODO
        @property
        def preview(self) -> Optional[PiRenderer]:
            # # TODO add overlays
            return self._preview if self.previewing else None

        def stop_preview(self):
            if self._preview_proc is not None:
                self._preview_proc.terminate()
                self._preview_proc = None
                self._preview = None

        # TODO
        def stop_recording(self, splitter_port: int = 1) -> None:
            return super().stop_recording(splitter_port)

        @property
        def _has_ffmpeg(self) -> bool:
            try:
                subprocess.run(  # nosec B603, B607
                    ["ffmpeg", "-version"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except FileNotFoundError:
                logger.error("ffmpeg not found. Please install it.")
                return False

        @property
        def _has_ffprobe(self) -> bool:
            try:
                subprocess.run(  # nosec B603, B607
                    ["ffprobe", "-version"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except FileNotFoundError:
                logger.error("ffprobe not found. Please install it.")
                return False

    return _PiCameraAdapter()
