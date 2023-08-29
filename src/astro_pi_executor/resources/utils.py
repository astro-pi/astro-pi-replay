import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from astro_pi_executor import PROGRAM_NAME

RESOURCE_DIR: Path = Path(__file__).parent
EXPECTED_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
REPLAY_DIR_ENV_VAR = f"{PROGRAM_NAME.upper()}_REPLAY_DIR"


def get_resource(path_relative_to_resources_dir: Union[str, Path]) -> Path:
    """
    Finds the given resource in the resource dir.
    """

    path = RESOURCE_DIR / path_relative_to_resources_dir
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path_relative_to_resources_dir}" + f" in '{RESOURCE_DIR}'"
        )
    return path


def get_replay_dir() -> Path:
    replay_dir: Optional[str] = os.environ.get(REPLAY_DIR_ENV_VAR)
    if replay_dir is not None:
        return get_resource(replay_dir)
    return get_resource("replay")


def get_metadata(key: str) -> Any:
    """
    Loads the photo album metadata
    """
    # TODO load the file once
    with (get_replay_dir() / "metadata.json").open() as f:
        metadata: dict[str, Any] = json.loads(f.read())
        return metadata[key]


def get_start_time() -> datetime:
    return datetime.strptime(get_metadata("start"), EXPECTED_DATETIME_FORMAT)
