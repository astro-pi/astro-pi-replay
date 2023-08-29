import glob
import logging
import platform
import re
import subprocess
from pathlib import Path

from exif import Image

from astro_pi_executor.resources import get_resource

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

to_index: Path = get_resource("replay") / "photos"

photos = sorted(
    [photo for photo in glob.glob(str(to_index / "*.jpg"))],
    key=lambda photo: int(
        re.findall(r"(image([0-9]+)\.jpg)", str(Path(photo).name))[-1][-1]
    ),
)

photo_datetime_dict = {}
for photo in photos:
    with open(photo, "rb") as f:
        im = Image(f)
        print(im.datetime)
        photo_datetime_dict[im.datetime] = Path(photo).name


def create_df():
    import pandas as pd

    df = pd.DataFrame.from_dict(photo_datetime_dict, orient="index", columns=["name"])
    df["datetime"] = df.index.values
    df["datetime"] = df["datetime"].apply(
        lambda s: pd.to_datetime(s, format="%Y:%m:%d %H:%M:%S")
    )
    df.set_index("datetime", inplace=True)
    df.to_csv(str(to_index / "photo_index.csv"))


def modify_access_times() -> None:
    """Modifies the access times on Unix.
    This is used as part of a trick to generate a video using a variable
    framerate using ffmpeg. This trick is a workaround
    because pyav segfaults for me as of 30/06/23."""
    if platform.system != "Windows":
        raise RuntimeError("Windows not supported")
    for timestamp, photo in photo_datetime_dict.items():
        photo_path: Path = to_index / photo
        timestamp = timestamp.replace(":", "-", 2)
        timestamp = timestamp.replace(" ", "T", 1)
        assert photo_path.exists()
        command_list: list[str] = ["touch", "-d", timestamp, str(photo_path)]
        command: str = " ".join(command_list)
        logger.debug(command)
        subprocess.run(command_list, check=True)  # nosec B603


def create_video() -> None:
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
        "image%d.jpg",
        # Set the framerate to 25
        "-filter:v",
        "fps=25",
        "OrbitAz.mp4",  # mp4 preferred as time-slicable with -ss
    ]
    logger.debug(" ".join(command_list))
    subprocess.run(command_list, check=True)  # nosec B603
