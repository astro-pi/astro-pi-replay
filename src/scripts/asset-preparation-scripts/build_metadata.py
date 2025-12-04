from datetime import datetime, timezone
from pathlib import Path
from typing import cast
import logging

from skyfield.positionlib import Geocentric


from skyfield.api import Loader

def get_altitude_average_km(
    start: datetime, 
    end: datetime,
    tle_filepath: Path
) -> float:
    start = start.replace(tzinfo=timezone.utc)
    end  = end.replace(tzinfo=timezone.utc)

    logging.debug(f"start: {start}")
    logging.debug(f"end: {end}")

    load = Loader(str(tle_filepath.parent.resolve()))

    iss = load.tle_file(str(tle_filepath))[0]
    logging.debug(f"tle epoch: {iss.epoch.utc_iso()}")

    ts = load.timescale()

    start_elevation: float = cast(
        float,
        cast(Geocentric, 
             iss.at(ts.from_datetime(start))).subpoint().elevation.km)
    end_elevation: float = cast(
        float,
        cast(Geocentric,
             iss.at(ts.from_datetime(end))).subpoint().elevation.km)

    logging.debug(f"elevation at {start}: {start_elevation}")
    logging.debug(f"elevation at {end}: {end_elevation}")

    return (start_elevation + end_elevation) / 2


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
    alt = get_altitude_average_km(
        datetime(2023,5,3,3,22,25),
        datetime(2023,5,3,3,32,26),
        Path(__file__).parent / "upsampled-resequenced" \
                / "data" / "iss-23123_20525188.tle"
    )
    print(alt)

