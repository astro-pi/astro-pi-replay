from datetime import datetime, timezone
from pathlib import Path
import argparse
import logging
from skyfield.api import Loader
from numpy.linalg import norm



PHOTO_CSV_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

def get_actual_times(
    photo_csv: Path, tle_filepath: Path
) -> None:

    load = Loader(str(tle_filepath.parent.resolve()))
    ts = load.timescale()
    iss = load.tle_file(str(tle_filepath))[0]

    with photo_csv.open() as f:
        lines = f.read().strip().splitlines()


    for line in lines[1:]:
        dt: datetime = datetime.strptime(
            line.split(",")[0], 
            PHOTO_CSV_DATETIME_FORMAT
        )

        pos = iss.at(ts.from_datetime(dt.replace(tzinfo=timezone.utc)))
        v = pos.velocity.km_per_s
        print(norm(v))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description="Gets the actual speeds of the " +
            "ISS for each photo, as reported by the given TLE file."
    )
    parser.add_argument(
            "photo_csv", type=Path,
           help="The path to the CSV file containing the " +
           "indexed photos")
    parser.add_argument(
            "tle", type=Path, 
            help="The path to the TLE file to use")
    args = parser.parse_args()
    
    get_actual_times(args.photo_csv, args.tle)

