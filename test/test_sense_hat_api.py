import json
import math
from datetime import timedelta
from unittest.mock import patch

import pytest

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.sense_hat.sense_hat import SenseHatAdapter
from test_utils import get_test_resource


def test_replayed_data_is_consistent():
    executor = AstroPiExecutor()
    # Makes the test deterministic
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)

        assert sh.color.rgb == sh.color.color_raw[:3]
        assert sh.color.red == sh.color.color[0]
        assert sh.color.green == sh.color.color[1]
        assert sh.color.blue == sh.color.color[2]
        assert sh.color.clear == sh.color.color[3]
        assert sh.color.gain == 1
        assert sh.color.max_raw == 1024
        assert sh.color.red_raw == sh.color.rgb[0]
        assert sh.color.green_raw == sh.color.rgb[1]
        assert sh.color.blue_raw == sh.color.rgb[2]
        assert sh.color.clear_raw == sh.color.color_raw[3]
        assert sh.color.color_raw[:3] == sh.color.rgb
        assert sh.color.clear_raw == sh.color.brightness
        assert sh.colour.rgb == sh.colour.color_raw[:3]
        assert sh.colour.integration_time == 0.0024
        assert sh.colour.integration_cycles == 1
        assert sh.temp == sh.temperature
        assert sh.temp == sh.get_temperature()
        assert sh.get_temperature() == sh.get_temperature_from_humidity()
        assert sh.get_temperature_from_humidity() == sh.get_temperature_from_pressure()
        assert sh.accel == sh.accelerometer
        assert sh.accel == sh.get_accelerometer()
        assert sh.gyro == sh.gyroscope
        assert sh.gyro == sh.get_gyroscope()
        assert sh.compass == sh.get_compass()
        assert sh.pressure == sh.get_pressure()
        assert sh.humidity == sh.get_humidity()
        assert sh.orientation == sh.get_orientation()
        assert sh.orientation_radians == sh.get_orientation_radians()
        assert sh.get_orientation() == sh.get_orientation_degrees()
        assert sh.get_orientation_degrees() == dict(
            (k, math.degrees(v) % 360) for k, v in sh.get_orientation_radians().items()
        )
        assert sh.accel_raw == sh.accelerometer_raw
        assert sh.accel_raw == sh.get_accelerometer_raw()
        assert sh.gyro_raw == sh.gyroscope_raw
        assert sh.gyro_raw == sh.get_gyroscope_raw()
        assert sh.compass_raw == sh.get_compass_raw()


def test_setters_assign_correctly():
    sh = SenseHatAdapter()
    try:
        sh.set_rotation(90)
        assert sh.rotation == 90
        sh.set_imu_config(True, True, False)
        sh.colour.integration_cycles = 3
        assert sh.colour.integration_cycles == 3
    except:  # noqa: E722
        assert False


def test_replay_should_replay_sequence_of_data():
    executor = AstroPiExecutor()

    # Make the test deterministic
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)
        assert sh.colour.colour == (9, 8, 8, 17)
        assert executor._state._last_sense_hat_row_index == 1023  # last row


def test_sense_hat_adapter_has_all_expected_methods():
    sh = SenseHatAdapter()
    with get_test_resource("sense_hat_interface.json").open() as f:
        sense_hat_interface = json.loads(f.read())
    for path in ["", "colour", "stick"]:
        suffix: str = path.split(".")[-1]
        obj: object = getattr(sh, path) if path != "" else sh
        for method in filter(
            lambda x: not x.startswith("_"),
            sense_hat_interface["sense_hat" if suffix == "" else suffix]["callables"],
        ):
            assert hasattr(obj, method)
            func = getattr(obj, method)
            assert callable(func)


def test_sense_hat_adapter_has_all_expected_attrs():
    sh = SenseHatAdapter()
    with get_test_resource("sense_hat_interface.json").open() as f:
        sense_hat_interface = json.loads(f.read())
    for path in ["", "colour", "stick"]:
        suffix: str = path.split(".")[-1]
        obj: object = getattr(sh, path) if path != "" else sh
        for attr in filter(
            lambda x: not x.startswith("_"),
            sense_hat_interface["sense_hat" if suffix == "" else suffix]["attrs"],
        ):
            assert hasattr(obj, attr)


def test_load_image_and_set_and_get_pixels():
    sh = SenseHatAdapter()
    result: list[list[int]] = sh.load_image(str(get_test_resource("ai-logo.rgb")))
    # this was taken from the actual sensehat
    assert result == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [128, 192, 0],
        [128, 192, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [128, 192, 0],
        [128, 192, 0],
        [128, 192, 0],
        [0, 0, 0],
        [128, 192, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    assert result == sh.get_pixels()


@pytest.mark.skip(reason="Not yet implemented")
def test_set_pixels_converts_to_rgb565():
    # convert actual from rgb8 to rgb565
    # arr = np.array(actual, dtype=np.uint8) # (64,3)
    # # r and b (originally 255) will be (255 & 0b11111000)=248
    # # g (originally 255) will be (255 & 0b11111100)=252
    # # TODO move this to set_pixels...
    # r = np.array(list(map(lambda x: x & 0b11111000, arr[:,0])), dtype=np.uint8)
    # g = np.array(list(map(lambda x: x & 0b11111000, arr[:,1])), dtype=np.uint8)
    # b = np.array(list(map(lambda x: x & 0b11111000, arr[:,2])), dtype=np.uint8)
    # actual = np.dstack((r,g,b)).tolist()
    pass


def test_rotations_rotate_display():
    sh = SenseHatAdapter()
    ai_logo = get_test_resource("ai-logo.rgb")
    sh.rotation = 270
    original = sh.load_image(str(ai_logo))
    before = original.copy()
    for i in range(90, 450, 90):
        sh.rotation = i % 360
        assert sh.get_pixels() != before
        before = sh.get_pixels()
    assert before == original


def test_flips_flips_display_orientation():
    sh = SenseHatAdapter()
    ai_logo = get_test_resource("ai-logo.rgb")
    sh.rotation = 270
    original = sh.load_image(str(ai_logo))
    assert original != sh.get_pixels()  # should be rotated
    original = sh.get_pixels()
    methods = [sh.flip_h, sh.flip_v]
    for method in methods:
        before = original.copy()
        for _ in range(2):
            method()
            assert before != sh.get_pixels()
            before = sh.get_pixels()
        assert before == original


def test_low_light_sets_gamma():
    sh = SenseHatAdapter()
    original = sh.gamma
    assert original == [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        2,
        2,
        3,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        14,
        15,
        17,
        18,
        20,
        21,
        23,
        25,
        27,
        29,
        31,
    ]
    sh.low_light = True
    assert sh.low_light is True
    assert sh.gamma == [
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        3,
        3,
        3,
        4,
        4,
        5,
        5,
        6,
        6,
        7,
        7,
        8,
        8,
        9,
        10,
        10,
    ]
    sh.low_light = False
    assert sh.low_light is False
    assert sh.gamma == original


def test_show_letter_displays_letter():
    sh = SenseHatAdapter()
    sh.show_letter("G")
    actual = sh.get_pixels()
    expected = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [0, 0, 0],
        [0, 0, 0],
    ]
    assert actual == expected


def test_show_message():
    sh = SenseHatAdapter()
    original_method = sh.set_pixels
    frames = []
    setattr(sh, "set_pixels", lambda p: (frames.append(p), original_method(p))[-1])
    message = "Hello, world!"
    sh.show_message(message, scroll_speed=0.001)  # fast for testing
    assert len(frames) == 72
