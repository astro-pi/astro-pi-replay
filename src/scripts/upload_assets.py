import os
from pathlib import Path

from uploader import Uploader

from astro_pi_replay.downloader import url_prefix

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
    sequence_id: str
    for sequence_id in os.listdir(sequences_root):
        # Upload the photos and videos separately
        sequence_base: Path = sequences_root / sequence_id

        url = url_prefix.replace("https://", "s3://") + "/"
        # photos and data
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
