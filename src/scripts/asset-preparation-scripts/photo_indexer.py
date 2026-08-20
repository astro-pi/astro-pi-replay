from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import Optional

from exif import Image


FULL_RESOLUTION: tuple[int,int] = (4056, 3040)
DEFAULT_GLOB: str = "*.jpg"

def generate_photo_index_csv(
    src_dir: Path, 
    glob: str,
    with_lat_lon: bool
) -> None:
    logging.info(f"src_dir: {src_dir}")
    logging.info(f"glob: {glob}")

    all_have_lat_lon: Optional[bool] = None
    headers = ["datetime","name","latitude_dms","longitude_dms"]

    inconsistent_lat_lon_message: str = "Not all images have " + \
        "latitude and longitude coordinates"

    lines: list[list[str]] = []

    for image_path in sorted(src_dir.glob(glob)):
        im = Image(str(image_path))
        line = []

        datetime_digitized = datetime.strptime(
            im.get("datetime_digitized"),
            "%Y:%m:%d %H:%M:%S")
        line.append(datetime_digitized.strftime("%Y-%m-%d %H:%M:%S"))

        line.append(image_path.name)

        if with_lat_lon:
            # (65.0, 34.0, 54.8)
            gps_latitude = im.get("gps_latitude")
            gps_longitude = im.get("gps_longitude")

            if gps_latitude is not None and \
                    gps_longitude is not None:

                if all_have_lat_lon is None:
                    # expect all lines to have lat-lon
                    all_have_lat_lon = True
                elif not all_have_lat_lon:
                    # expect all lines to have lat-lon
                    raise RuntimeError(inconsistent_lat_lon_message)

                # collect the latitude and longitude
                line.append("-".join(map(str, list(gps_latitude))))
                line.append("-".join(map(str, list(gps_longitude))))

            else:
                if all_have_lat_lon is None:
                    # expect all lines to not have lat-lon
                    all_have_lat_lon = False
                elif all_have_lat_lon:
                    raise RuntimeError(inconsistent_lat_lon_message)

        lines.append(line)
    

    if len(lines) > 0:
        lines.insert(0, headers)
    # if we got here, there was consistency in lat-lon
    for line in lines:
        # truncate if no lat-lon
        upper_limit = len(line) if all_have_lat_lon else 2
        print(",".join(line[:upper_limit]))




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description="Generates the photo_index.csv file " +
            "by globbing the given src dir using the given " +
            "glob pattern, sorting alphanumerically (ascending) " +
            "and then collecting the required metadata. Outputs "
            "the csv to stdout."
    )

    parser.add_argument("src", type=Path, 
                        help="The directory containing the images")
    parser.add_argument("--glob", type=str, 
                        default=DEFAULT_GLOB,
                        help="The default glob pattern to use " +
                        "find images in the src directory. " +
                        f"Defaults to {DEFAULT_GLOB}.")
    parser.add_argument("--with-lat-lon", action="store_true", 
                        default=False,
                        help="Include columns for the latitude " +
                        "and longitude values (when this is " +
                        "provided by every image).")
    args = parser.parse_args()

    generate_photo_index_csv(
            args.src, args.glob, args.with_lat_lon)


