import argparse
import json
import logging
import os
import shutil
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from astro_pi_replay import PROGRAM_NAME, __version__
from astro_pi_replay.resources import get_replay_dir
from astro_pi_replay.resources.downloader import Downloader
from astro_pi_replay.version_utils import decrement_semver
import astro_pi_replay.resources.config as cfg

logger = logging.getLogger(__name__)

CONFIG_FILE_ENV_VAR: str = f"{PROGRAM_NAME.upper()}_CONFIG_FILE"
CONFIG_FILE_NAME: str = "config.json"
CONFIG_FILE: Path = Path.home() / f".{PROGRAM_NAME}" / CONFIG_FILE_NAME


def get_config_file_path() -> Path:
    config_file: Optional[str] = os.environ.get(CONFIG_FILE_ENV_VAR)
    if config_file is not None:
        return Path(config_file)
    return CONFIG_FILE


def get_default_venv_dir() -> Path:
    return Path.home() / f".{PROGRAM_NAME}"


@dataclass
class Configuration:
    """
    Persistent configuration stored in the home directory.
    """

    no_wait_images: bool
    interpolate_sense_hat: bool
    debug: bool
    sequence: Optional[str]
    snapshot_sense_hat_display: bool
    sense_hat_snapshot_dir: Path
    astro_pi_replay_version: str
    is_transparent_to_user: bool
    streaming_mode: bool

    @staticmethod
    def _from_json(jstr: str) -> "Configuration":
        d = json.loads(jstr)
        d["sense_hat_snapshot_dir"] = Path(d["sense_hat_snapshot_dir"])
        if "astro_pi_replay_version" not in d:
            d["astro_pi_replay_version"] = decrement_semver(__version__)
        return Configuration(**d)

    @staticmethod
    def from_args(args: argparse.Namespace) -> "Configuration":
        return Configuration(
            args.no_match_original_photo_intervals,
            args.interpolate_sense_hat,
            args.debug,
            args.sequence,
            args.snapshot_sense_hat_display,
            args.sense_hat_snapshot_dir,
            __version__,
            args.is_transparent_to_user,
            args.streaming_mode,
        )

    @staticmethod
    def load() -> "Configuration":
        """
        Loads the current configuration from the file
        """
        with get_config_file_path().open() as f:
            return Configuration._from_json(f.read())

    # instance methods
    def _to_json(self) -> str:
        lambdas: dict[str, Callable] = {"sense_hat_snapshot_dir": lambda x: str(x)}
        return json.dumps(
            dict(
                {
                    (key, value if key not in lambdas else lambdas[key](value))
                    for key, value in self.__dict__.items()
                    # filter out hidden attributes
                    if not key.startswith("_")
                }
            ),
            indent=2,
            sort_keys=True
        )

    def save(self) -> None:
        """Writes out the configuration to config.json"""
        config_file = get_config_file_path()
        config_file.parent.mkdir(exist_ok=True)
        if config_file.exists():
            logger.debug(f"Overwriting {CONFIG_FILE_NAME} file")
        with config_file.open("w") as f:
            f.write(self._to_json())

    def get_replay_sequence_dir(
        self,
        download_metadata: bool = True
    ) -> Path:

        replay_dir: Path = get_replay_dir()

        try:
            config = Configuration.load()
            if config.sequence is not None:
                for photography_type in (
                    f for f in os.listdir(replay_dir) if not f.startswith(".")
                ):
                    if config.sequence in (
                        f
                        for f in os.listdir(replay_dir / photography_type)
                        if not f.startswith(".")
                    ):
                        return replay_dir / photography_type / config.sequence

                # if here, the sequence wasn't found
                if config.streaming_mode and download_metadata:
                    downloader = Downloader()
                    metadata_path: Path = downloader.fetch_metadata(config.sequence)

                    with metadata_path.open() as f:
                        metadata: dict[str, Any] = json.load(f)

                    photography_type = str(metadata["photography_type"])

                    sequence_dir: Path = replay_dir / photography_type / config.sequence
                    sequence_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(metadata_path, sequence_dir)
                    return sequence_dir
        except FileNotFoundError:
            pass

        replay_sequence: Optional[str] = os.environ.get(cfg.REPLAY_SEQUENCE_ENV_VAR)
        if replay_sequence is not None:
            return replay_dir / Path(replay_sequence)
        raise FileNotFoundError(f"Could not find the sequence {replay_sequence} to replay.")


    def get_video(self) -> Path:
        name: str = self.get_metadata("video")
        return self.get_replay_sequence_dir() / "videos" / name


    def get_metadata(self, key: Optional[str] = None, download_metadata: bool = False) -> Any:
        """
        Loads the photo album metadata
        """
        # TODO load the file once
        with (self.get_replay_sequence_dir(download_metadata) / cfg.METADATA_FILE_NAME).open() as f:
            metadata: dict[str, Any] = json.loads(f.read())

        return metadata[key] if key else metadata

    def get_start_time(self) -> datetime:
        return datetime.strptime(self.get_metadata("start"), cfg.EXPECTED_DATETIME_FORMAT)

    def get_tle(self, download_metadata: bool = False) -> Path:
        """
        Returns the path to the TLE specified in metadata.json
        """
        tle_dict: dict[str, str] = self.get_metadata("tle", download_metadata)
        return self.get_replay_sequence_dir() / str(tle_dict["file"])

