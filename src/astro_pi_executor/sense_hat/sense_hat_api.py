#!/usr/bin/python
import typing

import numpy as np
import pandas as pd

from astro_pi_executor.custom_types import (
    DEFAULT_ROLL_PITCH_YAW_DICT,
    DEFAULT_X_Y_Z_DICT,
    RGB,
    RGBC,
    RollPitchYawDict,
    XYZDict,
)
from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.sense_hat.sense_hat_public_api import (
    SenseHatAPI,
    SenseHatColourSensorAPI,
    SenseHatStickAPI,
)


def xyzdict_reducer(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(lambda col: col.split("_")[-1]).to_dict()


def to_dict_reducer(df: pd.DataFrame) -> pd.DataFrame:
    return df.to_dict()


def SenseHatColourSensorAdapter(executor: AstroPiExecutor) -> SenseHatColourSensorAPI:
    class _SenseHatColourSensorAdapter(SenseHatColourSensorAPI):
        def __init__(self):
            super().__init__(int(), int(), object())

        # Private
        def _scale(self, value) -> int:
            """Scales from a normalised value to an
            approximate raw value by reversing the
            steps in the original SenseHat module"""
            return value * (self.max_raw // 256)

        # Public

        @property
        @executor.sense_hat_replay(col_names=["blue"])
        def blue(self) -> int:
            return super().blue

        @property
        def blue_raw(self) -> int:
            return self._scale(self.blue)

        @property
        @executor.sense_hat_replay(col_names=["clear"])
        def clear(self) -> int:
            return super().clear

        @property
        def clear_raw(self) -> int:
            return self._scale(self.clear)

        @property
        @executor.sense_hat_replay(
            col_names=["red", "green", "blue", "clear"], reducer=lambda s: tuple(s[:4])
        )
        def colour(self) -> RGBC:
            return super().colour

        @property
        def colour_raw(self) -> RGBC:
            colour: RGBC = self.colour
            return typing.cast(RGBC, tuple(map(lambda x: self._scale(x), colour)))

        @property
        def enabled(self) -> bool:
            return True

        @enabled.setter
        def enabled(self, _: bool) -> None:
            pass

        @property
        def gain(self) -> int:
            return 1

        @gain.setter
        def gain(self, _: int) -> None:
            pass

        @property
        @executor.sense_hat_replay(col_names=["green"])
        def green(self) -> int:
            return super().green

        @property
        def green_raw(self) -> int:
            return self._scale(self.green)

        @property
        def integration_cycles(self) -> int:
            return 1

        @integration_cycles.setter
        def integration_cycles(self, _: int) -> None:
            pass

        @property
        def integration_time(self) -> float:
            return 0.0024

        @property
        def max_raw(self) -> int:
            return 1024

        @property
        @executor.sense_hat_replay(col_names=["red"])
        def red(self) -> int:
            return super().red

        @property
        def red_raw(self) -> int:
            return self._scale(self.red)

        @property
        @executor.sense_hat_replay(
            col_names=["red", "green", "blue"], reducer=lambda s: tuple(s[:3])
        )
        def rgb(self) -> RGB:
            return super().rgb

    return _SenseHatColourSensorAdapter()


# TODO - remove methods that are just synonyms
def SenseHatAdapter(executor: AstroPiExecutor = AstroPiExecutor()) -> SenseHatAPI:
    class _SenseHatAdapter(SenseHatAPI):
        """
        This is an object that conforms to the SenseHat interface
        that returns default values for every function call.
        For most types the default value is obvious, but
        check check sense_hat_public_api.py if in doubt.
        """

        def __init__(self):
            super().__init__(str(), str())

        # TODO
        # @property
        # def accel(self) -> RollPitchYawDict:
        #    return self.accelerometer

        @property
        def accel_raw(self) -> XYZDict:
            return self.accelerometer_raw

        # @property
        # def accelerometer(self) -> RollPitchYawDict:
        #    return DEFAULT_ROLL_PITCH_YAW_DICT

        @property
        @executor.sense_hat_replay(
            col_names=["acc_x", "acc_y", "acc_z"], reducer=xyzdict_reducer
        )
        def accelerometer_raw(self) -> XYZDict:
            return DEFAULT_X_Y_Z_DICT

        # def clear(self, *args) -> None:
        #    pass

        # @property
        # def compass(self) -> float:
        #    return float()

        @property
        @executor.sense_hat_replay(
            col_names=["mag_x", "mag_y", "mag_z"], reducer=xyzdict_reducer
        )
        def compass_raw(self) -> XYZDict:
            return DEFAULT_X_Y_Z_DICT

        @property
        def colour(self) -> SenseHatColourSensorAPI:
            return SenseHatColourSensorAdapter(executor)

        @property
        def color(self) -> SenseHatColourSensorAPI:
            return self.colour

        # def flip_h(self, redraw:bool) -> None:
        #    pass

        # def flip_v(self, redraw:bool) -> None:
        #    pass

        # @property
        # def gamma(self) -> list[int]:
        #    return list()

        # @gamma.setter
        # def gamma(self, buffer: list[int]) -> None:
        #    pass

        # def gamma_reset(self) -> None:
        #    pass

        # def get_pixel(self, x: int, y: int) -> list[int]:
        #    return list()

        # def get_pixels(self) -> list[list[int]]:
        #    return list()

        def get_temperature_from_humidity(self) -> float:
            return self.temperature

        def get_temperature_from_pressure(self) -> float:
            return self.temperature

        # @property
        # def gyro(self) -> RollPitchYawDict:
        #    return self.gyroscope

        @property
        def gyro_raw(self) -> XYZDict:
            return self.gyroscope_raw

        # @property
        # def gyroscope(self) -> RollPitchYawDict:
        #    return DEFAULT_ROLL_PITCH_YAW_DICT

        @property
        @executor.sense_hat_replay(
            col_names=["gyro_x", "gyro_y", "gyro_z"], reducer=xyzdict_reducer
        )
        def gyroscope_raw(self) -> XYZDict:
            return DEFAULT_X_Y_Z_DICT

        @property
        @executor.sense_hat_replay(col_names=["hum"])
        def humidity(self) -> float:
            return float()

        # TODO: no need for this in this file.
        def has_colour_sensor(self) -> bool:
            return hasattr(self, "colour")

        # def load_image(self, file_path: str, redraw:bool) -> list[list[int]]:
        #    return list()

        # @property
        # def low_light(self) -> bool:
        #    return bool()

        # @low_light.setter
        # def low_light(self, value: int) -> None:
        #    pass

        @property
        @executor.sense_hat_replay(
            col_names=["roll", "pitch", "yaw"], reducer=to_dict_reducer
        )
        def orientation(self) -> RollPitchYawDict:
            return DEFAULT_ROLL_PITCH_YAW_DICT

        @property
        def orientation_radians(self) -> RollPitchYawDict:
            # 1 degree is pi/180 radians
            degrees = self.orientation
            return {
                "roll": degrees["roll"] * (np.pi / 180.0),
                "pitch": degrees["pitch"] * (np.pi / 180.0),
                "yaw": degrees["yaw"] * (np.pi / 180.0),
            }

        @property
        @executor.sense_hat_replay(col_names=["pres"])
        def pressure(self) -> float:
            return float()

        # @property
        # def rotation(self) -> int:
        #    return int()

        # @rotation.setter
        # def rotation(self, r: int) -> None:
        #    pass

        # def set_imu_config(self,
        #                   compass_enabled: bool,
        #                   gyro_enabled: bool,
        #                   accel_enabled: bool) -> None:
        #    pass

        # def set_pixels(self, pixel_list:list[list[int]], intercept:bool) -> None:
        #    pass

        # def set_pixel(self, x: int, y: int, *args) -> None:
        #    pass

        # def set_rotation(self, r:int, redraw:bool) -> None:
        #    pass

        # def show_letter(self,
        #                s: str,
        #                text_colour: list[int],
        #                back_colour: list[int]) -> None:
        #    pass

        # def show_message(self,
        #                 text_string:str,
        #                 scroll_speed:float,
        #                 text_colour:list[int],
        #                 back_colour:list[int]) -> None:
        #    pass

        @property
        def stick(self) -> SenseHatStickAPI:
            return SenseHatStickAPI()

        @property
        def temp(self) -> float:
            return self.temperature

        @property
        @executor.sense_hat_replay(col_names=["temp"])
        def temperature(self) -> float:
            return float()

    return _SenseHatAdapter()


# Kept for reference (for now):
#
# class MagicSenseHat(SenseHatAPI):
#
#    example_file = { "rotation": [0.35] }
#    replay_mode = True
#
#    def __getattribute__(self, name: str):
#        is_replay_mode: bool = object.__getattribute__(self, "replay_mode")
#        if is_replay_mode and not name.startswith("_"):
#            try:
#                return MagicSenseHat.example_file[name][0]
#            except KeyError:
#                pass
#        # call the super method
#        return object.__getattribute__(self, name)
#
#
