from pathlib import Path
import os

from astro_pi_replay import PROGRAM_NAME, __version__


RESOURCE_DIR: Path = Path(__file__).parent
EXPECTED_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
REPLAY_DIR_ENV_VAR: str = f"{PROGRAM_NAME.upper()}_REPLAY_DIR"
REPLAY_SEQUENCE_ENV_VAR: str = f"{PROGRAM_NAME.upper()}_REPLAY_SEQUENCE"
SENSE_HAT_CSV_FILE: Path = Path("data") / "data.csv"
METADATA_FILE_NAME: str = "metadata.json"
SEQUENCES_FILENAME: str = "sequences.csv"
SEQUENCES_FILE: Path = RESOURCE_DIR / SEQUENCES_FILENAME

GPG_EMAIL = "enquiries@astro-pi.org"
BUCKET_NAME: str = "static.raspberrypi.org"
BUCKET_URL: str = os.environ.get(
    f"__{PROGRAM_NAME.upper()}_BUCKET_URL", f"https://{BUCKET_NAME}"
)
URL_BASE: str = f"{BUCKET_URL}/files/astro-pi"
GPG_KEY_URL = f"{URL_BASE}/astro-pi.gpg"  # TODO add key-rotation
url_prefix: str = f"{URL_BASE}/{PROGRAM_NAME}"
asset_url: str = f"{url_prefix}/assets"
asset_prefix: str = str(Path(asset_url).relative_to(Path(BUCKET_URL)))
version_url_prefix: str = f"{url_prefix}/{__version__}"

ONE_HOUR: int = 60 * 60

