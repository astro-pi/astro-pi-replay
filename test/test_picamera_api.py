import io
import itertools
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

import exif
import numpy as np
import pytest
from colorzero import Color
from PIL import Image

import test_utils
from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.picamera.array import PiRGBArray
from astro_pi_executor.picamera.camera import PiCameraAdapter
from astro_pi_executor.picamera.streams import PiCameraCircularIO
from astro_pi_executor.resources import get_replay_sequence_dir

logger = logging.getLogger(__name__)

# 4 formats are unsupported directly by PIL for now FIXME
# formats: list[str] = ['jpg', 'jpeg', 'png', 'gif', 'bmp',
#                        'yuv', 'rgb', 'rgba', 'bgr', 'bgra', 'raw']
photo_formats: list[str] = ["jpg", "jpeg", "png", "gif", "bmp", "rgb", "rgba"]
video_formats: list[str] = ["h264", "mjpeg", "yuv", "rgb", "rgba", "bgr", "bgra"]

###########
# Fixtures
###########


@pytest.fixture(scope="module")
def executor():
    executor = AstroPiExecutor()
    executor.no_wait = True
    yield executor


########
# TESTS
########


@pytest.mark.parametrize("format", photo_formats)
def test_replay_capture_should_replay_captured_photos_in_given_format(
    tmp_path: Path, executor: AstroPiExecutor, format: str
):
    expected_file_path: Path = tmp_path / f"example.{format}"
    cam = PiCameraAdapter(executor)
    cam.capture(str(expected_file_path))

    assert expected_file_path.exists()
    # TODO add content assert.


def test_replay_capture_should_replay_captured_photos_in_given_size(
    tmp_path: Path, executor: AstroPiExecutor
):
    expected_file_path: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter(executor)
    cam.capture(str(expected_file_path), resize=(800, 600))

    assert expected_file_path.exists()
    # TODO add content assert
    im = Image.open(expected_file_path)
    assert im.size == (800, 600)


def test_replay_capture_should_replay_captured_photos_in_given_file(
    tmp_path: Path, executor: AstroPiExecutor
):
    file_path: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter(executor)
    with file_path.open("wb") as f:
        cam.capture(f, format="jpeg")

    assert file_path.exists()
    # TODO assert on content


def test_replay_capture_to_numpy_array():
    cam = PiCameraAdapter()
    width, height = cam.resolution
    output = np.zeros((height, width, 3), dtype=np.uint8)
    zeros = output.copy()
    cam.capture(output, "bgr")
    assert not np.array_equal(output, zeros)
    # TODO assert on content.


# FIXME
def test_replay_capture_to_PiRGBArray(executor: AstroPiExecutor):
    cam = PiCameraAdapter(executor)
    width, height = cam.resolution
    stream = PiRGBArray(cam)
    zeros = np.zeros((height, width, 3), dtype=np.uint8)
    cam.capture(stream, format="rgb", use_video_port=True)
    assert stream.array.shape == (height, width, 3)
    assert not np.array_equal(stream.array, zeros)
    # TODO assert on content


def test_replay_capture_with_annotations(tmp_path: Path, executor: AstroPiExecutor):
    file: Path = tmp_path / "example.jpeg"
    cam = PiCameraAdapter(executor)
    cam.annotate_text = os.linesep.join(["foo", "bar"])
    cam.annotate_foreground = Color("red")
    cam.annotate_background = Color("white")
    cam.annotate_frame_num = True
    cam.capture(str(file))

    # TODO patch the image used so it's just the text being drawn
    assert file.exists()
    # TODO assert on content


def test_replay_capture_sets_exif_tags(tmp_path: Path, executor: AstroPiExecutor):
    file: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter(executor)
    now = datetime.now()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        cam.capture(str(file))

    with file.open("rb") as f:
        img = exif.Image(f)
    now_formatted: str = now.strftime("%Y:%m:%d %H:%M:%S")
    assert img.datetime_digitized == now_formatted
    assert img.datetime_original == now_formatted
    assert img.datetime == now_formatted


def test_replay_when_capture_called_repeatedly_should_return_different_photos(
    tmp_path: Path, executor: AstroPiExecutor
):
    with test_utils.patch_photo_indices(indices=[0, 1]):
        cam = PiCameraAdapter(executor)
        prev: Optional[np.ndarray] = None
        for i in range(2):
            image_path: Path = tmp_path / f"photo_{i}.jpg"
            cam.capture(str(image_path))

            assert image_path.exists()
            np_image = np.array(Image.open(image_path))
            if prev is not None:
                assert not np.array_equal(
                    np_image, prev
                ), "should return different photos"
            prev = np_image


def test_replay_capture_continuous_replays_yields_filenames(
    tmp_path: Path, executor: AstroPiExecutor
):
    cam = PiCameraAdapter(executor)
    output: Path = tmp_path / "img"
    output.mkdir()
    with test_utils.patch_photo_indices(indices=[0, 1, 2]):
        filenames: list[str] = list(
            itertools.islice(
                cam.capture_continuous(
                    str(output) + "/{timestamp:%H%M%S}-{counter:03d}.jpg"
                ),
                3,
            )
        )
    assert len(filenames) == 3
    for filename in os.listdir(output):
        assert filename in os.listdir(output)
    # TODO assert on content


