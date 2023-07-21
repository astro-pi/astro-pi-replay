import io
import itertools
import json
import logging
import os
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
from astro_pi_executor.resources import get_resource

logger = logging.getLogger(__name__)

# 4 formats are unsupported directly by PIL for now FIXME
# formats: list[str] = ['jpg', 'jpeg', 'png', 'gif', 'bmp',
#                        'yuv', 'rgb', 'rgba', 'bgr', 'bgra', 'raw']
formats: list[str] = ["jpg", "jpeg", "png", "gif", "bmp", "rgb", "rgba"]

########
# TESTS
########


@pytest.mark.parametrize("format", formats)
def test_replay_capture_should_replay_captured_photos_in_given_format(
    tmp_path: Path, format: str
):
    executor: AstroPiExecutor = AstroPiExecutor()
    expected_file_path: Path = tmp_path / f"example.{format}"
    cam = PiCameraAdapter(executor)
    cam.capture(str(expected_file_path))

    assert expected_file_path.exists()
    # TODO add content assert.


def test_replay_capture_should_replay_captured_photos_in_given_size(tmp_path: Path):
    executor: AstroPiExecutor = AstroPiExecutor()
    expected_file_path: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter(executor)
    cam.capture(str(expected_file_path), resize=(800, 600))

    assert expected_file_path.exists()
    # TODO add content assert
    im = Image.open(expected_file_path)
    assert im.size == (800, 600)


def test_replay_capture_should_replay_captured_photos_in_given_file(tmp_path: Path):
    executor: AstroPiExecutor = AstroPiExecutor()
    file_path: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter(executor)
    with file_path.open("wb") as f:
        cam.capture(f)

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
def test_replay_capture_to_PiRGBArray():
    cam = PiCameraAdapter()
    width, height = cam.resolution
    stream = PiRGBArray(cam)
    zeros = np.zeros((height, width, 3), dtype=np.uint8)
    cam.capture(stream, format="rgb", use_video_port=True)
    assert stream.array.shape == (height, width, 3)
    assert not np.array_equal(stream.array, zeros)
    # TODO assert on content


def test_replay_capture_with_annotations(tmp_path: Path):
    file: Path = tmp_path / "example.jpeg"
    cam = PiCameraAdapter()
    cam.annotate_text = os.linesep.join(["foo", "bar"])
    cam.annotate_foreground = Color("red")
    cam.annotate_background = Color("white")
    cam.annotate_frame_num = True
    cam.capture(str(file))

    # TODO patch the image used so it's just the text being drawn
    assert file.exists()
    # TODO assert on content


def test_replay_capture_sets_exif_tags(tmp_path: Path):
    file: Path = tmp_path / "example.jpg"
    cam = PiCameraAdapter()
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
    tmp_path: Path,
):
    with test_utils.patch_photo_indices(indices=[0, 1]):
        cam = PiCameraAdapter()
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


def test_replay_capture_continuous_replays_yields_filenames(tmp_path: Path):
    cam = PiCameraAdapter()
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


def test_replay_capture_continuous_replays_into_streams():
    cam = PiCameraAdapter()
    stream = io.BytesIO()
    with test_utils.patch_photo_indices(indices=[0, 1, 2]):
        for _ in itertools.islice(cam.capture_continuous(stream, format="rgb"), 3):
            pass

    # Calculate the expected size
    with get_resource("OrbitAz/metadata.json").open("r") as f:
        metadata: dict[str, Any] = json.loads(f.read())
    resolution: tuple[int, int] = metadata["resolution_x"], metadata["resolution_y"]

    bytes_per_image: int = np.prod((*resolution, 3)).item()
    expected_num_bytes: int = bytes_per_image * 3
    assert len(stream.getbuffer()) == expected_num_bytes
    # TODO assert on content


def test_replay_capture_sequence_with_filenames(tmp_path: Path):
    cam = PiCameraAdapter()
    output: Path = tmp_path / "img"
    output.mkdir()
    images: list[str] = ["image1.jpg", "image2.jpg", "image3.jpg"]

    with test_utils.patch_photo_indices(indices=[0, 1, 2]):  # FIXME
        cam.capture_sequence(list(map(lambda x: str(output / x), images)))

    assert len(os.listdir(output)) == 3
    for image in images:
        assert image in os.listdir(output)
    # TODO assert on content


def test_replay_start_recording(tmp_path: Path):
    cam = PiCameraAdapter()
    output = tmp_path / "example.h264"
    df = cam.start_recording(str(output), format="h264")
    print(df)
    # TODO
    pass


def test_picamera_adapter_has_all_expected_methods():
    cam = PiCameraAdapter()
    methods = []  # TODO
    for method in methods:
        assert hasattr(cam, method)
        func = getattr(cam, method)
        assert callable(func), f"Expecting {method} to be callable"


def test_picamera_adapter_has_all_expected_attrs():
    cam = PiCameraAdapter()
    attrs = []  # TODO
    for attr in attrs:
        assert hasattr(cam, attr), f"Expecting PiCameraAdapter to have {attr}"


# TODO test custom objects e.g. renderers, streams, encoders?

# TODO test camera.add_overlay(pad.tobytes(), size=img.size)

# TODO test the rest of the API! e.g. video, capture sequence, attributes, etc.
# TODO start_recording, wait_recording, stop_recording, split_recording
# TODO start_recording with text annotation
# TODO add annotation text to preview
# TODO test capture with PiCameraCircularIO (stream)
# TODO perhaps test preview calls tkinter?

# TODO test preview processes close
