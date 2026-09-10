import argparse
import copy
import os
from pathlib import Path
from unittest.mock import patch
import copy
from typing import Any, get_type_hints
from dataclasses import fields
import itertools
import json

from astro_pi_replay.main import main

import pytest

from astro_pi_replay import PROGRAM_NAME, __version__
from astro_pi_replay.configuration import (
    CONFIG_FILE,
    CONFIG_FILE_ENV_VAR,
    CONFIG_FILE_NAME,
    Configuration,
    PartialConfiguration
)
from astro_pi_replay.resources.downloader import get_replay_dir
from test.test_utils import TestConfiguration

@pytest.fixture
def test_config() -> Configuration:
    return Configuration(
        True, True, True, "theninja", True, Path(__file__), "0.0.1", True, True, (4056,3040), "VIS"
    )

def test_configuration_equality(test_config: Configuration):
    config2 = copy.deepcopy(test_config)
    config2.interpolate_sense_hat = False
    assert test_config != config2

def test_configuration_default_values():
    assert CONFIG_FILE.name == CONFIG_FILE_NAME
    assert CONFIG_FILE.is_relative_to(Path.home())


@pytest.mark.asyncio
async def test_default_config():
    sequence_id = "mock_sequence_id"
    with patch("astro_pi_replay.configuration.search_for_sequence") as mock_search_for_sequence:
        mock_search_for_sequence.return_value = sequence_id
        default_config = await Configuration.default()
    assert default_config.no_wait_images is False
    assert default_config.interpolate_sense_hat is True
    assert default_config.debug is False
    assert default_config.sequence == sequence_id
    assert default_config.snapshot_sense_hat_display is False
    assert default_config.sense_hat_snapshot_dir == Path(os.getcwd())
    assert default_config.astro_pi_replay_version == __version__
    assert default_config.is_transparent_to_user is True
    assert default_config.streaming_mode is False
    assert default_config.resolution == (4056,3040)
    assert default_config.photography_type == "VIS"


def test_configuration_serde(test_config: Configuration):
    # test_config.interpolate_sense_hat = False
    json = test_config._to_json()
    assert '"debug": true' in json
    assert '"interpolate_sense_hat": true' in json
    assert '"no_wait_images": true' in json
    assert '"sequence": "theninja"' in json
    assert '"snapshot_sense_hat_display": true' in json
    assert '"sense_hat_snapshot_dir"' in json
    assert f'"{PROGRAM_NAME}_version"' in json
    assert '"is_transparent_to_user"' in json
    assert '"streaming_mode"' in json
    assert '"resolution"' in json
    assert '"photography_type"' in json
    new_conf = Configuration._from_json(json)

    assert new_conf == test_config
    new_conf.photography_type = "IR"
    json = new_conf._to_json()
    assert '"photography_type": "IR"' in json


def test_configuration_constructor_from_args():
    args = {
        "match_original_photo_intervals": False,
        "debug": True,
        "sequence": None,
        "interpolate_sense_hat": True,
        "snapshot_sense_hat_display": True,
        "sense_hat_snapshot_dir": "/",
        "is_transparent_to_user": True,
        "streaming_mode": True,
        "resolution": (4056, 3040),
        "photography_type": "VIS"
    }
    args = argparse.Namespace(**args)
    configuration = Configuration.from_args(args)
    assert configuration.no_wait_images is True
    assert configuration.snapshot_sense_hat_display is True
    assert str(configuration.sense_hat_snapshot_dir) == "/"
    assert configuration.astro_pi_replay_version == __version__
    assert configuration.is_transparent_to_user is True
    assert configuration.streaming_mode is True
    assert configuration.resolution == (4056, 3040)
    assert configuration.photography_type == "VIS"


def test_write_config_serdes_to_config_dir(mock_config_filepath: Path):
    os.environ.pop(CONFIG_FILE_ENV_VAR)
    os.remove(mock_config_filepath)
    assert not mock_config_filepath.exists()
    with patch("astro_pi_replay.configuration.CONFIG_FILE", mock_config_filepath):
        conf = Configuration(
            True, True, True, "sequence_id", True, Path(__file__), "2.1.1", True, True, (4056, 3040), "IR"
        )
        conf.save()
        assert mock_config_filepath.exists()
        conf2 = Configuration.load()
        assert conf == conf2


