from pathlib import Path
from typing import Union

RESOURCE_DIR: Path = Path(__file__).parent


def get_resource(path_relative_to_resources_dir: Union[str, Path]) -> Path:
    """
    Finds the given resource in the resource dir.
    """

    path = RESOURCE_DIR / path_relative_to_resources_dir
    if not path.exists():
        raise FileNotFoundError("Could not find " + f"in '{path}'")
    return path
