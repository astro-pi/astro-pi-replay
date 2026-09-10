from pathlib import Path
import argparse
import logging
import shutil


DEFAULT_GLOB: str = "*.jpg"
DEFAULT_STEM: str = "photo_"


def resequence(
    src: Path, 
    dest_dir: Path, 
    glob: str, 
    stem: str,
    is_one_indexed: bool,
    is_dry_run: bool
) -> None:
    assert src.exists() and src.is_dir()
    if not dest_dir.exists() and not is_dry_run:
        dest_dir.mkdir(parents=True)
    elif not is_dry_run:
        assert dest_dir.is_dir()

    logging.info(f"src: {src}")
    logging.info(f"dest_dir: {dest_dir}")
    logging.info(f"glob: {glob}")
    if is_one_indexed:
        logging.info("One-indexing enabled")
    if is_dry_run:
        logging.info("Dry run mode...")

    sorted_images: list[Path] = sorted(src.glob(glob))
    n = len(str(len(sorted_images)))

    stem_format_string = stem + "{:0" + str(n) + "d}"

    for i, image_path in enumerate(sorted_images):
        ix = i+1 if is_one_indexed else i
        filename: str = stem_format_string.format(ix) + \
                image_path.suffix
        dest  = dest_dir / filename

        if is_dry_run:
            logging.debug(f"Copy {image_path} to {dest}")
        else:
            logging.debug(f"Copying {image_path} to {dest}...")
            shutil.copy2(image_path, dest)
    logging.debug("Completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description="Re-sequences the images in src to dest by using the specified glob pattern to find the images, sorting them in ascending order, and then restarting them from 0"
    )
    parser.add_argument(
            "src", type=Path,
           help="The directory containing the images to re-sequence")
    parser.add_argument(
            "dest", type=Path, 
            help="The path to the directory in which the " +
            "re-sequenced images will be placed. The directory " +
            "will be created if it doesn't exist")
    parser.add_argument(
            "--glob", type=str,
            default=DEFAULT_GLOB,
            help="The glob pattern used to find the images. " +
            f"Defaults to {DEFAULT_GLOB}."
    )
    parser.add_argument(
            "--stem", type=str,
            default=DEFAULT_STEM,
            help="The stem to use for images in the new " +
            f"sequence. Defaults to {DEFAULT_STEM}."
    )
    parser.add_argument(
            "--one-index", action="store_true",
            default=False,
            help="Whether to one-index the re-sequenced " +
            "images. By default, the images are zero-indexed."
    )
    parser.add_argument(
            "--dry-run", action="store_true",
            default=False,
            help="Print what would happen but do not actually " +
            "action anything"
    )
    args = parser.parse_args()

    resequence(args.src, args.dest, args.glob,
               args.stem, args.one_index, args.dry_run)
