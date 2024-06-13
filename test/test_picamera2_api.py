import logging
import test.test_utils as test_utils
from pathlib import Path

import pytest
from astro_pi_replay.configuration import Configuration
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.picamera2.picamera2.picamera2 import Picamera2Adapter

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


def test_default_configuration_matches_real(executor: AstroPiExecutor):
    picam2 = Picamera2Adapter(executor)

    # # check the internal state matches the real implementation
    assert picam2.camera_idx == 0
    # picam2.camera == Camera()
    # picam2.camera_manager.cameras
    assert len(picam2.camera_manager.cameras) == 1
    assert picam2.camera_manager.cameras[0] == picam2.camera
    # assert picam2.camera_ctrl_info == {'Sharpness': (libcamera.ControlId(22, Sharpness, ControlType.Float), libcamera.ControlInfo([0.000000..16.000000])), 'AwbEnable': (libcamera.ControlId(15, AwbEnable, ControlType.Bool), libcamera.ControlInfo([false..true])), 'Contrast': (libcamera.ControlId(13, Contrast, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'Saturation': (libcamera.ControlId(20, Saturation, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'Brightness': (libcamera.ControlId(12, Brightness, ControlType.Float), libcamera.ControlInfo([-1.000000..1.000000])), 'AeFlickerPeriod': (libcamera.ControlId(10, AeFlickerPeriod, ControlType.Integer32), libcamera.ControlInfo([100..1000000])), 'HdrMode': (libcamera.ControlId(41, HdrMode, ControlType.Integer32), libcamera.ControlInfo([0..4])), 'ExposureValue': (libcamera.ControlId(6, ExposureValue, ControlType.Float), libcamera.ControlInfo([-8.000000..8.000000])), 'ColourGains': (libcamera.ControlId(18, ColourGains, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'StatsOutputEnable': (libcamera.ControlId(20001, StatsOutputEnable, ControlType.Bool), libcamera.ControlInfo([false..true])), 'ScalerCrop': (libcamera.ControlId(25, ScalerCrop, ControlType.Rectangle), libcamera.ControlInfo([(0, 0)/0x0..(65535, 65535)/65535x65535])), 'ExposureTime': (libcamera.ControlId(7, ExposureTime, ControlType.Integer32), libcamera.ControlInfo([0..66666])), 'AeEnable': (libcamera.ControlId(1, AeEnable, ControlType.Bool), libcamera.ControlInfo([false..true])), 'NoiseReductionMode': (libcamera.ControlId(10002, NoiseReductionMode, ControlType.Integer32), libcamera.ControlInfo([0..4])), 'AeConstraintMode': (libcamera.ControlId(4, AeConstraintMode, ControlType.Integer32), libcamera.ControlInfo([0..3])), 'FrameDurationLimits': (libcamera.ControlId(28, FrameDurationLimits, ControlType.Integer64), libcamera.ControlInfo([33333..120000])), 'AnalogueGain': (libcamera.ControlId(8, AnalogueGain, ControlType.Float), libcamera.ControlInfo([1.000000..16.000000])), 'AeFlickerMode': (libcamera.ControlId(9, AeFlickerMode, ControlType.Integer32), libcamera.ControlInfo([0..1])), 'AwbMode': (libcamera.ControlId(16, AwbMode, ControlType.Integer32), libcamera.ControlInfo([0..7])), 'AeMeteringMode': (libcamera.ControlId(3, AeMeteringMode, ControlType.Integer32), libcamera.ControlInfo([0..3])), 'AeExposureMode': (libcamera.ControlId(5, AeExposureMode, ControlType.Integer32), libcamera.ControlInfo([0..3]))}
    # assert picam2.camera_properties_ == {'Model': 'imx477', 'UnitCellSize': (1550, 1550), 'ColorFilterArrangement': 0, 'Location': 2, 'Rotation': 180, 'PixelArraySize': (4056, 3040), 'PixelArrayActiveAreas': [(8, 16, 4056, 3040)], 'ScalerCropMaximum': (0, 0, 0, 0), 'SystemDevices': (20750, 20751, 20737, 20738, 20739)}
    assert picam2._raw_modes == [{'format': 'SRGGB10_CSI2P', 'size': (1332, 990)}, {'format': 'SRGGB12_CSI2P', 'size': (2028, 1080)}, {'format': 'SRGGB12_CSI2P', 'size': (2028, 1520)}, {'format': 'SRGGB12_CSI2P', 'size': (4056, 3040)}]
    assert picam2._native_mode == {'format': 'SRGGB12_CSI2P', 'size': (4056, 3040)}
    assert picam2.sensor_resolution == (4056, 3040)
    assert picam2.sensor_format == 'SRGGB12_CSI2P'

    config = picam2.create_still_configuration()
    picam2.configure(config)
    
    # picam2.libcamera_config == <libcamera._libcamera.CameraConfiguration object at 0x7fa489d630>

    # assert picam2.camera_ctrl_info == {'AeExposureMode': (libcamera.ControlId(5, AeExposureMode, ControlType.Integer32), libcamera.ControlInfo([0..3])), 'AeMeteringMode': (libcamera.ControlId(3, AeMeteringMode, ControlType.Integer32), libcamera.ControlInfo([0..3])), 'AwbMode': (libcamera.ControlId(16, AwbMode, ControlType.Integer32), libcamera.ControlInfo([0..7])), 'AeFlickerMode': (libcamera.ControlId(9, AeFlickerMode, ControlType.Integer32), libcamera.ControlInfo([0..1])), 'AnalogueGain': (libcamera.ControlId(8, AnalogueGain, ControlType.Float), libcamera.ControlInfo([1.000000..22.260870])), 'FrameDurationLimits': (libcamera.ControlId(28, FrameDurationLimits, ControlType.Integer64), libcamera.ControlInfo([100000..694434742])), 'AeConstraintMode': (libcamera.ControlId(4, AeConstraintMode, ControlType.Integer32), libcamera.ControlInfo([0..3])), 'NoiseReductionMode': (libcamera.ControlId(10002, NoiseReductionMode, ControlType.Integer32), libcamera.ControlInfo([0..4])), 'Sharpness': (libcamera.ControlId(22, Sharpness, ControlType.Float), libcamera.ControlInfo([0.000000..16.000000])), 'AwbEnable': (libcamera.ControlId(15, AwbEnable, ControlType.Bool), libcamera.ControlInfo([false..true])), 'StatsOutputEnable': (libcamera.ControlId(20001, StatsOutputEnable, ControlType.Bool), libcamera.ControlInfo([false..true])), 'Contrast': (libcamera.ControlId(13, Contrast, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'Saturation': (libcamera.ControlId(20, Saturation, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'Brightness': (libcamera.ControlId(12, Brightness, ControlType.Float), libcamera.ControlInfo([-1.000000..1.000000])), 'ColourGains': (libcamera.ControlId(18, ColourGains, ControlType.Float), libcamera.ControlInfo([0.000000..32.000000])), 'AeFlickerPeriod': (libcamera.ControlId(10, AeFlickerPeriod, ControlType.Integer32), libcamera.ControlInfo([100..1000000])), 'HdrMode': (libcamera.ControlId(41, HdrMode, ControlType.Integer32), libcamera.ControlInfo([0..4])), 'ExposureValue': (libcamera.ControlId(6, ExposureValue, ControlType.Float), libcamera.ControlInfo([-8.000000..8.000000])), 'ScalerCrop': (libcamera.ControlId(25, ScalerCrop, ControlType.Rectangle), libcamera.ControlInfo([(0, 0)/64x64..(0, 0)/4056x3040])), 'ExposureTime': (libcamera.ControlId(7, ExposureTime, ControlType.Integer32), libcamera.ControlInfo([114..0])), 'AeEnable': (libcamera.ControlId(1, AeEnable, ControlType.Bool), libcamera.ControlInfo([false..true]))}
    assert picam2.camera_properties_ == {'Model': 'imx477', 'UnitCellSize': (1550, 1550), 'ColorFilterArrangement': 0, 'Location': 2, 'Rotation': 180, 'PixelArraySize': (4056, 3040), 'PixelArrayActiveAreas': [(8, 16, 4056, 3040)], 'ScalerCropMaximum': (0, 0, 4056, 3040), 'SystemDevices': (20750, 20751, 20737, 20738, 20739), 'SensorSensitivity': 1.0}
    # assert picam2.stream_map == {'main': <libcamera._libcamera.Stream object at 0x7f95a60a70>, 'lores': None, 'raw': <libcamera._libcamera.Stream object at 0x7f95a60a30>}
    assert picam2.display_stream_name is None
    assert picam2.encode_stream_name is None
    assert picam2._max_queue_len == 0
    # assert picam2.streams == [<libcamera._libcamera.Stream object at 0x7f95a60a70>, <libcamera._libcamera.Stream object at 0x7f95a60a30>]
    # assert picam2.camera_config == {'use_case': 'still', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'sYCC'>, 'buffer_count': 1, 'queue': True, 'main': {'format': 'BGR888', 'size': (4056, 3040), 'stride': 12192, 'framesize': 37063680}, 'lores': None, 'raw': {'format': 'SBGGR12_CSI2P', 'size': (4056, 3040), 'stride': 6112, 'framesize': 18580480}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>, 'FrameDurationLimits': (100, 1000000000)}, 'sensor': {'bit_depth': 12, 'output_size': (4056, 3040)}, 'display': None, 'encode': None}
    # ? assert picam2.allocator == <picamera2.allocators.dmaallocator.DmaAllocator object at 0x7f95a611d0>
    # picam2.controls == <Controls: {'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>, 'FrameDurationLimits': (100, 1000000000)}>
    assert picam2.configure_count == 1


