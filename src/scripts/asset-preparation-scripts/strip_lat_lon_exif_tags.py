from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import Optional

from exif import Image

DEFAULT_GLOB: str = "*.jpg"
TAGS: list[str] = [
    "gps_longitude", 
    "gps_longitude_ref",
    "gps_latitude", 
    "gps_latitude_ref",
    "gps_altitude",
    "gps_altitude_ref"
]


def strip_lat_lon_metadata(
    src: Path,
    glob_pattern: str,
    is_dry_run: bool
) -> None:
    
    for image_path in sorted(src.glob(glob_pattern)):
        image = Image(str(image_path))
        for tag in TAGS:
            if image.get(tag):

                if is_dry_run:
                    logging.debug(
                            f"Deleting {tag} tag from " + \
                            f"{image_path.name}")
                else:
                    image.delete(tag)
        if not is_dry_run:
            with image_path.open("wb") as f:
                f.write(image.get_file())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description="Strips the latitude, longitude, " +
            "and altitude exif metadata from the images " +
            "in the given dir."
    )

    parser.add_argument("src", type=Path, 
                        help="The directory containing the images")
    parser.add_argument("--glob", type=str, 
                        default=DEFAULT_GLOB,
                        help="The default glob pattern to use " +
                        "find images in the src directory. " +
                        f"Defaults to {DEFAULT_GLOB}.")
    parser.add_argument("--dry-run", action="store_true", 
                        default=False,
                        help="Log what would be done but do not " +
                        "actually action anything")
    args = parser.parse_args()


    strip_lat_lon_metadata(args.src, args.glob, args.dry_run)

