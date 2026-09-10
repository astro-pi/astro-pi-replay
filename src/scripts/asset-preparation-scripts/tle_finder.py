# Uses space-track.org to find the nearest TLE to the 
# given daterange.
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Union
import argparse
import logging
import subprocess
import sys
import json

import spacetrack
import spacetrack.operators as op


logger = logging.getLogger(Path(__file__).name)

ISS_ZARYA_NORAD_CAT_ID: int = 25544
SECONDS_IN_DAY: int = 86400 # 60*60*24


def get_start_and_end_from_file(csv_file: Path) -> tuple[datetime,datetime]:
    with Path(args.csv_file).open() as f:
        lines = f.read().strip().splitlines()
    header_line = lines[0]
    delimiter = ","
    headers = header_line.split(delimiter)
    datetime_header = "datetime"
    if datetime_header not in headers:
        logger.error("Supplied csv does not " +
        f"include {datetime_header} header")
        sys.exit(1)

    datetime_index = headers.index(datetime_header)
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None
    for line in lines[1:]:
        cols = line.split(delimiter)
        dt = datetime.fromisoformat(cols[datetime_index])
        if min_date is None or dt < min_date:
            min_date = dt
        if max_date is None or dt > max_date:
            max_date = dt
    if min_date is None or max_date is None:
        logger.error(f"File {csv_file} does not contain dates")
        sys.exit(1)
    return min_date, max_date

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


def get_tle_list(start: Union[datetime,date], end: Union[datetime,date]) -> list[dict]:
    logger.debug(f"Searching for best TLE to fit {start} - {end}")

    password = subprocess.run(
        ["op", "read", "op://Employee/Spacetrack/password"],
        check=True, text=True, capture_output=True
    ).stdout.strip()
    with spacetrack.SpaceTrackClient(
            identity="geraint.ballinger@raspberrypi.org", 
            password=password) as st:
        response = st.gp_history(
            norad_cat_id=ISS_ZARYA_NORAD_CAT_ID,
            epoch=op.inclusive_range(start, end),
            orderby="EPOCH asc",
            format="json",
        )
        return json.loads(response)



def find_nearest_tle(
    tle_list: list[dict], 
    midpoint: datetime
) -> dict:
    if not tle_list:
        raise ValueError()
    smallest_diff: Optional[timedelta] = None
    best_index: Optional[int] = None

    for i, tle_dict in enumerate(tle_list):
        # Space-Track JSON format stores the epoch as an ISO string
        epoch = datetime.fromisoformat(tle_dict["EPOCH"])
        
        diff = abs(epoch - midpoint)
        
        if smallest_diff is None or diff < smallest_diff:
            smallest_diff = diff
            best_index = i

    if best_index is not None:
        logger.info(f"Minimised diff is: {smallest_diff}")
        best = tle_list[best_index]
        logger.info(f"Epoch: {best['EPOCH']}")
        return tle_list[best_index]
    else:
        raise ValueError()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

#     with spacetrack.SpaceTrackClient(identity="geraint.ballinger@raspberrypi.org", password=password) as st:
#         tles = st.gp_history(
#             norad_cat_id=25544,
#             epoch=op.inclusive_range(min_date, max_date),
#             orderby="EPOCH asc",
#             format="json",
#         )

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description=" ".join([
                        "python3", Path(__file__).name, 
                        "'2023-05-03 03:22:25'",
                        "'2023-05-03 03:32:26'"
            ])
    )
    parser.add_argument("--csv-file", type=Path, 
                        help="Path to csv file (photos.csv) " +
                        "containing the photo datetimes")
    parser.add_argument("--start",
                        help="The sequence start in ISO 8601 format.")
    parser.add_argument("--end",
                        help="The sequence end in ISO 8601 format.")
    parser.add_argument("--debug", action="store_true",
                        help="Emit debugging messages")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)
    spacetrack_logger = logging.getLogger("httpcore")
    spacetrack_logger.setLevel(log_level)

    if all([a is None for a in [args.csv_file, args.start, args.end]]):
           logger.error(
               "Please specify either a csv file or " +
               "start and end datetimes."
           )
           sys.exit(1)

    start: datetime
    end: datetime
    if args.csv_file:
        start, end = get_start_and_end_from_file(args.csv_file)
    else:
        start = datetime.fromisoformat(args.start)
        end = datetime.fromisoformat(args.end)

    midpoint = start + ((end - start) / 2)
    # midpoint_epoch = _datetime_to_epoch(midpoint)
    # logger.debug(f"midpoint: {midpoint_epoch}")

    tles = get_tle_list(start, end)
    if len(tles) == 0:
        logger.warning("Could not find TLEs within the supplied timeframe")
        logger.info("Broadening search to 24h window...")
        tles = get_tle_list(
                start.date(),
                end.date() + timedelta(days=1))
    if len(tles) > 0:
        tle = find_nearest_tle(tles, midpoint)[0]
        if len(tle) > 0:
            for key in ["TLE_LINE0","TLE_LINE1","TLE_LINE2"]:
                print(tle[key])
            # iss-23123_20525188.tle
        else:
            logger.error("No TLE data found in range")

            