##############
# Test methods
##############

def test_create_preview_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor).create_preview_configuration())
    expected: str = """{'use_case': 'preview', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'sYCC'>, 'buffer_count': 4, 'queue': True, 'main': {'format': 'XBGR8888', 'size': (640, 480)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (640, 480)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.Minimal: 3>, 'FrameDurationLimits': (100, 83333)}, 'sensor': {}, 'display': 'main', 'encode': 'main'}"""
    assert actual == expected


def test_create_still_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor).create_still_configuration())
    expected: str = """{'use_case': 'still', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'sYCC'>, 'buffer_count': 1, 'queue': True, 'main': {'format': 'BGR888', 'size': (4056, 3040)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (4056, 3040)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>, 'FrameDurationLimits': (100, 1000000000)}, 'sensor': {}, 'display': None, 'encode': None}"""
    assert actual == expected


def test_create_video_configuration_defaults(executor: AstroPiExecutor):
    actual: str = repr(Picamera2Adapter(executor).create_video_configuration())
    expected: str = """{'use_case': 'video', 'transform': <libcamera.Transform 'identity'>, 'colour_space': <libcamera.ColorSpace 'Rec709'>, 'buffer_count': 6, 'queue': True, 'main': {'format': 'XBGR8888', 'size': (1280, 720)}, 'lores': None, 'raw': {'format': 'SRGGB12_CSI2P', 'size': (1280, 720)}, 'controls': {'NoiseReductionMode': <NoiseReductionModeEnum.Fast: 1>, 'FrameDurationLimits': (33333, 33333)}, 'sensor': {}, 'display': 'main', 'encode': 'main'}"""
    assert actual == expected


# Photo capture

def test_start_and_capture_file_takes_picture(
    executor: AstroPiExecutor, tmp_path: Path
):
    expected_path: Path = tmp_path / "image1.jpg"
    camera = Picamera2Adapter(executor)
    camera.start_and_capture_file(str(expected_path))

    # TODO content assert
    assert expected_path.exists()


# TODO test set exif tags


def test_start_and_capture_files(executor: AstroPiExecutor, tmp_path: Path):
    camera = Picamera2Adapter(executor)
    camera.start_and_capture_files(num_files=3)


def test_start_and_record_video(executor: AstroPiExecutor, tmp_path: Path):
    pass
    # "test.mp4", duration=5)


def test_foo():
    pass
