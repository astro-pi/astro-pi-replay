import argparse
import json
import logging
import os
import shutil
from datetime import datetime
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Callable, Optional, Union

from astro_pi_replay import PROGRAM_NAME, __version__
from astro_pi_replay.resources import get_replay_dir
from astro_pi_replay.resources.downloader import Downloader, get_sequence_metadata, search_for_sequence
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
class PartialConfiguration:
    no_wait_images: Optional[bool]
    interpolate_sense_hat: Optional[bool]
    debug: Optional[bool]
    sequence: Optional[str]
    snapshot_sense_hat_display: Optional[bool]
    sense_hat_snapshot_dir: Optional[Path]
    astro_pi_replay_version: Optional[str]
    is_transparent_to_user: Optional[bool]
    streaming_mode: Optional[bool]
    resolution: Optional[tuple[int,int]]
    photography_type: Optional[str]

    @staticmethod
    def from_args(args: argparse.Namespace) -> "PartialConfiguration":
        mapping = {
            "no_wait_images": "match_original_photo_intervals"
        }
        field_values = {}
        for f in fields(PartialConfiguration):
            name = mapping[f.name] if f.name in mapping else f.name
            arg_value = None
            try:
                arg_value = getattr(args, name)
            except AttributeError: pass

            if f.name == "no_wait_images":
                # negate
                arg_value = arg_value if arg_value is None else not arg_value
            field_values[f.name] = arg_value
        return PartialConfiguration(**field_values)

    @staticmethod
    def _from_json(jstr: str) -> "PartialConfiguration":
        d = json.loads(jstr)
        if "sense_hat_snapshot_dir" in d:
            d["sense_hat_snapshot_dir"] = Path(d["sense_hat_snapshot_dir"])
        if "resolution" in d:
            d["resolution"] = tuple(d["resolution"])

        for f in fields(PartialConfiguration):
            if f.name not in d:
                d[f.name] = None

        return PartialConfiguration(**d)

    @staticmethod
    def load() -> "PartialConfiguration":
        with get_config_file_path().open() as f:
            return PartialConfiguration._from_json(f.read())


@dataclass
class Configuration:
    """
    Persistent configuration stored in the home directory.
    """

    no_wait_images: bool
    interpolate_sense_hat: bool
    debug: bool
    sequence: str
    snapshot_sense_hat_display: bool
    sense_hat_snapshot_dir: Path
    astro_pi_replay_version: str
    is_transparent_to_user: bool
    streaming_mode: bool
    resolution: tuple[int,int]
    photography_type: str

    @staticmethod
    def _from_json(jstr: str) -> "Configuration":
        d = json.loads(jstr)
        d["sense_hat_snapshot_dir"] = Path(d["sense_hat_snapshot_dir"])
        if "astro_pi_replay_version" not in d:
            d["astro_pi_replay_version"] = decrement_semver(__version__)
        d["resolution"] = tuple(d["resolution"])
        return Configuration(**d)

    @staticmethod
    def from_args(args: argparse.Namespace) -> "Configuration":
        return Configuration(
            not args.match_original_photo_intervals,
            args.interpolate_sense_hat,
            args.debug,
            args.sequence,
            args.snapshot_sense_hat_display,
            args.sense_hat_snapshot_dir,
            __version__,
            args.is_transparent_to_user,
            args.streaming_mode,
            args.resolution,
            args.photography_type,
        )

    @staticmethod
    def load() -> "Configuration":
        """
        Loads the current configuration from the file
        """
        with get_config_file_path().open() as f:
            return Configuration._from_json(f.read())

    @staticmethod
    async def resolve_configuration(
        args: argparse.Namespace
    ) -> "Configuration":
        """
        Resolves the final configuration by merging the
        command-line arguments, the configuration from file,
        and the default configuration.

        When a new sequence id is provided, the resolved
        configuration will be changed to have the
        photography_type and resolution of the sequence.
        """
        from_file: Optional[PartialConfiguration] = None
        try:
            from_file = PartialConfiguration.load()
            logger.debug("Loaded from file")
        except (FileNotFoundError, json.JSONDecodeError): pass

        config: Configuration
        default_config = await Configuration.default()
        from_args = PartialConfiguration.from_args(args)

        if from_args.sequence is not None and \
            from_args.photography_type is None and \
            from_args.resolution is None:
            # when users do not specify all the metadata,
            # via the CLI, the metadata must be fetched
            # from the sequences file.

            metadata = get_sequence_metadata(
                    from_args.sequence)
            from_args.photography_type = metadata['photography_type']
            from_args.resolution = metadata['resolution']

        if from_file is None:
            config = Configuration.merge(default_config, from_args)
        else:
            base = Configuration.merge(default_config, from_file)
            config = Configuration.merge(base, from_args)

        return config

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

    @staticmethod
    def merge(left: "Configuration", right: Union["Configuration", PartialConfiguration]):
        """
        Merges the left and right configurations.
        Every field in right takes precedence over left,
        if it exists.
        """
        fs = {}
        for f in fields(right):
            val = getattr(right, f.name)
            if val is None:
                val = getattr(left, f.name)
            fs[f.name] = val
        return Configuration(**fs)

    @staticmethod
    async def default() -> "Configuration":
        res = (4056,3040)
        ph_type = "VIS"

        return Configuration(
            no_wait_images = False,
            interpolate_sense_hat = True,
            debug = False,
            sequence = await search_for_sequence(res, ph_type, True),
            snapshot_sense_hat_display = False,
            sense_hat_snapshot_dir = Path(os.getcwd()),
            astro_pi_replay_version = __version__,
            is_transparent_to_user = True,
            streaming_mode = False,
            resolution = res,
            photography_type = ph_type
        )


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

