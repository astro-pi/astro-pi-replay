import argparse
import os
from pathlib import Path
from test.test_utils import ProgramFixture
from unittest.mock import patch

import pytest

from astro_pi_replay import PROGRAM_NAME
from astro_pi_replay.configuration import CONFIG_FILE_ENV_VAR, Configuration
from astro_pi_replay.main import _main, main


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
def test_main_cli_when_run_given_supplies_args_as_None(
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
        assert namespace.debug is None
        assert namespace.mode is None
        assert namespace.match_original_photo_intervals is None
        assert namespace.venv_dir is None
        assert namespace.interpolate_sense_hat is None
        assert namespace.resolution is None
        assert namespace.photography_type is None
        assert namespace.snapshot_sense_hat_display is None
        assert namespace.sense_hat_snapshot_dir is None




@pytest.mark.asyncio
async def test_main_saves_configuration(tmp_path: Path, mock_config_filepath: Path):
    # remove the default test profile set up in conftest
    os.environ.pop(CONFIG_FILE_ENV_VAR)
    os.remove(mock_config_filepath)
    main: Path = tmp_path / "main.py"
    os.close(os.open(str(main), flags=os.O_CREAT))
    # Given
    args: dict = {
        "debug": True,
        "main": main,
        "match_original_photo_intervals": False,
        "cmd": "run",
        "mode": None,
        "venv_dir": None,
        "resolution": (4056, 3040),
        "photography_type": "VIS",
        "sequence": None,
        "interpolate_sense_hat": True,
        "snapshot_sense_hat_display": True,
        "sense_hat_snapshot_dir": __file__,
        "is_transparent_to_user": True,
        "streaming_mode": True,
    }
    namespace: argparse.Namespace = argparse.Namespace(**args)

    # When
    with patch("astro_pi_replay.configuration.CONFIG_FILE", mock_config_filepath):
        await _main(namespace)

        # then
        assert mock_config_filepath.exists()
        config1 = Configuration.load()
        stat1 = mock_config_filepath.stat()

        # now pass None except for main and cmd
        new_args = {
            k:None for k in args.keys()
        } | { "main": main, "cmd": "run" }
        await _main(argparse.Namespace(**new_args))
        config2 = Configuration.load()
        stat2 = mock_config_filepath.stat()

        # then the saved config should be used
        assert config1 == config2
        # and the underlying config file touched
        assert stat2.st_mtime > stat1.st_mtime

@pytest.mark.asyncio
async def test_main_overrides_configuration(
    tmp_path: Path,
    none_args: dict[str,None]
) -> None:
    main: Path = tmp_path / "main.py"
    os.close(os.open(str(main), flags=os.O_CREAT))

    config_before = Configuration.load()
    assert config_before.sequence == "test_data"

    # when
    sequence = "Vulpes"
    args = none_args | {
        "cmd": "run",
        "main": main,
        "sequence": sequence,
    }

    namespace = argparse.Namespace(**args)
    await _main(namespace)

    # then
    config_after = Configuration.load()
    assert config_after.sequence == sequence
    assert config_after.photography_type == "IR"

@pytest.mark.skip(reason="TODO")
def test_calls_executor_run_with_correct_args():
    pass


# TODO test when downloader throws Exception, should still run
