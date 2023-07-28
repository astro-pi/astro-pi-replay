import functools
import logging
import typing
from datetime import datetime, timezone

import skyfield.api
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
    logger.info("PATCHED")
    new_time: datetime = executor.time_since_start()
    new_time = new_time.replace(tzinfo=timezone.utc)
    return _timescale.from_datetime(new_time)


def get_patched_iss(executor: AstroPiExecutor = AstroPiExecutor()) -> EarthSatellite:
    """
    Patches the timescale object used by the ISS EarthSatellite so that
    times are relative to the start time of the replayed experiment.
    The start time is stored in the metadata.json file
    """
    global _timescale
    _timescale.now = functools.partial(now, executor)
    return typing.cast(EarthSatellite, _ISS)


ISS: EarthSatellite = get_patched_iss()
