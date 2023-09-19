import argparse
import os
from pathlib import Path
from unittest.mock import patch

from astro_pi_executor.configuration import (
    CONFIG_FILE,
    CONFIG_FILE_ENV_VAR,
    Configuration,
)


def test_configuration_equality():
    assert Configuration(True, True, True, None) != Configuration(
        True, False, True, None
    )


def test_configuration_default_values():
    assert CONFIG_FILE.name == "config.json"
    assert CONFIG_FILE.is_relative_to(Path.home())


def test_configuration_serde():
    conf1 = Configuration(True, True, False, None)
    json = conf1._to_json()
    assert '"debug": false' in json
    assert '"interpolate_sense_hat": true' in json
    assert '"no_wait_images": true' in json
    assert '"sequence": null' in json
    new_conf = Configuration._from_json(json)
    assert new_conf == conf1
    conf2 = Configuration(True, False, True, "sequence_id")
    json = conf2._to_json()
    assert '"sequence": "sequence_id"' in json


def test_configuration_constructor_from_args():
    args = {
        "no_match_original_photo_intervals": True,
        "debug": True,
        "sequence": None,
        "interpolate_sense_hat": True,
    }
    args = argparse.Namespace(**args)
    configuration = Configuration.from_args(args)
    assert configuration.no_wait_images is True


def test_write_config_serdes_to_config_dir(tmp_path: Path, mock_config_filepath: Path):
    os.environ.pop(CONFIG_FILE_ENV_VAR)
    os.remove(mock_config_filepath)
    assert not mock_config_filepath.exists()
    with patch("astro_pi_executor.configuration.CONFIG_FILE", mock_config_filepath):
        conf = Configuration(True, True, True, "sequence_id")
        conf.save()
        assert mock_config_filepath.exists()
        conf2 = Configuration.load()
        assert conf == conf2
