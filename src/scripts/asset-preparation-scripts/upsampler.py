from pathlib import Path
from typing import DefaultDict, Union, Any
import argparse
import logging
from dataclasses import dataclass

from PIL import Image
from PIL.Image import Resampling
from exif import Image as ExifImage

logger = logging.getLogger(__file__)
StrPath = Union[str,Path]
FULL_RESOLUTION: tuple[int,int] = (4056, 3040)
IMAGE_EXTENSIONS: set[str] = set([".jpg", ".jpeg", ".png"])
DIRECTORY_CMD: str = "directory"
FILE_CMD: str = "file"

@dataclass
class UpscaleJob:
    src: Path
    dest: Path

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


def upsample(src: Path, dest: Path, resolution: tuple[int,int]) -> None:
    logger.debug(f"Upsampling {src} to {dest}")
    original_image: Image.Image = Image.open(src)

    logger.debug(f"Original size: {original_image.size}")
    resized: Image.Image = original_image.resize(
        resolution, Resampling.LANCZOS
    )
    logger.debug(f"Resized size: {resized.size}")
    resized.save(str(dest), exif=original_image.getexif())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem)

    parser.add_argument("src", type=Path, help="The source path " +
                        "- either an image file to upscale or " +
                        "a directory")
    parser.add_argument("dest", type=Path, help="The destination " +
                        "path - must be the same type as src, " +
                        "i.e. a file when src is a file, and " +
                        "directory when src is a directory")
    parser.add_argument("--resolution_x", type=int, 
                        default=FULL_RESOLUTION[0],
                        help="The x component of the resolution " + 
                        "to upscale to. " +
                        f"Defaults to {FULL_RESOLUTION[0]}.")
    parser.add_argument("--resolution_y", type=int, 
                        default=FULL_RESOLUTION[1],
                        help="The y component of the resolution " +
                        "to upscale to " +
                        f"Defaults to {FULL_RESOLUTION[1]}.")
    parser.add_argument("--image_suffixes", nargs="*", type=str,
                        default=IMAGE_EXTENSIONS,
                        help="The suffixes to search for when " +
                        "searching for images to upscale in the " +
                        "given directory. " +
                        f"Defaults to {list(IMAGE_EXTENSIONS)}")
    parser.add_argument("--debug", action="store_true",
                        help="Emit debugging messages")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(level=log_level)
    logging.basicConfig(level=log_level)

    images: list[UpscaleJob]
    if args.src.is_dir():
        if not args.dest.is_dir():
            logger.error(f"Source {args.src} is a directory but dest is a file")
            sys.exit(1)

        images = [UpscaleJob(f, (args.dest / f.name)) 
                  for f in args.src.iterdir()
                  if f.suffix in IMAGE_EXTENSIONS]
    else:
        images = [UpscaleJob(args.src, args.dest)]

    n = len(images)
    logger.info(f"{n} images to upscale")

    for i, image in enumerate(images):
        if i % 10 == 0:
            logger.info(f"Image {i} of {n}")

        upsample(image.src, image.dest, 
                 (args.resolution_x, args.resolution_y))
        modify_exif_tags(image.dest, {
            "pixel_y_dimension": args.resolution_y,
            "image_height": args.resolution_y,
            "pixel_x_dimension": args.resolution_x,
            "image_width": args.resolution_x,
        })

