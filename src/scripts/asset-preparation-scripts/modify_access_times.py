from datetime import datetime
from pathlib import Path
import argparse
import logging
import subprocess
import platform

DELIMITER: str = ","
PHOTO_CSV_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
# touch -d has the format YYYY-MM-DDThh:mm:SS[.frac]
TOUCH_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S"


def modify_access_times(
    csv_file: Path, 
    images_dir: Path,
    is_dry_run: bool
) -> None:
    with csv_file.open() as f:
        lines: list[str] = f.read().strip().splitlines()

    for line in lines[1:]:

        line_elements: list[str] = line.split(DELIMITER)
        name: str = line_elements[1]

        image_file: Path = images_dir / name
        dt: datetime = datetime.strptime(
                line_elements[0], PHOTO_CSV_DATETIME_FORMAT)

        # Use the 'touch' command
        command_list: list[str] = [
                "touch", "-d", 
                dt.strftime(TOUCH_TIMESTAMP_FORMAT),
                str(image_file)]

        command: str = " ".join(command_list)

        if is_dry_run:
            logging.info(command)
        else:
            logging.debug(f"Executing {command}")
            subprocess.run(command_list, check=True, text=True)


def create_video(
    input_file_pattern: str = "image%d.jpg",
    output_file: str = "video.mp4",
    fps: int = 25
) -> None:
    """Creates an mp4 from the files with a variable
    timestamp, reading the timestamp from the file modified time"""
    if platform.system() != "Linux":
        raise RuntimeError("This method only works on Linux")
    command_list: list[str] = [
        "ffmpeg",
        # Set input format to image2
        "-f",
        "image2",
        # use the file access times as the frame timestamps
        "-ts_from_file",
        "2",
        "-i",
        input_file_pattern,
        # Set the framerate to 25
        "-filter:v",
        f"fps={fps}",
        output_file
    ]
    logging.debug(" ".join(command_list))
    subprocess.run(command_list, check=True)  # nosec B603


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    if platform.system == "Windows":
        raise RuntimeError("Windows not supported")

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem)
    parser.add_argument("csv_file", type=Path,
                        help="The csv file to read datetimes from.")
    parser.add_argument(
            "photo_dir", type=Path,
            help="The directory in which photos listed in " +
            "the csv file are stored")
    parser.add_argument(
            "--dry-run", action="store_true",
            help="Print what would be done but don't actually " +
            "action anything.")

    args = parser.parse_args()

    modify_access_times(
            args.csv_file, args.photo_dir, args.dry_run)