def test_get_replay_sequence_dir(test_config: Configuration):
    sequence_dir: Path = test_config.get_replay_sequence_dir()
    assert sequence_dir.is_relative_to(get_replay_dir())
    assert test_config.get_replay_sequence_dir().name == "test_data"


def test_get_metadata(test_config: Configuration):
    metadata: dict[str, Any] = test_config.get_metadata()
    expected_metadata: dict[str, Any] = {
        "altitude_average_km": 408,
        "camera": {
            "name": "Sony IMX477",
            "sensor_size_x": "6.287mm",
            "sensor_size_y": "4.712mm",
            "sensor_resolution_x": 4056,
            "sensor_resolution_y": 3040,
        },
        "lens": {"name": "Kowa 5mm C-mount Lens", "focal_length": "5mm"},
        "ground_sampling_distance_cm": 39588,
        "resolution_x": 1280,
        "resolution_y": 720,
        "tle": {
            "file": "data/iss-23097_09993082.tle",
            "sha256sum": "545c9581ca3d2bcd7d772a770ed7b70bfaa4613f1bd4d43530ff86a152afbe63",  # noqa: E501
        },
        "start": "2023-04-27 06:41:09.939574",
        "end": "2023-04-27 09:40:47.108350",
        "team_credits": "OrbitAz",
        "photography_type": "VIS",
        "photos": {"prefix": "img", "suffix": "jpg", "isZeroIndexed": True},
        "video": "OrbitAz.mp4",
    }
    assert metadata == expected_metadata


def test_get_tle(test_config: Configuration):
    tle_file: Path = test_config.get_tle()
    sequence_dir: Path = test_config.get_replay_sequence_dir()
    tle_metadata: dict[str, str] = test_config.get_metadata("tle")
    assert tle_file.is_relative_to(sequence_dir)
    assert str(tle_file.relative_to(sequence_dir)) == tle_metadata["file"]


class TestConfigMerge:

    @pytest.fixture
    def other_config(self, test_config: Configuration) -> Configuration:
        other = copy.deepcopy(test_config)
        other.no_wait_images = False
        other.interpolate_sense_hat = False
        other.debug = False
        other.sequence = "kkkm"
        other.snapshot_sense_hat_display = False
        other.sense_hat_snapshot_dir = Path("/new-snapshot-dir")
        other.astro_pi_replay_version = "-1.0.0"
        other.is_transparent_to_user = False
        other.streaming_mode = True
        other.resolution = (1080, 870)
        other.photography_type = "IR"
        return other

    @pytest.fixture
    def partial_config(self) -> PartialConfiguration:
        return PartialConfiguration(
            no_wait_images=None,
            interpolate_sense_hat=None,
            debug=None,
            sequence="new_sequence",
            snapshot_sense_hat_display=None,
            sense_hat_snapshot_dir=None,
            astro_pi_replay_version=None,
            is_transparent_to_user=None,
            streaming_mode=None,
            resolution=None,
            photography_type=None
        )

    def test_self_merge_produces_new_equivalent_object(
        self, test_config: Configuration
    ) -> None:
        result = Configuration.merge(test_config, test_config)
        assert id(result) != id(test_config)
        assert result == test_config

    def test_merge_to_other_config_uses_other_config(
        self,
        test_config: Configuration,
        other_config: Configuration
    ) -> None:
        for left,right in itertools.permutations([test_config, other_config], 2):
            merged = Configuration.merge(left, right)
            for f in fields(merged):
                assert getattr(merged, f.name) == \
                        getattr(right, f.name)

    def test_merge_only_overwrites_not_None_values(
        self,
        test_config: Configuration,
        partial_config: PartialConfiguration
    ) -> None:
        merged = Configuration.merge(test_config, partial_config)
        for f in fields(partial_config):
            v = getattr(partial_config, f.name)
            if v is not None:
                assert getattr(merged, f.name) == v
            else:
                assert getattr(merged, f.name) == \
                        getattr(test_config, f.name)

