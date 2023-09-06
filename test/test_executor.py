"""
These tests ensure that data is replayed correctly or
accessed live correctly
"""

import json
import logging
import os
import re
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from subprocess import CalledProcessError
from typing import Callable
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from astro_pi_executor.custom_types import ExecutionMode
from astro_pi_executor.executor import AstroPiExecutor, Lifecycle
from astro_pi_executor.resources import get_start_time
from astro_pi_executor.venv_resolver import VenvResolver
from test_utils import (
    ProgramFixture,
    get_test_resource,
    prepare_executor_to_run_in_fake_live_venv,
)

logger = logging.getLogger(__name__)


@patch("astro_pi_executor.executor.time")
def test_replay_should_sleep_when_nowait_false_and_delta_is_positive(mock_time):
    executor = AstroPiExecutor(no_wait=False)

    resource: Path = get_test_resource("photo_indexes.csv")
    df = pd.read_csv(resource, parse_dates=["datetime"])

    # Given
    first: pd.Timestamp = df["datetime"].iloc[0]
    executor._state._start_time = first.to_pydatetime()

    decorator = executor.replay(filename=str(resource), col_names=["name"])
    inner_decorator = decorator(lambda: ...)
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = (first + timedelta(seconds=5)).to_pydatetime()
        inner_decorator()
    assert mock_time.sleep.call_count == 1


@patch("astro_pi_executor.executor.time")
def test_replay_replayed_index_should_always_increase_when_no_wait_is_False(_):
    executor = AstroPiExecutor(no_wait=False)

    resource: Path = get_test_resource("photo_indexes.csv")
    df = pd.read_csv(resource, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)

    # Given
    first: pd.Timestamp = df.iloc[0].name
    executor._state._start_time = first.to_pydatetime()

    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(
            seconds=1
        )
        i = executor._find_next_datum(df)
        assert i == 1


def test_executor_is_singleton():
    executor1 = AstroPiExecutor()
    executor2 = AstroPiExecutor()
    assert hash(executor1) == hash(executor2)
    assert executor1 is executor2
    assert executor1 == executor2


def test_time_since_start():
    executor = AstroPiExecutor()
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time
        assert executor.time_since_start() == get_start_time()


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
    AstroPiExecutor.run(ExecutionMode.LIVE, tmp_path, sense_hat_program.main)
    expected_regex = r"<MagicMock name='mock\(\)\.colour\.colour.*' id='[0-9]+'>"
    assert sense_hat_program.expected_file.exists()
    with sense_hat_program.expected_file.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(expected_regex, contents) is not None


def test_executor_replay_mode_should_replay_data(
    tmp_path: Path, sense_hat_program: ProgramFixture
):
    executor: AstroPiExecutor = AstroPiExecutor(no_wait=True)

    # make the test deterministic
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(
            seconds=2
        )
        executor.run(ExecutionMode.REPLAY, tmp_path, sense_hat_program.main)
    assert sense_hat_program.expected_file.exists()
    with sense_hat_program.expected_file.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(r"(13, 12, 12)", contents) is not None


def test_executor_loads_config_when_instantiated(tmp_path: Path):
    expected_file: Path = tmp_path / "test_config.json"
    with expected_file.open("w") as f:
        f.write(json.dumps({"no_wait": True, "debug": False}))
    with patch("astro_pi_executor.configuration.CONFIG_FILE", expected_file):
        executor: AstroPiExecutor = AstroPiExecutor()
        assert executor.no_wait is True


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

    venv = VenvResolver(tmp_path / "venv", init_venv=False)
    assert venv.venv_dir.exists()

    assert "sense_hat" in os.listdir(venv.venv_info.site_packages_dir)
    sense_hat_path: Path = venv.venv_info.site_packages_dir / "sense_hat"
    assert "sense_hat.py" in os.listdir(sense_hat_path)

    assert "picamera" in os.listdir(venv.venv_info.site_packages_dir)
    picamera_path: Path = venv.venv_info.site_packages_dir / "picamera"
    assert "camera.py" in os.listdir(picamera_path)

    assert "orbit" in os.listdir(venv.venv_info.site_packages_dir)
    orbit_path: Path = venv.venv_info.site_packages_dir / "orbit"
    assert "telemetry.py" in os.listdir(orbit_path)


