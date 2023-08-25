from pathlib import Path

from uploader import Uploader

# Upload standard assets with:
u = Uploader()
to_include = [
    "photos",
    "data",
    "metadata.json",
]
base = Path("../../src/astro_pi_executor/resources/replay/")
# photos and data
u.upload(
    base,
    include_filter=lambda f: any(
        Path(f).is_relative_to(base / include) for include in to_include
    ),
)
u.upload(
    base,
    include_filter=lambda f: Path(f).is_relative_to(base / "videos"),
    name="videos",
)
