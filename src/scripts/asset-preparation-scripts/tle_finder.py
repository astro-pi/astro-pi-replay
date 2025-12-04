# Uses space-track.org to find the nearest TLE to the 
# given daterange.
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse
import logging
import urllib.parse

ISS_ZARYA_NORAD_CAT_ID: int = 25544
SECONDS_IN_DAY: int = 86400 # 60*60*24


def _datetime_to_epoch(d: datetime) -> str:
    """
    Returns the given datetime object as a TLE epoch string.
    """
    epoch_year = str(d.year)[-2:]
    day_of_year = str(d.timetuple().tm_yday)

    midnight = d.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = d - midnight
    fractional_day = str(round(
        delta.total_seconds() / SECONDS_IN_DAY, 6))[2:]

    to_return = epoch_year + day_of_year + "." + fractional_day

    return to_return
    # d
    # # Epoch year (last two digits of year)	
# 8	21–32	Epoch (day of the year and fractional portion of the day)	

    # return ""


def get_tle_list(start: datetime, end: datetime) -> list[str]:
    logging.debug(f"Searching for best TLE to fit {start} - {end}")

    # 2023-05-03
    # https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/25544/EPOCH/>2023-05-03,<2023-05-04/orderby/EPOCH asc/limit/5/format/tle/emptyresult/show


    protocol: str = "https"
    origin: str = "www.space-track.org"
    limit: int  = 5
    pathname = f"basicspacedata/query" + \
        "/class/tle" + \
        f"/NORAD_CAT_ID/{ISS_ZARYA_NORAD_CAT_ID}" + \
        f"/EPOCH/>{start.date().isoformat()}," + \
        f"<{end.date().isoformat()}" + \
        "/orderby/EPOCH asc" + \
        f"/limit/{limit}/" + \
        "/format/tle/emptyresult/show"

    unencoded_url: str = f"{protocol}://{origin}/{pathname}"

    logging.debug(unencoded_url)

    encoded_url: str = urllib.parse.quote(unencoded_url)
    logging.debug(encoded_url)
    return [] # TODO



def find_nearest_tle(
    tle_list: list[str], 
    midpoint: str
) -> list[str]:
    midpoint_epoch = float(midpoint)

    smallest: Optional[tuple[float, int]] = None

    for i in range(len(tle_list) // 2):
        first_line = tle_list[i*2]
        epoch = float(first_line.split()[2])
        diff = abs(epoch - midpoint_epoch)
        if smallest is None:
            smallest = (diff, i)
        if smallest is not None:
            smallest_diff, _ = smallest
            if diff < smallest_diff:
                smallest = (diff,i)

    if smallest is None:
        return []
    else:
        _, i = smallest
        return tle_list[i*2:(i*2)+1]
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description=" ".join([
                        "python3", Path(__file__).name, 
                        "'2023-05-03 03:22:25'",
                        "'2023-05-03 03:32:26'"
            ])
    )
    parser.add_argument("start",
                        help="The sequence start in ISO 8601 format.")
    parser.add_argument("end",
                        help="The sequence end in ISO 8601 format.")

    args = parser.parse_args()
    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)

    midpoint = start + ((end - start) / 2)
    midpoint_epoch = _datetime_to_epoch(midpoint)
    logging.debug(f"midpoint: {midpoint_epoch}")

    tles = get_tle_list(start, end)
    tle = find_nearest_tle(tles, midpoint_epoch)

