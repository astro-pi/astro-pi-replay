import argparse
import copy
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from astro_pi_replay import PROGRAM_NAME, __version__
from astro_pi_replay.configuration import (
    CONFIG_FILE,
    CONFIG_FILE_ENV_VAR,
    CONFIG_FILE_NAME,
    Configuration,
)

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


def test_configuration_serde(test_config: Configuration):
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
    new_conf = Configuration._from_json(json)

    assert new_conf == test_config
    new_conf.photography_type = "IR"
    json = new_conf._to_json()
    assert '"photography_type": "IR"' in json


def test_configuration_constructor_from_args():
    args = {
        "no_match_original_photo_intervals": True,
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


def test_write_config_serdes_to_config_dir(tmp_path: Path, mock_config_filepath: Path):
    os.environ.pop(CONFIG_FILE_ENV_VAR)
    os.remove(mock_config_filepath)
    assert not mock_config_filepath.exists()
    with patch("astro_pi_replay.configuration.CONFIG_FILE", mock_config_filepath):
        conf = Configuration(
            True, True, True, "sequence_id", True, Path(__file__), "2.1.1", True, True, (4056,3040), "IR"
        )
        conf.save()
        assert mock_config_filepath.exists()
        conf2 = Configuration.load()
        assert conf == conf2
