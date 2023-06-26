"""
These tests ensure that data is replayed correctly or
accessed live correctly
"""

import logging
import os
import re
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.types import ExecutionMode
from test_utils import ProgramFixture, prepare_executor_to_run_in_fake_live_venv

logger = logging.getLogger(__name__)


###########################################
# Testing adapters are called
###########################################
def test_replay_data_should_be_mutually_consistent():
    # a bit like Kafka's event windowing, could aggregate measurements
    # into logical sessions that read from the same row?
    pass


###########################################
# Testing e2e but system independent
###########################################


@prepare_executor_to_run_in_fake_live_venv
def test_executor_live_mode_should_call_underlying_libraries(
    tmp_path: Path, sense_hat_program: ProgramFixture
):
    executor: AstroPiExecutor = AstroPiExecutor(replay_mode=False)

    executor.run(ExecutionMode.LIVE, tmp_path, sense_hat_program.main)
    expected_regex = r"<Mock name='mock\(\)\.colour\.rgb' id='[0-9]+'>"
    assert sense_hat_program.expected_file.exists()
    with sense_hat_program.expected_file.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(expected_regex, contents) is not None


def test_executor_replay_mode_should_replay_data(
    tmp_path: Path, sense_hat_program: ProgramFixture
):
    executor: AstroPiExecutor = AstroPiExecutor()

    executor.run(ExecutionMode.REPLAY, tmp_path, sense_hat_program.main)
    assert sense_hat_program.expected_file.exists()
    with sense_hat_program.expected_file.open() as f:
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
