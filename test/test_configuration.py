import argparse
from pathlib import Path
from unittest.mock import patch

from astro_pi_executor.configuration import CONFIG_FILE, Configuration


def test_configuration_equality():
    assert Configuration(True, True) != Configuration(False, True)


def test_configuration_default_values():
    assert CONFIG_FILE.name == "config.json"
    assert CONFIG_FILE.is_relative_to(Path.home())


def test_configuration_serde():
    conf = Configuration(True, False)
    json = conf._to_json()
    assert '"debug": false' in json
    assert '"no_wait": true' in json
    new_conf = Configuration._from_json(json)
    assert new_conf == conf


def test_configuration_constructor_from_args():
    args = {"no_match_original_photo_intervals": True, "debug": True}
    args = argparse.Namespace(**args)
    configuration = Configuration.from_args(args)
    assert configuration.no_wait is True


def test_write_config_serdes_to_config_dir(tmp_path: Path):
    expected_file: Path = tmp_path / "test_config.json"
    assert not expected_file.exists()
    with patch("astro_pi_executor.configuration.CONFIG_FILE", expected_file):
        conf = Configuration(True, True)
        conf.save()
        assert expected_file.exists()
        conf2 = Configuration.load()
        assert conf == conf2
