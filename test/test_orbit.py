from datetime import datetime
from unittest.mock import patch

import pytest
from skyfield.api import load
from skyfield.toposlib import GeographicPosition

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.orbit import ephemeris
from astro_pi_executor.orbit.telemetry_adapter import get_patched_iss
from astro_pi_executor.resources import get_start_time


def test_ISS_coordinates_returns_coordinates():
    executor = AstroPiExecutor()
    # makes the test deterministic by hardcoding
    # the executor start time and executor elapsed time
    start_time: datetime = get_start_time()
    executor._state._start_time = start_time
    with patch("astro_pi_executor.executor.AstroPiExecutor") as mock_executor:
        ISS = get_patched_iss(mock_executor)
        mock_executor.time_since_start.return_value = start_time
        pos: GeographicPosition = ISS.coordinates()
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


# TODO have to overwrite the skyfield timescale method in general...
# because of the is_sunlit method.
@pytest.mark.skip(reason="Not yet implemented - requires Skyfield stubs")
def test_ISS_is_sunlit():
    ISS = get_patched_iss()
    timescale = load.timescale()
    t = timescale.now()
    if ISS.at(t).is_sunlit(ephemeris):
        print("In sunlight")
