import itertools
import logging
import os
import shutil
import subprocess
from pathlib import Path
from test import test_utils
from time import sleep
from typing import Optional
from unittest.mock import MagicMock, patch

import exif
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from astro_pi_replay.configuration import Configuration
from astro_pi_replay.exception import FfmpegNotInstalledException
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.picamzero.camera_adapter import CameraAdapter
from astro_pi_replay.resources import get_replay_sequence_dir

logger = logging.getLogger(__name__)


def _has_ffmpeg_and_ffprobe() -> bool:
    return all([shutil.which("ffmpeg") is None, shutil.which("ffprobe") is None])


def _get_duration(filename: str) -> float:
    cmd: list[str] = ["ffprobe", "-show_entries", "format=duration", filename]
    cmd_string: str = " ".join(cmd)
    logger.debug(f"Executing {cmd_string}")
    proc = subprocess.run(cmd, text=True, capture_output=True)  # nosec B603
    assert proc.returncode == 0
    duration: float = float(
        [line for line in proc.stdout.splitlines() if "duration" in line][0]
        .split("=")[-1]
        .strip()
    )
    return duration


skip_if_no_ffmpeg = pytest.mark.skipif(
    _has_ffmpeg_and_ffprobe(), reason="ffmpeg/ffprobe required"
)


@pytest.fixture(scope="module")
def configuration() -> Configuration:
    return test_utils.TestConfiguration(True, False, False)


@pytest.fixture()
def executor(clear_caches_module, configuration: Configuration):
    logger.debug("About to instantiate the picamera executor")
    executor = AstroPiExecutor(configuration=configuration)
    index_cycle: Optional[itertools.cycle[int]] = None

    def mock_find_next_datum(df: pd.DataFrame) -> int:
        nonlocal index_cycle
        if index_cycle is None:
            index_cycle = itertools.cycle((i for i in range(len(df))))
        return index_cycle.__next__()

    with patch.object(executor, "_find_next_datum", side_effect=mock_find_next_datum):
        yield executor


