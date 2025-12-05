"""
Uploads the assets in the current src/astro_pi_replay/resources/replay
Usage (from the src directory):

    python3 -m scripts.upload_assets
"""
import dataclasses
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Union

import exif

from astro_pi_replay.resources.downloader import asset_url, get_replay_dir

from .uploader import GPS_TAGS, Uploader

CURRENT_DIR = Path(__file__).parent
PROJECT_DIR = CURRENT_DIR.parent.parent
SEQUENCE_IDS_DEST: str = "sequence_ids"
UPLOAD_VIDEOS_DEST: str = "upload_videos"
IMAGE_SUFFIXES: set[str] = set(["jpeg", "jpg", "png"])
replay_dir: Path = get_replay_dir()


@dataclasses.dataclass
class ValidatedArguments:
    """
    Class represented the validated arguments
    """

    sequences: list[Path]
    upload_video_zip: bool
    raw_only: bool
    zips_only: bool


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Uploads the assets in the current "
        + "src/astro_pi_replay/resources/replay directory."
    )
    parser.add_argument(
        "--sequence-ids",
        dest=SEQUENCE_IDS_DEST,
        default=[],
        help="Comma separated list of sequence ids to upload. By default, "
        + "all detected sequences in the replay dir will be uploaded",
    )
    parser.add_argument(
        "--upload-videos",
        dest=UPLOAD_VIDEOS_DEST,
        action="store_true",
        default=False,
        help="Provide this flag to upload videos. When not provided "
        + "the script will just upload photos",
    )
    parser.add_argument(
        "--zips_only",
        action="store_true",
        default=False,
        help="Only upload the zip files (and skip uploading " +
        "the raw uncompressed assets)."
    )
    parser.add_argument(
        "--raw-only",
        action="store_true",
        default=False,
        help="Only upload the sequences in uncompressed " +
        "form (and skip uploading the zipped assets)."
    )
    return parser.parse_args()


def validate_args(args: Namespace, sequences: list[Path]) -> ValidatedArguments:
    for required_attr in [SEQUENCE_IDS_DEST, UPLOAD_VIDEOS_DEST]:
        if not hasattr(args, SEQUENCE_IDS_DEST):
            raise RuntimeError(f"Missing required argument {required_attr}")
    args_as_dict: dict = vars(args)
    to_keep_union: Union[str, list[str]] = args_as_dict[SEQUENCE_IDS_DEST]
    to_keep_list: list[str]
    if isinstance(to_keep_union, list):
        to_keep_list = to_keep_union
        if len(to_keep_list) == 0:
            to_keep_list = [seq.name for seq in sequences]
    else:
        to_keep_list = to_keep_union.split(",")
    to_keep: set[str] = set([sequence.strip() for sequence in to_keep_list])
    if len([seq for seq in to_keep if len(seq) == 0]) > 0:
        raise RuntimeError(f"Syntax error in {SEQUENCE_IDS_DEST}")
    filtered: list[Path] = [
        collected_seq for collected_seq in sequences if collected_seq.name in to_keep
    ]
    print(filtered)

    return ValidatedArguments(
        sequences=filtered, 
        upload_video_zip=args_as_dict[UPLOAD_VIDEOS_DEST],
        raw_only=args.raw_only,
        zips_only=args.zips_only,
    )


def collect_sequences() -> list[Path]:
    """
    Collects sequences in the {replay_dir}/VIS and {replay_dir}/IR
    directories.
    """
    sequences: list[Path] = []
    for photography_type in os.listdir(replay_dir):
        sequences_root: Path = replay_dir / photography_type
        if not sequences_root.is_dir():
            continue  # skip files that are not directories
        sequence_id: str
        for sequence_id in os.listdir(sequences_root):
            # Upload the photos and videos separately
            sequence_base: Path = sequences_root / sequence_id
            sequences.append(sequence_base)
    return sequences


def upload_zips(validated_args: ValidatedArguments) -> None:
    # Upload standard assets with:
    u = Uploader()
    to_include = [
        "photos",
        "data",
        "metadata.json",
    ]

    for sequence_base in validated_args.sequences:
        s3_url = asset_url.replace("https://", "s3://") + "/"

        for img in (sequence_base / "photos").iterdir():
            if any([img.name.endswith(suffix) for suffix in IMAGE_SUFFIXES]):
                im: exif.Image = exif.Image(str(img))
                if any(im.get(tag) for tag in GPS_TAGS):
                    raise RuntimeError("GPS exif tags are populated")

        if validated_args.zips_only or not validated_args.raw_only:
            u.upload_zip(
                sequence_base,
                include_filter=lambda f: any(
                    Path(f).is_relative_to(sequence_base / include)
                    for include in to_include
                ),
                url=s3_url,
            )
            if validated_args.upload_video_zip:
                u.upload_zip(
                    sequence_base,
                    include_filter=lambda f: Path(f).is_relative_to(
                        sequence_base / "videos"
                    ),
                    zip_name=sequence_base.name + "_videos",
                    url=s3_url,
                )
        if validated_args.raw_only or not validated_args.zips_only:
            u.upload_raw(
                sequence_base,
                url=s3_url + f"{sequence_base.name}/"
            )


def _main(args: Namespace) -> None:
    collected_sequences: list[Path] = collect_sequences()
    validated: ValidatedArguments = validate_args(args, sequences=collected_sequences)
    upload_zips(validated)


def main() -> None:
    _main(parse_args())

if __name__ == "__main__":
    main()