def test_replay_capture_continuous_replays_into_streams(executor: AstroPiExecutor):
    cam = PiCameraAdapter(executor)
    stream = io.BytesIO()
    with test_utils.patch_photo_indices(indices=[0, 1, 2]):
        for _ in itertools.islice(cam.capture_continuous(stream, format="rgb"), 3):
            pass

    # Calculate the expected size
    with (get_replay_sequence_dir() / "metadata.json").open("r") as f:
        metadata: dict[str, Any] = json.loads(f.read())
    resolution: tuple[int, int] = metadata["resolution_x"], metadata["resolution_y"]

    bytes_per_image: int = np.prod((*resolution, 3)).item()
    expected_num_bytes: int = bytes_per_image * 3
    assert len(stream.getbuffer()) == expected_num_bytes
    # TODO assert on content


def test_replay_capture_sequence_with_filenames(
    tmp_path: Path, executor: AstroPiExecutor
):
    cam = PiCameraAdapter(executor)
    output: Path = tmp_path / "img"
    output.mkdir()
    images: list[str] = ["image1.jpg", "image2.jpg", "image3.jpg"]

    with test_utils.patch_photo_indices(indices=[0, 1, 2]):  # FIXME
        cam.capture_sequence(list(map(lambda x: str(output / x), images)))

    assert len(os.listdir(output)) == 3
    for image in images:
        assert image in os.listdir(output)
    # TODO assert on content


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
@pytest.mark.parametrize("format", video_formats)
def test_replay_start_recording_supports_all_video_formats(tmp_path: Path, format: str):
    cam = PiCameraAdapter()
    output = tmp_path / f"example.{format}"
    # TODO make deterministic
    cam.start_recording(str(output), format=format)
    cam.wait_recording(1)
    cam.stop_recording()
    assert output.exists()
    # TODO assert on content


# @pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
@pytest.mark.skip(reason="Not yet implemented")
def test_replay_start_recording_resizes():
    pass


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
@pytest.mark.parametrize("format", video_formats)
def test_replay_start_recording_into_stream(format: str):
    # TODO make deterministic
    # executor = AstroPiExecutor()
    # # TODO create an astro pi executor fixture
    # executor._state._start_time = datetime.now()
    cam = PiCameraAdapter()
    stream = io.BytesIO()
    # TODO make the ffmpeg process be quiet!
    cam.start_recording(stream, format=format, quality=23)
    cam.wait_recording(1)
    cam.stop_recording()
    assert len(stream.getbuffer()) > 0
    # TODO assert on content


# @pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
@pytest.mark.skip(reason="Not yet implemented")
def test_replay_start_recording_writes_text_annotations():
    pass


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_replay_split_recording_creates_multiple_files(tmp_path: Path):
    cam = PiCameraAdapter()
    # TODO make deterministic
    cam.start_recording(str(tmp_path / "1.h264"))
    cam.wait_recording(1)
    cam.split_recording(str(tmp_path / "2.h264"))
    cam.wait_recording(1)
    cam.stop_recording()
    for filename in ["1.h264", "2.h264"]:
        assert filename in os.listdir(tmp_path)
        # TODO assert on content


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_replay_records_to_a_circular_stream(tmp_path: Path):
    # TODO make deterministic
    cam = PiCameraAdapter()
    bytes_per_frame: int = cam.resolution[0] * cam.resolution[1] * 3

    # TODO make the recording consumer silent and move it

    stream = PiCameraCircularIO(cam, size=bytes_per_frame)
    cam.start_recording(stream, format="rgb")
    cam.wait_recording(1)
    cam.stop_recording()

    assert len(stream.getvalue()) == bytes_per_frame
    # TODO assert on content

    copied_output: Path = tmp_path / "example.rgb"
    stream.copy_to(str(copied_output))
    with copied_output.open("rb") as f:
        assert len(f.read()) == bytes_per_frame


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_replay_record_sequence(tmp_path: Path):
    cam = PiCameraAdapter()
    # TODO make deterministic
    outputs: list[str] = list(map(lambda x: str(tmp_path / x), ["1.h264", "2.h264"]))
    for _ in cam.record_sequence(outputs):
        cam.wait_recording(1)
    cam.stop_recording()
    for output in outputs:
        assert Path(output).exists()
        # TODO assert on content


@pytest.mark.skip(reason="GUI test")
def test_start_preview_shows_preview():
    # tkinter test
    pass


@pytest.mark.skip(reason="Not yet implemented")
def test_start_preview_shows_annotations_if_present():
    pass


@pytest.mark.skip(reason="Not yet implemented")
def test_start_preview_displays_overlays():
    # test camera.add_overlay(pad.tobytes(), size=img.size)
    # test camera.remove_overlay
    pass


@pytest.mark.skip(reason="Not yet implemented")
def test_frames_returns_frame_info():
    pass


@pytest.mark.skip(reason="Not yet implemented")
def test_camera_adapter_as_content_manager_does_not_leak_resource():
    pass


def test_picamera_adapter_has_all_expected_methods():
    cam = PiCameraAdapter()
    with test_utils.get_test_resource("picamera_interface.json").open() as f:
        expected_picamera_interface: dict[str, list[str]] = json.loads(f.read())

    for method in filter(
        lambda x: not x.startswith("_"), expected_picamera_interface["callables"]
    ):
        assert hasattr(cam, method)
        func = getattr(cam, method)
        assert callable(func), f"Expecting {method} to be callable"


def test_picamera_adapter_has_all_expected_attrs():
    cam = PiCameraAdapter()
    with test_utils.get_test_resource("picamera_interface.json").open() as f:
        expected_picamera_interface: dict[str, list[str]] = json.loads(f.read())
    # led is not a readable attribute, and frame only works during video playback
    for attr in filter(
        lambda x: not x.startswith("_") and x not in ["frame", "led"],
        expected_picamera_interface["attrs"],
    ):
        assert hasattr(cam, attr), f"Expecting PiCameraAdapter to have {attr}"


# TODO test custom objects e.g. renderers, streams, encoders?

# TODO test preview processes close / resource closure...
