import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

import test_utils
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import get_replay_sequence_dir
from astro_pi_replay.sense_hat.sense_hat import SenseHatAdapter
from test_utils import TestConfiguration, get_test_resource

###########
# Fixtures
###########


@pytest.fixture(autouse=True, scope="module")
def configuration():
    return TestConfiguration(True, True, False)


@pytest.fixture(autouse=True, scope="module")
def executor(configuration):
    # Set to interpolate to avoid blocking the tests
    executor = AstroPiExecutor(configuration=configuration)
    return executor


########
# Tests
########


def test_replayed_data_is_consistent(executor: AstroPiExecutor):
    # Makes the test deterministic
    with patch("astro_pi_replay.executor.datetime", wraps=datetime) as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)

        assert sh.color.rgb == sh.color.color[:3]
        # the real rgb is just color.color[:3] and not raw.
        assert sh.color.red == sh.color.color[0]
        assert sh.color.green == sh.color.color[1]
        assert sh.color.blue == sh.color.color[2]
        assert sh.color.clear == sh.color.color[3]
        assert sh.color.gain == 1
        assert sh.color.max_raw == 1024
        assert sh.color.red_raw == sh.color.color_raw[0]
        assert sh.color.green_raw == sh.color.color_raw[1]
        assert sh.color.blue_raw == sh.color.color_raw[2]
        assert sh.color.clear_raw == sh.color.color_raw[3]
        assert sh.color.clear_raw == sh.color.brightness
        assert sh.color.red_raw == sh.color.red * (sh.color.max_raw // 256)
        assert sh.color.green_raw == sh.color.green * (sh.color.max_raw // 256)
        assert sh.color.blue_raw == sh.color.blue * (sh.color.max_raw // 256)
        assert sh.color.clear_raw == sh.color.clear * (sh.color.max_raw // 256)
        assert sh.colour.rgb == sh.color.rgb
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


def test_setters_assign_correctly(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
    try:
        sh.set_rotation(90)
        assert sh.rotation == 90
        sh.set_imu_config(True, True, False)
        sh.colour.integration_cycles = 3
        assert sh.colour.integration_cycles == 3
    except:  # noqa: E722
        assert False


def test_replay_should_replay_sequence_of_data(executor: AstroPiExecutor):
    # Make the test deterministic
    with patch("astro_pi_replay.executor.datetime", wraps=datetime) as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)
        assert sh.colour.colour == (9, 8, 8, 17)
        assert executor._state._last_sense_hat_row_index == -1


def test_sense_hat_adapter_has_all_expected_methods(executor: AstroPiExecutor):
    executor.configuration.interpolate_sense_hat = True
    sh = SenseHatAdapter(executor)
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


def test_sense_hat_adapter_has_all_expected_attrs(executor: AstroPiExecutor):
    executor.configuration.interpolate_sense_hat = True
    sh = SenseHatAdapter(executor)
    with get_test_resource("sense_hat_interface.json").open() as f:
        sense_hat_interface = json.loads(f.read())
    for path in ["", "colour", "stick"]:
        suffix: str = path.split(".")[-1]
        obj: object = getattr(sh, path) if path != "" else sh
        for attr in filter(
            lambda x: not x.startswith("_"),
            sense_hat_interface["sense_hat" if suffix == "" else suffix]["attrs"],
        ):
            if attr == "accel":
                print(f"Checking {attr}")
            assert hasattr(obj, attr)


def test_load_image_and_set_and_get_pixels(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
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
def test_set_pixels_converts_to_rgb565(executor: AstroPiExecutor):
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


def test_rotations_rotate_display(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
    ai_logo = get_test_resource("ai-logo.rgb")
    sh.rotation = 270
    original = sh.load_image(str(ai_logo))
    before = original.copy()
    for i in range(90, 450, 90):
        sh.rotation = i % 360
        assert sh.get_pixels() != before
        before = sh.get_pixels()
    assert before == original


def test_flips_flips_display_orientation(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
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


def test_low_light_sets_gamma(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
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


def test_show_letter_displays_letter(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
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


def test_show_message(executor: AstroPiExecutor):
    sh = SenseHatAdapter(executor)
    original_method = sh.set_pixels
    frames = []
    setattr(sh, "set_pixels", lambda p: (frames.append(p), original_method(p))[-1])
    message = "Hello, world!"
    sh.show_message(message, scroll_speed=0.001)  # fast for testing
    assert len(frames) == 72


def test_interpolates_values():
    configuration = TestConfiguration(True, True, False)
    executor = AstroPiExecutor(configuration=configuration)
    sh = SenseHatAdapter(executor)

    # Find the last two rows
    test_sh_data: Path = get_replay_sequence_dir() / "data" / "data.csv"
    # TODO this name should be static and globally defined
    df = executor._df_from_replay_file(str(test_sh_data), "datetime")
    first_date = df.iloc[-2].name.to_pydatetime()
    # TODO this column name should be statically defined
    column_to_compare = "pres"
    first_datum = df.iloc[-2][column_to_compare]
    second_date = df.iloc[-1].name.to_pydatetime()
    second_datum = df.iloc[-1][column_to_compare]
    test_utils.assume(
        [first_date < second_date, first_datum != second_datum],
        reason="Interpolation needs different values for a fair test",
    )

    # patch datetime.now to return a datetime in between
    in_between: datetime = first_date + timedelta(
        seconds=(second_date - first_date).total_seconds() / 2
    )
    with patch("astro_pi_replay.executor.datetime", wraps=datetime) as mock_datetime:
        mock_datetime.now.return_value = in_between
        pressure = sh.get_pressure()
    assert (
        pressure > first_datum
        and pressure < second_datum
        or pressure < first_datum
        and pressure > second_datum
    )