@pytest.mark.asyncio
class TestResolveConfiguration:

    @pytest.fixture
    def run_cli_default_args(self) -> argparse.Namespace:
        with patch("astro_pi_replay.main._main") as mock_main:
            args = [PROGRAM_NAME, "run", ""]
            with patch("sys.argv", args):
                main()
        assert len(mock_main.call_args.args) == 1
        namespace = mock_main.call_args.args[0]
        return namespace

    async def test_saved_configuration_missing_key(
        # when saved configuration is missing a key
        self,
        mock_config_filepath: Path,
        run_cli_default_args: argparse.Namespace
    ) -> None:
        from_file = Configuration.load()
        as_dict = json.loads(mock_config_filepath.read_text())
        as_dict.pop("photography_type")
        mock_config_filepath.write_text(json.dumps(as_dict))

        resolved_config = await Configuration.resolve_configuration(
            run_cli_default_args
        )

        # should use merged args/defaults if missing
        # otherwise, all fields from backup take precedence
        default_config = await Configuration.default()
        for f in fields(resolved_config):
            v = getattr(resolved_config, f.name)
            if f.name == "photography_type":
                expected = getattr(default_config, f.name)
            else:
                expected = getattr(from_file, f.name)
            assert v == expected

    async def test_saved_configuration_invalid(
        self,
        mock_config_filepath: Path,
        run_cli_default_args: argparse.Namespace
    ) -> None:
        # when invalid
        mock_config_filepath.write_text("not a json file")

        # should use merged args/defaults
        default_config = await Configuration.default()
        resolved_config = await Configuration.resolve_configuration(
                run_cli_default_args)
        assert resolved_config == default_config

    async def test_empty_args_and_no_config_file_uses_default(
        self,
        mock_config_filepath: Path,
        run_cli_default_args: argparse.Namespace
    ) -> None:
        # given
        os.remove(mock_config_filepath)

        # when
        resolved_config = await Configuration.resolve_configuration(
            run_cli_default_args)

        # then
        assert resolved_config == (await Configuration.default())

    async def test_empty_args_and_config_file_uses_config_file(
        self,
        test_config: Configuration,
        run_cli_default_args: argparse.Namespace
    ) -> None:
        # given
        test_config.save()

        # when
        resolved_config = await Configuration.resolve_configuration(
            run_cli_default_args
        )

        # then
        assert resolved_config == test_config

    async def test_cli_args_have_highest_precedence(
        self, run_cli_default_args: argparse.Namespace
    ) -> None:
        # given
        resolved_config1 = await Configuration.resolve_configuration(
            run_cli_default_args
        )
        run_cli_default_args.match_original_photo_intervals = False

        # when
        resolved_config2 = await Configuration.resolve_configuration(
            run_cli_default_args
        )

        # then
        for f in fields(resolved_config2):
            if f.name == "no_wait_images":
                assert resolved_config2.no_wait_images == True
            else:
                actual = getattr(resolved_config2, f.name)
                expected = getattr(resolved_config1, f.name)

                assert actual == expected, \
                    f"{f.name}: {actual} != {expected}"

    async def test_file_config_has_precedence_over_defaults(
        self,
        run_cli_default_args: argparse.Namespace
    ) -> None:
        # given
        file_config = await Configuration.default()
        file_config.no_wait_images = True
        file_config.save()

        # when
        resolved_config = await Configuration.resolve_configuration(
            run_cli_default_args
        )

        # then
        default_config = await Configuration.default()
        for f in fields(resolved_config):
            v = getattr(resolved_config, f.name)
            if f.name == "no_wait_images":
                assert resolved_config.no_wait_images is True
            else:
                assert v == getattr(default_config, f.name)

    async def test_modifies_photography_type_when_sequence_changed(
        self, none_args: dict[str,None]
    ) -> None:
        config_before = Configuration.load()
        assert config_before.sequence == "test_data"
        assert config_before.photography_type == "VIS"

        new_sequence = "Vulpes" # IR sequence
        # pass sequence id
        args = argparse.Namespace(**none_args | {
            "sequence": new_sequence
        })
        resolved_config = await Configuration.resolve_configuration(args)

        assert resolved_config.sequence == new_sequence
        assert resolved_config.photography_type == "IR"

    async def test_photography_type_VIS_finds_theninja(
        self, none_args
    ) -> None:
        args = argparse.Namespace(**none_args | {
            "photography_type": "VIS"
        })
        resolved_config = await Configuration.resolve_configuration(args)
        assert resolved_config.sequence == "theninja"


    async def test_photography_type_IR_finds_Vulpes(
        self, none_args
    ) -> None:
        args = argparse.Namespace(**none_args | {
            "photography_type": "IR"
        })
        resolved_config = await Configuration.resolve_configuration(args)
        assert resolved_config.sequence == "Vulpes"
