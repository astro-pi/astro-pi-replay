import logging
import sys
import typing
from datetime import datetime, timezone

from skyfield.api import Timescale, load
from skyfield.positionlib import Geocentric
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.orbit import ephemeris
from astro_pi_executor.orbit.telemetry_adapter import EarthSatellite, get_patched_iss
from astro_pi_executor.resources import get_start_time

logger = logging.getLogger(__name__)


def trace(frame, event, arg):
    if event == "call":
        filename = frame.f_code.co_filename
        if "skyfield/vectorlib" in filename:
            logger.debug(
                f"skyfield vectorlib method {frame.f_code.co_name} "
                + f"called with args:\n{frame.f_locals}"
            )
            lineno = frame.f_lineno
            # Here I'm printing the file and line number,
            # but you can examine the frame, locals, etc too.
            print("%s @ %s" % (filename, lineno))
    return trace


# TODO broken in CI
def test_ISS_coordinates_returns_coordinates():
    executor = AstroPiExecutor()
    ISS = _get_iss(executor)
    sys.settrace(trace)
    pos: GeographicPosition = ISS.coordinates()
    sys.settrace(None)
    assert pos.latitude.radians == 0.7367376918681074
    assert pos.longitude.radians == 0.6975267490346151
    assert pos.model.name == "IERS2010"
    assert pos.center == 399  # Earth. See:
    # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
    assert pos.elevation.km == 421.6127652392057


def test_iss_is_singleton():
    iss1 = get_patched_iss()
    iss2 = get_patched_iss()
    assert hash(iss1) == hash(iss2)
    assert iss1 is iss2
    assert iss1 == iss2


# TODO broken in CI
def test_ISS_at_ignores_argument_in_favour_of_relative_time():
    executor = AstroPiExecutor()
    ISS: EarthSatellite = _get_iss(executor)
    timescale: Timescale = load.timescale()
    t: Time = timescale.from_datetime(datetime.max.replace(tzinfo=timezone.utc))
    pos: GeographicPosition = typing.cast(Geocentric, ISS.at(t)).subpoint()
    assert pos is not None
    assert pos.latitude.radians == 0.7367376918681074
    assert pos.longitude.radians == 0.6975267490346151
    assert pos.elevation.km == 421.6127652392057


def test_ISS_is_sunlit_works_as_advertised():
    executor = AstroPiExecutor()
    ISS = _get_iss(executor)
    timescale = load.timescale()
    t = timescale.from_datetime(datetime.max.replace(tzinfo=timezone.utc))
    is_sunlit = ISS.at(t).is_sunlit(ephemeris)
    assert is_sunlit


def _get_iss(executor: AstroPiExecutor) -> EarthSatellite:
    """
    Makes the test deterministic by hardcoding
    the executor start time and executor elapsed time
    """
    executor.time_since_start = lambda: get_start_time()
    ISS = get_patched_iss(executor)

    return ISS