# TODO speed up this test!
def test_setup_venv_reinstalls_venv_when_deps_changed_in_current_env(tmp_path: Path):
    output_file: Path = tmp_path / "version.txt"

    # 1. execute the main.py once in replay mode
    main: Path = tmp_path / "main.py"
    with main.open("w") as f:
        f.write(
            os.linesep.join(
                [
                    "import os",
                    "import fake_dep",
                    "",
                    f"with open(r'{str(output_file)}', 'w') as f:",
                    "    f.write(fake_dep.__version__ + os.linesep)",
                ]
            )
        )
    # The problem is that sys.prefix is used in .run - which has already been altered
    # so there is no pip...
    try:
        AstroPiExecutor.run(ExecutionMode.REPLAY, tmp_path, main)
    except CalledProcessError:
        pass  # expected

    # 2. Install a fake dep into the current venv
    current_python: Path = Path(sys.prefix) / "bin" / "python"
    if not current_python.exists():
        current_python = Path(sys.prefix) / "python.exe"
    fake_dep: Path = get_test_resource("fake_dep")
    installed = False
    try:
        # TODO override sys.prefix to install to the non-real site-packages
        subprocess.run(
            [current_python, "-m", "pip", "install", str(fake_dep)], check=True
        )  # nosec B603
        installed = True

        # 3. Re-execute and confirm that it now works
        AstroPiExecutor.run(ExecutionMode.REPLAY, tmp_path, main)

        assert output_file.exists()
        with output_file.open() as f:
            output_file_contents = f.read().strip()
        assert output_file_contents == "0.0.1"

    finally:
        # Cleanup
        if installed:
            subprocess.run(
                [current_python, "-m", "pip", "uninstall", "-y", "fake_dep"], check=True
            )  # nosec B603


def test_teardowns_run_when_exception_thrown_by_program(
    tmp_path: Path, exception_program: Path
):
    AstroPiExecutor(no_wait=True)
    semaphore: Path = tmp_path / "semaphore"
    callback: Callable = lambda: os.close(os.open(str(semaphore), os.O_CREAT))
    AstroPiExecutor._register_callback(Lifecycle.AFTER, callback)
    try:
        AstroPiExecutor.run(ExecutionMode.REPLAY, tmp_path, exception_program)
    except CalledProcessError:
        pass
    assert semaphore.exists()


@pytest.mark.skip(reason="TODO")
def test_replay_venv_includes_external_libs():
    # TODO decide if it should be symlinked so that the users that install
    # libraries AFTER running astro_pi_executor run for the first time
    # will also get the installed lib in the executor venv?
    pass


@pytest.mark.skip(reason="TODO")
def test_replay_should_stream_stdout_immediately():
    pass


@pytest.mark.skip(reason="TODO")
def test_logging_is_outputted_regularly():
    pass


@pytest.mark.skip(reason="TODO")
def test_executor_should_read_from_config_if_not_supplied():
    pass


def test_replay_mode_when_debug_mode_logger_should_emit(
    tmp_path: Path, debug_log_program: Path, capfd
):
    AstroPiExecutor(no_wait=True, debug=True)
    AstroPiExecutor.run(ExecutionMode.REPLAY, tmp_path, debug_log_program, debug=True)
    output = capfd.readouterr()
    assert "foo" in output.err


def test_when_main_raises_exception_should_raise_errors_correctly(
    tmp_path: Path, exception_program: Path, capfd
):
    # the stack trace should be pruned so as to not reveal
    # the internals of the executor
    AstroPiExecutor(no_wait=True, debug=False)
    try:
        AstroPiExecutor.run(ExecutionMode.LIVE, tmp_path, exception_program)
    except BaseException:
        output = capfd.readouterr()
        assert "Something went wrong" in output.err
        assert "CalledProcessError" not in output.err
    else:
        assert False
