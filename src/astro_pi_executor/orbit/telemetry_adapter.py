import functools
import logging
import typing
from datetime import datetime, timezone

import skyfield.api
from skyfield.positionlib import ICRF, Barycentric, Geocentric
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition

from astro_pi_executor.executor import AstroPiExecutor

from .telemetry import ISS as _ISS
from .telemetry import _timescale, coordinates

logger = logging.getLogger(__name__)


class EarthSatellite(skyfield.api.EarthSatellite):
    """Desired subclass type signature"""

    def coordinates(self) -> GeographicPosition:
        return coordinates(self)


def now(executor: AstroPiExecutor) -> Time:
    """
    Gets the relative time since the start from the executor
    and converts it.
    """
    new_time: datetime = executor.time_since_start()
    new_time = new_time.replace(tzinfo=timezone.utc)
    return _timescale.from_datetime(new_time)


def get_patched_iss(executor: AstroPiExecutor = AstroPiExecutor()) -> EarthSatellite:
    """
    Patches the timescale object used by the ISS EarthSatellite so that
    times are relative to the start time of the replayed experiment.
    The start time is stored in the metadata.json file
    """
    print(executor)
    # TODO refactor this and use a private instance attribute instead
    global _timescale
    _timescale.now = functools.partial(now, executor)

    # Override the original at method to ignore the time given and instead
    # use the relative time since the execution started
    original_at: typing.Callable[
        [Time], typing.Union[Barycentric, Geocentric, ICRF]
    ] = _ISS.at

    # TODO The problem is here - the executor patch is not working.
    def at(t) -> typing.Union[Barycentric, Geocentric, ICRF]:
        new_t: Time = now(executor)
        return original_at(new_t)

    _ISS.at = at

    print("Done")
    return typing.cast(EarthSatellite, _ISS)


ISS: EarthSatellite = get_patched_iss()