@pytest.fixture(autouse=True)
def cwd(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    return tmpdir


##################
# Helper methods #
##################

# MSE of image0.jpg and image1.jpg is ~100
# so, a tolerance of 10% of that is probably fine
TOLERANCE = 10

#########
# Tests #
#########


def test_image_capture(executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    filename: str = "photo1.jpg"
    cam.take_photo(filename)
    assert Path(filename).exists()
    test_utils.assert_images_equal(
        filename, get_replay_sequence_dir() / "photos" / "image0.jpg", TOLERANCE
    )


def test_image_capture_sets_exif_metadata(executor: AstroPiExecutor):
    latitude = (1.0, 29.1, 29.0, 48.78250810956524)
    longitude = (-1.0, 79.0, 17.0, 53.33060722541995)

    image_name = "picture_with_gps.jpg"
    cam = CameraAdapter(executor)
    cam.take_photo(image_name, gps_coordinates=(latitude, longitude))

    with open(image_name, "rb") as f:
        img = exif.Image(f)
    print(dir(img))
    assert img.gps_latitude == (29.0, 29.0, 48.8)
    assert img.gps_latitude_ref == "N"
    assert img.gps_longitude == (79.0, 17.0, 53.3)
    assert img.gps_longitude_ref == "W"


def test_image_capture_with_overlay():
    pass


def test_image_capture_with_annotation():
    pass


def test_capture_sequence(executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    filename: str = "sequence"
    cam.capture_sequence(filename)
    for i in range(10):
        format_string = f"{filename}-" + "{:02d}.jpg"
        actual = Path(format_string.format(i + 1))
        assert actual.exists()
        test_utils.assert_images_equal(
            actual, get_replay_sequence_dir() / "photos" / f"image{i}.jpg", TOLERANCE
        )


def test_capture_array(executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    arr = cam.capture_array()
    assert arr.shape == (720, 1280, 3)
    expected = np.asarray(
        Image.open(get_replay_sequence_dir() / "photos" / "image0.jpg")
    )

    test_utils.assert_arrays_equal(arr, expected, TOLERANCE)


@skip_if_no_ffmpeg
def test_capture_sequence_creates_video(executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    filename: str = "frame"
    cam.capture_sequence(filename, make_video=True)
    expected_filename: str = filename + "-timelapse.mp4"
    assert Path(expected_filename).exists()

    # The video should be 10 seconds in duration
    duration: float = _get_duration(expected_filename)
    assert round(duration) == 10


@skip_if_no_ffmpeg
@patch("astro_pi_replay.picamzero.camera_adapter.sleep", spec=True)
def test_record_video(mock_sleep: MagicMock, executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    filename: str = "video.mp4"
    cam.record_video(filename)

    assert Path(filename).exists()

    # Duration should be 5 seconds by default
    duration: float = _get_duration(filename)
    assert round(duration) == 5

    # it should have tried to sleep (assuming that
    # the test machine is fast enough)
    mock_sleep.assert_called_once()
    # and the argument should be a positive float
    assert len(mock_sleep.call_args.args) == 1
    assert isinstance(mock_sleep.call_args.args[0], float)
    assert mock_sleep.call_args.args[0] > 0


@skip_if_no_ffmpeg
def test_nonblocking_video_recording(executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    filename: str = "nonblocking-video.mp4"
    cam.start_recording(filename)
    sleep_duration: int = 1
    sleep(1)
    cam.stop_recording()
    assert Path(filename).exists()

    actual_duration: float = _get_duration(filename)
    assert round(actual_duration) == sleep_duration


@skip_if_no_ffmpeg
@patch("astro_pi_replay.picamzero.camera_adapter.sleep", spec=True)
def test_take_video_and_still(mock_sleep: MagicMock, executor: AstroPiExecutor):
    cam = CameraAdapter(executor)
    basename: str = "video_and_still"
    still_interval: int = 1
    cam.take_video_and_still(basename, duration=2, still_interval=still_interval)
    assert Path(f"{basename}.mp4").exists()
    assert Path(f"{basename}-1.jpg").exists()

    # TODO mock the datetime.now's in picamzero.Camera so that the test
    # is more deterministic + faster

    mock_sleep.assert_called()
    actual_interval: float = mock_sleep.call_args.args[0]
    assert round(actual_interval) == still_interval


def test_record_video_logs_helpful_message_when_ffmpeg_in_browser(
    monkeypatch, caplog, executor: AstroPiExecutor
):
    # Given
    monkeypatch.setenv("PATH", "")
    assert shutil.which("ffmpeg") is None
    executor.is_running_in_browser = True
    cam = CameraAdapter(executor)

    # When
    cam.record_video("failed_video_in_browser.mp4")

    assert (
        "Recording a video is not currently supported by "
        + "astro-pi-replay-online, sorry"
    ) in caplog.text
    assert (
        "On an Astro Pi this would record a video as you " + "requested"
    ) in caplog.text


def test_record_video_raises_helpful_exception_when_ffmpeg_not_installed(
    monkeypatch, executor: AstroPiExecutor
):
    # Given
    monkeypatch.setenv("PATH", "")
    assert shutil.which("ffmpeg") is None
    executor.is_running_in_browser = False
    cam = CameraAdapter(executor)

    # When
    with pytest.raises(FfmpegNotInstalledException) as e:
        cam.record_video("failed_video.mp4")
    assert os.linesep.join(
        [
            "Please install ffmpeg to record a video",
            "On Raspberry Pi OS, this can be done using the command below:",
            "",
            "  sudo apt-get install ffmpeg",
            "",
            "For download instructions on other operating systems, "
            + "check the ffmpeg website:",
            "",
            "  https://www.ffmpeg.org/download.html",
        ]
    ) in str(e.value)
