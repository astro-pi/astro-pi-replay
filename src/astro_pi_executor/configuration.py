import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from astro_pi_executor import PROGRAM_NAME

logger = logging.getLogger(__name__)

CONFIG_FILE: Path = Path.home() / f".{PROGRAM_NAME}" / "config.json"


@dataclass
class Configuration:
    """
    Persistent configuration stored in the home directory.
    """

    no_wait: bool
    debug: bool

    @staticmethod
    def _from_json(jstr: str) -> "Configuration":
        return Configuration(**json.loads(jstr))

    @staticmethod
    def from_args(args: argparse.Namespace) -> "Configuration":
        return Configuration(args.no_match_original_photo_intervals, args.debug)

    @staticmethod
    def load() -> "Configuration":
        """
        Loads the current configuration from the file
        """
        with CONFIG_FILE.open() as f:
            return Configuration._from_json(f.read())

    # instance methods
    def _to_json(self) -> str:
        # filter out hidden attributes
        return json.dumps(
            dict(
                {
                    (key, value)
                    for key, value in self.__dict__.items()
                    if not key.startswith("_")
                }
            )
        )

    def save(self) -> None:
        """Writes out the configuration to config.json"""
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        if CONFIG_FILE.exists():
            logger.debug("Overwriting config.json file")
        with CONFIG_FILE.open("w") as f:
            f.write(self._to_json())
