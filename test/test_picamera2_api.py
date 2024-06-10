import logging
from pathlib import Path
import pytest

from astro_pi_replay.configuration import Configuration
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.picamera2.picamera2.picamera2 import Picamera2Adapter
import test.test_utils as test_utils


logger = logging.getLogger(__name__)


############
# Fixtures #
############

@pytest.fixture(scope="module")
def configuration() -> Configuration:
    return test_utils.TestConfiguration(True, False, False)


@pytest.fixture(scope="module")
def executor(clear_caches_module, configuration: Configuration):
    logger.debug("About to instantiate the picamera executor")
    executor = AstroPiExecutor(configuration=configuration)
    return executor


def test_create_preview_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor).create_preview_configuration())
    expected: str = \
    """{'use_case': 'preview', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'sYCC'>, 'buffer_count': 4, 'queue': True, 'main': {'format': 'XBGR8888', 'size': (640, 480)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (640, 480)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.Minimal: 3>, 'FrameDurationLimits': (100, 83333)}, 'sensor': {}, 'display': 'main', 'encode': 'main'}"""
    assert actual == expected

def test_create_still_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor)
        .create_still_configuration())
    expected: str = \
    """{'use_case': 'still', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'sYCC'>, 'buffer_count': 1, 'queue': True, 'main': {'format': 'BGR888', 'size': (4056, 3040)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (4056, 3040)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>, 'FrameDurationLimits': (100, 1000000000)}, 'sensor': {}, 'display': None, 'encode': None}"""
    assert actual == expected

def test_create_video_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor).create_video_configuration())
    expected: str = \
    """{'use_case': 'video', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'Rec709'>, 'buffer_count': 6, 'queue': True, 'main': {'format': 'XBGR8888', 'size': (1280, 720)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (1280, 720)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.Fast: 1>, 'FrameDurationLimits': (33333, 33333)}, 'sensor': {}, 'display': 'main', 'encode': 'main'}"""
    assert actual == expected

##############
# Test methods
##############

def test_start_and_capture_file_takes_picture(
    executor: AstroPiExecutor,
    tmp_path: Path):
    expected_path: Path = tmp_path / "image1.jpg"
    camera = Picamera2Adapter(executor)
    camera.start_and_capture_file(str(expected_path))

    # TODO content assert
    assert expected_path.exists()

# TODO test set exif tags

def test_start_and_capture_files(
    executor: AstroPiExecutor,
    tmp_path: Path):
    camera = Picamera2Adapter(executor)
    camera.start_and_capture_files(num_files=3)

def test_start_and_record_video(
    executor: AstroPiExecutor,
    tmp_path: Path):
    pass
    # "test.mp4", duration=5)

def test_foo():
    pass
