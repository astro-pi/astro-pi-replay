from skyfield import almanac
from skyfield.api import load, wgs84, Topos, Time
from skyfield.positionlib import Geocentric, Barycentric
from skyfield.toposlib import GeographicPosition
from skyfield.vectorlib import VectorSum
from skyfield.units import Angle
from astro_pi_replay.orbit import ephemeris, ISS
from datetime import datetime, timedelta, timezone
from typing import Callable
import typing
import numpy as np

ts = load.timescale()
sun = ephemeris["sun"]
earth = ephemeris["earth"]


d1=datetime(2023,4,21,12,52,59).replace(tzinfo=timezone.utc)
t1 = ts.from_datetime(d1)
iss = ISS(None)


def is_nadir_sunlit_or_in_civil_twilight():
    now: datetime = datetime.now().replace(tzinfo=timezone.utc)
    t = ts.from_datetime(now)
    # 1. Get lat long of ISS now
    pos: Geocentric = typing.cast(Geocentric, iss.at(t)) # TODO make skyfield use types
    nadir_subpoint_sealevel: GeographicPosition = wgs84.subpoint_of(pos)
    # nadir ISS at sea-level
    observer: VectorSum = earth + nadir_subpoint_sealevel
    sun_pos = typing.cast(Barycentric, observer.at(t)).observe(sun)
    alt: Angle = sun_pos.apparent().altaz()[0]
    deg: np.float64 = typing.cast(np.float64, alt.degrees)
    return deg >= -6.0

def is_sunlit() -> bool:
    now: datetime = datetime.now().replace(tzinfo=timezone.utc)
    t: Time = ts.from_datetime(now)
    pos: Geocentric = typing.cast(Geocentric, iss.at(t))
    subpos: GeographicPosition = pos.subpoint()
    nadir_sealevel_topos: Topos = Topos(
        latitude_degrees=subpos.latitude.degrees,
        longitude_degrees=subpos.longitude.degrees)

    is_sunlit: Callable[[Time], bool] = almanac.sunrise_sunset(ephemeris, nadir_sealevel_topos)
    # return is_sunlit(t)
    is_dark_of_night: Callable[[Time], np.ndarray] = almanac.dark_twilight_day(ephemeris, nadir_sealevel_topos)
    return is_dark_of_night(t)[0] == 4 # 4 is sunlit

