import json
from datetime import datetime
from pathlib import Path
from typing import Any, Union

RESOURCE_DIR: Path = Path(__file__).parent
EXPECTED_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"


def get_resource(path_relative_to_resources_dir: Union[str, Path]) -> Path:
    """
    Finds the given resource in the resource dir.
    """

    path = RESOURCE_DIR / path_relative_to_resources_dir
    if not path.exists():
        raise FileNotFoundError("Could not find " + f"in '{path}'")
    return path


def get_metadata(key: str) -> Any:
    """
    Loads the photo album metadata
    """
    # TODO load the file once
    with (get_resource("OrbitAz") / "metadata.json").open() as f:
        metadata: dict[str, Any] = json.loads(f.read())
        return metadata[key]


def get_start_time() -> datetime:
    return datetime.strptime(get_metadata("start"), EXPECTED_DATETIME_FORMAT)
