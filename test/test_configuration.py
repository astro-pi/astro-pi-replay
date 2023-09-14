import argparse
from pathlib import Path
from unittest.mock import patch

from astro_pi_executor.configuration import CONFIG_FILE, Configuration


def test_configuration_equality():
    assert Configuration(True, True, None) != Configuration(False, True, None)


def test_configuration_default_values():
    assert CONFIG_FILE.name == "config.json"
    assert CONFIG_FILE.is_relative_to(Path.home())


def test_configuration_serde():
    conf1 = Configuration(True, False, None)
    json = conf1._to_json()
    assert '"debug": false' in json
    assert '"no_wait": true' in json
    assert '"sequence": null' in json
    new_conf = Configuration._from_json(json)
    assert new_conf == conf1
    conf2 = Configuration(False, True, "sequence_id")
    json = conf2._to_json()
    assert '"sequence": "sequence_id"' in json


def test_configuration_constructor_from_args():
    args = {"no_match_original_photo_intervals": True, "debug": True, "sequence": None}
    args = argparse.Namespace(**args)
    configuration = Configuration.from_args(args)
    assert configuration.no_wait is True


def test_write_config_serdes_to_config_dir(tmp_path: Path):
    expected_file: Path = tmp_path / "test_config.json"
    assert not expected_file.exists()
    with patch("astro_pi_executor.configuration.CONFIG_FILE", expected_file):
        conf = Configuration(True, True, "sequence_id")
        conf.save()
        assert expected_file.exists()
        conf2 = Configuration.load()
        assert conf == conf2
