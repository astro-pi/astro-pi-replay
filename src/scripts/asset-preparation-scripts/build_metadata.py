from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import cast
import logging
import numpy as np

from skyfield.positionlib import Geocentric


from skyfield.api import Loader


def _get_iss_coords(
    start: datetime,
    sequence_length: timedelta,
    tle_filepath: Path,
    every_minute = False
) -> Geocentric:
    """
    Returns the ISS positions in the GCRF at each minute from the
    given sequence start time for the required sequence length.
    """
    start = start.replace(tzinfo=timezone.utc)
    logging.debug(f"start: {start}")

    load = Loader(str(tle_filepath.parent.resolve()))

    iss = load.tle_file(str(tle_filepath))[0]
    logging.debug(f"tle epoch: {iss.epoch.utc_iso()}")

    ts = load.timescale()

    divisor = 60 if every_minute else 1
    dts = []
    for i in range(round(sequence_length.total_seconds() / divisor)):
        dt = (start + timedelta(seconds=i)).replace(
                tzinfo=timezone.utc)
        dts.append(dt)

    dts = ts.from_datetimes(dts)
    return iss.at(dts)


def get_iss_altitude_average_km(
    start: datetime,
    sequence_length: timedelta,
    tle_filepath: Path
) -> float:
    coords =  _get_iss_coords(start, sequence_length, tle_filepath)
    return np.mean(coords.subpoint().elevation.km)

def get_iss_wgs84_coordinates(
    start: datetime,
    sequence_length: timedelta,
    tle_filepath: Path
):
    coords = _get_iss_coords(start, sequence_length, tle_filepath, every_minute=True).subpoint()

    lats = np.array(coords.latitude.signed_dms()).T # (N, 4)
    longs = np.array(coords.longitude.signed_dms()).T # (N, 4)
    altitudes = coords.elevation.km # (N,)

    coord_dicts = []
    for i in range(len(altitudes)):
        coord_dict = {}
        for key, point in [
                ("latitude", lats[i,:]), 
                ("longitude", longs[i,:])
        ]:
            s,d,m,sec = point
            coord_dict[key] = {
                "sign": "+" if s > 0 else "-",
                "degrees": d,
                "minutes": m,
                "seconds": sec
            }
        coord_dict["altitude"] = altitudes[i]
        coord_dicts.append(coord_dict)
        return coord_dicts

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         prog=Path(__file__).stem,
#         description="")
#     parser.add_argument("start", help="The start time in ISO format.")
#     parser.add_argument("end", help="The start time in ISO format.")
#     parser.add_argument("tle", type=Path,
#                         help="The path to the TLE file")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    alt = get_iss_altitude_average_km(
        datetime(2023,5,3,3,22,25),
        datetime(2023,5,3,3,32,26),
        Path(__file__).parent / "upsampled-resequenced" \
                / "data" / "iss-23123_20525188.tle"
    )
    print(alt)

