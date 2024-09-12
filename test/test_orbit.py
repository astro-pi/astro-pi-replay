import typing
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from skyfield.api import Timescale, load
from skyfield.positionlib import Geocentric
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition

from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.orbit import ISS, ephemeris
from astro_pi_replay.resources import get_start_time


def test_ISS_coordinates_returns_coordinates():
    executor = AstroPiExecutor()
    start_time = get_start_time()
    with patch.object(executor, "time_since_start", return_value=start_time):
        iss = ISS(executor)
        with patch(
            "skyfield.api.EarthSatellite.at", side_effect=super(type(iss), iss).at
        ) as mock_at:
            pos: GeographicPosition = iss.coordinates()

            mock_at.assert_called_once()
            assert pos.latitude.radians == pytest.approx(0.7339144102710123)
            assert pos.longitude.radians == pytest.approx(0.7033707692532865)
            assert pos.model.name == "IERS2010"
            assert pos.center == 399  # Earth. See:
            # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
            assert pos.elevation.km == pytest.approx(421.4205875887477)


def test_ISS_at_ignores_argument_in_favour_of_relative_time():
    executor = AstroPiExecutor()
    start_time = get_start_time()
    with patch.object(executor, "time_since_start", return_value=start_time):
        iss = ISS(executor)
        timescale: Timescale = load.timescale()
        t: Time = timescale.from_datetime(datetime.max.replace(tzinfo=timezone.utc))
        with patch(
            "skyfield.api.EarthSatellite.at", side_effect=super(type(iss), iss).at
        ) as mock_at:
            pos: GeographicPosition = typing.cast(Geocentric, iss.at(t)).subpoint()
            mock_at.assert_called_once()
            assert pos.latitude.radians == pytest.approx(0.7339144102710123)
            assert pos.longitude.radians == pytest.approx(0.7033707692532865)
            assert pos.elevation.km == pytest.approx(421.4205875887477)
            assert isinstance(mock_at.call_args.args[0], Time)
            assert mock_at.call_args.args[0] != t


def test_ISS_is_sunlit_works_as_advertised():
    executor = AstroPiExecutor()
    start_time = get_start_time()
    with patch.object(executor, "time_since_start", return_value=start_time):
        iss = ISS(executor)
        timescale: Timescale = load.timescale()
        t: Time = timescale.from_datetime(datetime.max.replace(tzinfo=timezone.utc))
        with patch(
            "skyfield.api.EarthSatellite.at", side_effect=super(type(iss), iss).at
        ) as mock_at:
            is_sunlit = iss.at(t).is_sunlit(ephemeris)
            mock_at.assert_called_once()
    assert is_sunlit
