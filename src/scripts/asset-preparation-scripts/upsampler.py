from pathlib import Path
from typing import Union, Any
import argparse
import logging

from PIL import Image
from PIL.Image import Resampling
from exif import Image as ExifImage


StrPath = Union[str,Path]
FULL_RESOLUTION: tuple[int,int] = (4056, 3040)


def modify_exif_tags(dest: StrPath, tags: dict[str,Any]) -> None:
    """
    Set the given tags on the dest image, if they have already
    been set.
    If the tag is not found, the tag is not set.
    """
    image = ExifImage(str(dest))
    for tag, value in tags.items():
        if image.get(tag, None):
            image.set(tag, value)
    Path(dest).write_bytes(image.get_file())


def upsample(src: Path, dest: Path) -> None:
    logging.info(f"Upsampling {src} to {dest}")
    original_image: Image.Image = Image.open(src)

    logging.info(f"Original size: {original_image.size}")
    resized: Image.Image = original_image.resize(
        FULL_RESOLUTION, Resampling.LANCZOS
    )
    logging.info(f"Resized size: {resized.size}")
    resized.save(str(dest), exif=original_image.getexif())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem)
    parser.add_argument("src", type=Path, help="The source image")
    parser.add_argument("dest", type=Path, help="The destination path")

    args = parser.parse_args()

    upsample(args.src, args.dest)
    modify_exif_tags(args.dest, {
        "pixel_y_dimension": FULL_RESOLUTION[1],
        "image_height": FULL_RESOLUTION[1],
        "pixel_x_dimension": FULL_RESOLUTION[0],
        "image_width": FULL_RESOLUTION[0],
    })

