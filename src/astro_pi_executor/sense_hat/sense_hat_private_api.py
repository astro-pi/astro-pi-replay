#!/usr/bin/python
from abc import ABC, abstractmethod
from typing import Optional, Protocol


class SenseHatPrivateAttributesProtocol(Protocol):
    _fb_device: Optional[str]
    _pix_map: None  # dict[int, np.ndarray]
    _rotation: int
    _text_dict: None
    _imu_settings: object  # use object for now because we don't -
    # want to import RTIMU.Settings here.
    _imu: object  # similar problem for RTIMU.RTIMU
    _imu_init: bool
    _pressure: object  # RTIMU.RTPressure
    _pressure_init: bool
    _humidity: object  # RTIMU.RTHumidity
    _humidity_init: bool
    _last_orientation: dict[str, float]
    _last_compass_raw: dict[str, float]
    _last_gyro_raw: dict[str, float]
    _last_accel_raw: dict[str, float]
    _compass_enabled: bool
    _gyro_enabled: bool
    _accel_enabled: bool
    _stick: object  # SenseStick()
    _colour: object  # ColourSensor()


class AbstractSenseHatPrivateMethods(ABC):
    @abstractmethod
    def _get_fb_device(self) -> str:
        return str()

    @abstractmethod
    def _load_text_assets(self, text_image_file: str, text_file: str) -> None:
        pass

    @abstractmethod
    def _trim_whitespace(self, char: str) -> str:
        return str()

    @abstractmethod
    # TODO should be an RTIMU.Settings
    def _get_settings_file(self, imu_settings_file: str) -> object:
        return object()

    @abstractmethod
    def _pack_bin(self, pix: list[list[int]]) -> bytes:
        return bytes()

    @abstractmethod
    # TODO double check this signature
    def _unpack_bin(self, packed: bytes) -> list[list[int]]:
        return list()

    @abstractmethod
    def _save_matrix(self) -> None:
        pass

    @abstractmethod
    # TODO double check this signature
    def _get_char_pixels(self, s: str) -> list[list[int]]:
        return list()

    @abstractmethod
    def _init_humidity(self) -> None:
        pass

    @abstractmethod
    def _init_pressure(self) -> None:
        pass

    @abstractmethod
    def _init_imu(self) -> None:
        pass

    @abstractmethod
    # TODO double check this signature
    def _read_imu(self) -> object:
        return object()

    @abstractmethod
    # TODO double check this signature
    def _get_raw_data(self, is_valid_key: bool, data_key: str) -> dict[str, float]:
        return dict()
