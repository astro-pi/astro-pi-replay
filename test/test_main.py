import argparse
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from astro_pi_replay import PROGRAM_NAME
from astro_pi_replay.configuration import CONFIG_FILE_ENV_VAR
from astro_pi_replay.main import _main, main
from test_utils import ProgramFixture


@pytest.mark.skip(reason="TODO")
@patch("sys.argv", [PROGRAM_NAME, "download"])
def test_main_cli_downloads():
    pass


@patch("sys.argv", [PROGRAM_NAME, "run"])
def test_main_cli_when_run_given_but_no_main_should_error(capsys):
    try:
        main()
    except SystemExit:
        pass
    output = capsys.readouterr()
    assert "the following arguments are required: main" in output.err


@patch("astro_pi_replay.main._main")
def test_main_cli_when_run_given_supplies_default_args(
    mock_main, sense_hat_program: ProgramFixture
):
    args = [PROGRAM_NAME, "run", str(sense_hat_program.main)]
    with patch("sys.argv", args):
        try:
            main()
        except SystemExit:
            pass
        assert len(mock_main.call_args.args) == 1
        namespace = mock_main.call_args.args[0]
        assert namespace.main == sense_hat_program.main
        assert namespace.cmd == args[1]
        assert namespace.debug is (
            os.environ.get(f"{PROGRAM_NAME.upper()}_DEBUG", None) is not None
        )
        assert namespace.mode is None
        assert namespace.no_match_original_photo_intervals is False
        assert namespace.venv_dir is None
        assert namespace.interpolate_sense_hat is True
        assert namespace.resolution == (4056, 3040)
        assert namespace.photography_type == "VIS"


def test_main_saves_configuration(tmp_path: Path, mock_config_filepath: Path):
    # remove the default test profile set up in conftest
    os.environ.pop(CONFIG_FILE_ENV_VAR)
    os.remove(mock_config_filepath)
    main: Path = tmp_path / "main.py"
    os.close(os.open(str(main), flags=os.O_CREAT))
    # Given
    args: dict = {
        "debug": True,
        "main": main,
        "no_match_original_photo_intervals": True,
        "cmd": "run",
        "mode": None,
        "venv_dir": None,
        "resolution": (4056, 3040),
        "photography_type": "VIS",
        "sequence": None,
        "interpolate_sense_hat": True,
    }
    namespace: argparse.Namespace = argparse.Namespace(**args)

    # When
    with patch("astro_pi_replay.configuration.CONFIG_FILE", mock_config_filepath):
        _main(namespace)
    assert mock_config_filepath.exists()


@pytest.mark.skip(reason="TODO")
def test_calls_executor_run_with_correct_args():
    pass
