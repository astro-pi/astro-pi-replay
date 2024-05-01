"""
Uploads the assets in the current src/astro_pi_replay/resources/replay
"""
import os
from pathlib import Path

import exif
from uploader import GPS_TAGS, Uploader

from astro_pi_replay.downloader import asset_prefix

# Upload standard assets with:
u = Uploader()
to_include = [
    "photos",
    "data",
    "metadata.json",
]
base = Path("../../src/astro_pi_replay/resources/replay/")

photography_type: str
for photography_type in os.listdir(base):
    sequences_root: Path = base / photography_type
    if not sequences_root.is_dir():
        continue  # skip files that are not directories
    sequence_id: str
    for sequence_id in os.listdir(sequences_root):
        # Upload the photos and videos separately
        sequence_base: Path = sequences_root / sequence_id

        url = asset_prefix.replace("https://", "s3://") + "/"

        for img in (sequence_base / "photos").iterdir():
            if (
                img.name.endswith("jpg")
                or img.name.endswith("jpeg")
                or img.name.endswith("png")
            ):
                im: exif.Image = exif.Image(str(img))
                if any(im.get(tag) for tag in GPS_TAGS):
                    raise RuntimeError("GPS exif tags are populated")

        u.upload(
            sequence_base,
            include_filter=lambda f: any(
                Path(f).is_relative_to(sequence_base / include)
                for include in to_include
            ),
            url=url,
        )
        # videos
        u.upload(
            sequence_base,
            include_filter=lambda f: Path(f).is_relative_to(sequence_base / "videos"),
            zip_name=sequence_base.name + "_videos",
            url=url,
        )
