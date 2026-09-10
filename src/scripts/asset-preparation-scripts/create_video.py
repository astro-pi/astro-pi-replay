from pathlib import Path
import argparse
import logging
import subprocess
import platform

logger = logging.getLogger(Path(__file__).name)

DEFAULT_INPUT_FILE_PATTERN: str = "photo_%03d.jpg"
DEFAULT_OUTPUT_FILENAME: str = "video.mp4"
DEFAULT_FPS: int = 25


def create_video(input_file_pattern: str, output_file: str, 
                 fps: int, is_dry_run: bool) -> None:
    """Creates an mp4 from the files with a variable
    timestamp, reading the timestamp from the file modified time"""
    # TODO must have just executed modify_access_times.py
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
        "-filter:v",
        f"fps={fps}",
        output_file
    ]

    logger.debug(" ".join(command_list))
    if not is_dry_run:
        subprocess.run(command_list, check=True)  # nosec B603


if __name__ == "__main__":

    if platform.system == "Windows":
        raise RuntimeError("Windows not supported")

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem)
    parser.add_argument("src", type=Path,
                        help="The path in which to search for images")
    parser.add_argument(
            "--input_file_pattern", type=str,
            default=DEFAULT_INPUT_FILE_PATTERN,
            help="The pattern to pass to ffmpeg. " +
            f"Defaults to {DEFAULT_INPUT_FILE_PATTERN.replace("%", "%%")}")
    parser.add_argument(
            "--output_file", type=str,
            default=DEFAULT_OUTPUT_FILENAME,
            help="The output file to write to. " +
            f"Defaults to {DEFAULT_OUTPUT_FILENAME}.")
    parser.add_argument(
            "--fps", type=int,
            default=DEFAULT_FPS,
            help="The FPS to pass to ffmpeg. " +
            f"Defaults to {DEFAULT_FPS}.")
    parser.add_argument(
            "--dry-run", action="store_true",
            help="Print what would be done but don't actually " +
            "action anything.")
    parser.add_argument("--debug", action="store_true",
                        help="Emit debugging messages")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)

    final_pattern = str(args.src / args.input_file_pattern)

    create_video(final_pattern, args.output_file, 
                 args.fps, args.dry_run)


