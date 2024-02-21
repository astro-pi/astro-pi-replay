import logging
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Callable, Generator, Generic, Optional, TypeVar, Union

from astro_pi_replay.gpiozero.exc import DeviceClosed

logger = logging.getLogger(__name__)


T1 = TypeVar("T1")


class Factory:
    pass


class RPiGPIOFactory(Factory):
    def __getattribute__(self, _):
        logger.error("This feature is not supported by the Astro Pi Replay tool")

    def is_active(self):
        pass


class InputDevice(Generic[T1]):
    # shared stuff between CPUTemp and MotionSensor
    def __init__(
        self,
        pin: Union[int, str],
        pull_up: Optional[bool],
        active_state: Optional[bool],
        pin_factory: Optional[Factory] = None,
    ):
        self.pin_factory: Factory = (
            RPiGPIOFactory() if pin_factory is None else pin_factory
        )
        self._pin: Union[str, int] = pin
        self._pull_up: bool = False if pull_up is None else pull_up
        self._active_state: bool = True if active_state is None else active_state
        self._closed: bool = False
        self._start_time: datetime = datetime.now()

    @property
    def active_time(self) -> Optional[float]:
        return None

    def close(self) -> None:
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def inactive_time(self) -> Optional[float]:
        return (datetime.now() - self._start_time).seconds

    @property
    def is_active(self) -> bool:
        if self._closed:
            raise DeviceClosed()
        return False

    @property
    def pin(self) -> Union[int, str]:
        return "GPIO" + str(self._pin)

    @property
    def pull_up(self) -> Optional[bool]:
        if self._pull_up is None:
            # self.pin.pull
            raise AttributeError("'NoneType' has no attribute 'pull'")
        return False

    @abstractmethod
    def _default_value(self) -> T1:
        pass

    @property
    def value(self) -> T1:
        if self._closed:
            raise DeviceClosed()
        return self._default_value()

    @property
    def values(self) -> Generator[T1, T1, None]:
        yield self._default_value()

    def _wait_while(
        self, condition: Callable[[], bool], timeout: Optional[float] = None
    ):
        if timeout is None:
            while condition():
                pass
        else:
            start_time: datetime = datetime.now()
            delta: timedelta = start_time - start_time
            while delta.seconds < timeout or condition():
                pass

    def wait_for_active(self, timeout: Optional[float] = None) -> None:
        self._wait_while(lambda: not self.is_active, timeout)

    def wait_for_inactive(self, timeout: Optional[float] = None) -> None:
        self._wait_while(lambda: self.is_active, timeout)

    def when_activated(self, _: Optional[Callable] = None) -> None:
        pass

    def when_deactivated(self, _: Optional[Callable] = None) -> None:
        pass


class MotionSensor(InputDevice):
    """
    Dummy sensor that is never active
    """

    def __init__(
        self,
        pin: Union[int, str],
        pull_up: Optional[bool] = False,
        active_state: Optional[bool] = True,
        queue_len: int = 1,
        threshold: float = 0.5,
        partial: bool = False,
        pin_factory: Optional[Factory] = None,
    ):
        super().__init__(pin, pull_up, active_state, pin_factory)
        self.threshold: float = threshold
        self._queue_len: int = queue_len
        self._partial: bool = partial

        if str(self._pin) != "12":
            logger.warning("Only GPIO12 is available to use on the ISS")
            logger.warning(
                "Your code may be disallowed if another GPIO pin is" + "accessed"
            )

    @property
    def motion_detected(self) -> bool:
        if self._closed:
            raise DeviceClosed()
        return False

    @property
    def pin(self) -> Union[int, str]:
        return "GPIO" + str(self._pin)

    @property
    def queue_len(self) -> int:
        if self._closed:
            raise DeviceClosed()
        return self._queue_len

    def _default_value(self) -> int:
        return 0

    def wait_for_motion(self, timeout: Optional[float] = None) -> None:
        self._wait_while(lambda: not self.motion_detected, timeout)

    def wait_for_no_motion(self, timeout: Optional[float] = None) -> None:
        self._wait_while(lambda: self.motion_detected, timeout)

    def when_motion(self, _: Optional[Callable] = None) -> None:
        pass

    def when_no_motion(self, _: Optional[Callable] = None) -> None:
        pass


class CPUTemperature(InputDevice):
    def __init__(
        self,
        sensor_file: str = "/sys/class/thermal/thermal_zone0/tmp",
        min_temp: float = 0.0,
        max_temp: float = 1.0,
        threshold: float = 80.0,
        event_delay: float = 5,
        pin_factory: Optional[Factory] = None,
    ):
        super().__init__("cpu", None, True, pin_factory)  # TODO cpu is not right
        self.sensor_file: str = sensor_file
        self.min_temp: float = min_temp
        self.max_temp: float = max_temp
        self.threshold: float = threshold
        self.event_delay: float = event_delay

    def _default_value(self) -> float:
        # 0.35536999999999996
        # sample 0.36024 (36 degrees)
        return 0.36024

    @property
    def temperature(self) -> float:
        if self._closed:
            raise DeviceClosed()
        return self._default_value()
