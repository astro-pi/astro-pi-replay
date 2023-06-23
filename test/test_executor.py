"""
These tests ensure that data is replayed correctly or
accessed live correctly
"""

import logging
import os
import re
import sys
import uuid
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.sense_hat.sense_hat_api import SenseHatAdapter
from astro_pi_executor.types import ExecutionMode
from test_utils import prepare_executor_to_run_in_fake_live_venv

# TODO reuse the venvs so that Pytest doesn't need to keep re-creating them

logger = logging.getLogger(__name__)


###########################################
# Testing adapters are called
###########################################
# Executor decorator tests
# TODO perhaps this should be in the SenseHatAdapter test?
def test_replay_should_replay_sequence_of_data():
    executor = AstroPiExecutor()

    # Make the test deterministic
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)
        assert sh.colour.colour == (17, 15, 13, 48)
        assert executor._state._last_row_index == (13723 - 1)  # should be the last row


def test_replay_data_should_be_mutually_consistent():
    # a bit like Kafka's event windowing, could aggregate measurements
    # into logical sessions that read from the same row?
    pass


###########################################
# Testing e2e but system independent
###########################################


def get_basic_sense_hat_programme(random_uuid: str, path: Path) -> str:
    """
    Utility method
    """
    file_path: Path = path / (random_uuid + ".txt")
    return os.linesep.join(
        [
            "from sense_hat import SenseHat",
            "sh = SenseHat()",
            "rgb = sh.colour.rgb",
            f"with open('{str(file_path)}', 'w') as f:",
            "    f.write(repr(rgb))",
            f"print('{random_uuid}', rgb){os.linesep}",
        ]
    )


@prepare_executor_to_run_in_fake_live_venv
# def test_executor_live_mode_should_call_underlying_libraries(tmp_path: Path, capfd):
def test_executor_live_mode_should_call_underlying_libraries(tmp_path: Path):
    executor: AstroPiExecutor = AstroPiExecutor(replay_mode=False)
    main_path: Path = tmp_path / "main.py"
    random_uuid: str = str(uuid.uuid4())
    with main_path.open("w") as f:
        f.write(get_basic_sense_hat_programme(random_uuid, tmp_path))

    executor.run(ExecutionMode.LIVE, tmp_path, main_path)
    # captured = capfd.readouterr()
    # captured_out = captured.out
    # assert random_uuid in captured_out
    expected_regex = r"<Mock name='mock\(\)\.colour\.rgb' id='[0-9]+'>"
    # assert re.search(expected_regex, captured_out) is not None
    expected_path = tmp_path / (random_uuid + ".txt")
    assert expected_path.exists()
    with expected_path.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(expected_regex, contents) is not None


def test_executor_replay_mode_should_replay_data(tmp_path: Path, capfd):
    executor: AstroPiExecutor = AstroPiExecutor()
    main_path: Path = tmp_path / "main.py"
    random_uuid: str = str(uuid.uuid4())
    with main_path.open("w") as f:
        f.write(get_basic_sense_hat_programme(random_uuid, tmp_path))

    executor.run(ExecutionMode.REPLAY, tmp_path, main_path)
    #  captured = capfd.readouterr()
    #  captured_out = captured.out
    #  lines = [
    #     line for line in captured_out.split(os.linesep) \
    #     if line.startswith(random_uuid)
    #  ]
    #  assert len(lines) == 1
    #  split_line = lines[0].split()
    #  assert split_line[0] == random_uuid
    # TODO an even better test would be to configure the data that is being read
    # using a mock - then we can be absolutely sure it's reading the file
    #  assert " ".join(split_line[1:]) == "(29, 27, 24)"
    expected_path = tmp_path / (random_uuid + ".txt")
    assert expected_path.exists()
    with expected_path.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(r"(29, 27, 24)", contents) is not None


###########################################
# Testing executor setup (static) methods #
###########################################


def test_detect_mode_when_all_modules_present_should_return_Live():
    with patch("astro_pi_executor.executor.importlib.util") as mock_importlib_util:
        mock_importlib_util.find_spec.side_effect = [
            Mock(name=module) for module in AstroPiExecutor.MODULES_TO_STUB
        ]
        actual_mode = AstroPiExecutor._detect_execution_mode()
    assert actual_mode == ExecutionMode.LIVE


def test_detect_mode_when_module_missing_should_return_Replay():
    with patch("astro_pi_executor.executor.importlib.util") as mock_importlib_util:
        mock_importlib_util.find_spec.side_effect = [
            None for _ in AstroPiExecutor._detect_execution_mode()
        ]
        actual_mode = AstroPiExecutor._detect_execution_mode()
    assert actual_mode == ExecutionMode.REPLAY


def test_setup_venv_installs_stubs_into_venv_in_replay_mode(tmp_path: Path):
    main = tmp_path / "example.py"
    with (tmp_path / "example.py").open("w") as f:
        f.write("")  # empty file
    AstroPiExecutor.run(ExecutionMode.REPLAY, tmp_path, main)

    expected_venv_path = tmp_path / "venv"
    assert expected_venv_path.exists()
    assert os.listdir(expected_venv_path)

    python_version: str = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_packages_path: Path = (
        expected_venv_path / "lib" / python_version / "site-packages"
    )

    assert "sense_hat" in os.listdir(site_packages_path)
    sense_hat_path: Path = site_packages_path / "sense_hat"
    assert "sense_hat_api.py" in os.listdir(sense_hat_path)
    # TODO add the other modules
