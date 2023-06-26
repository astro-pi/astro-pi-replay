import collections
import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import pytest

from astro_pi_executor.executor import AstroPiExecutor

logger = logging.getLogger(__name__)

TEST_PYPI_URL = "https://test.pypi.org/simple/"
ProgramFixture = collections.namedtuple("ProgramFixture", ["main", "expected_file"])


def is_raspberry_pi_os() -> bool:
    """
    Checks the /etc/os-release file
    if it exists to determine whether
    the current system is running the
    Raspberry Pi OS.
    """
    release_file = Path("/") / "etc" / "os-release"
    if release_file.exists():
        with release_file.open() as f:
            lines: list[str] = f.readlines()
        return "ID=raspbian" in lines
    return False


raspberry_pi_os_only: pytest.MarkDecorator = pytest.mark.skipif(
    not is_raspberry_pi_os(), reason="Can only be tested on Raspberry Pi OS"
)


def get_test_resource(path_relative_to_tests_root: str) -> Path:
    path = Path(__file__).parent / "resources" / path_relative_to_tests_root
    if not path.exists():
        raise FileNotFoundError("Could not find " + f"in '{path}'")
    return path


def prepare_executor_to_run_in_smoke_test_venv(func):
    def wrapper(smoke_test_venv, capfd, tmp_path, sense_hat_program, *args, **kwargs):
        logging.debug("Copying original values in case of a problem")
        path_before: Optional[str] = os.environ.get("PATH")
        virtual_env_before: Optional[str] = os.environ.get("VIRTUAL_ENV")
        if path_before is None:
            raise Exception(
                f"Cannot execute {func.__name__} as PATH env does not exist"
            )
        sys_prefix_before = sys.prefix
        sys_path_before = sys.path.copy()

        venv_dir: Path = smoke_test_venv.resolve()
        venv_bin: str = str(venv_dir / "bin")
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

        try:
            logger.debug("Setting sys.path and friends")
            os.environ["PATH"] = ":".join([venv_bin, path_before])
            os.environ["VIRTUAL_ENV"] = str(venv_dir)
            sys.prefix = venv_dir
            sys.path.append(str(venv_dir / "lib" / python_version / "site-packages"))

            logger.debug(f"PATH: {os.environ['PATH']}")
            logger.debug(f"VIRTUAL_ENV: {os.environ['VIRTUAL_ENV']}")
            logger.debug(f"sys.prefix: {sys.prefix}")
            logger.debug(f"sys.path: {sys.path}")

            # HERE
            for module in AstroPiExecutor.MODULES_TO_STUB:
                if module in sys.modules:
                    importlib.reload(sys.modules[module])

            sig = inspect.signature(func)
            mapping = {
                "smoke_test_venv": smoke_test_venv,
                "capfd": capfd,
                "tmp_path": tmp_path,
                "sense_hat_program": sense_hat_program,
            }
            for fixture_name, fixture in mapping.items():
                if fixture_name in sig.parameters:
                    kwargs[fixture_name] = fixture
            func(*args, **kwargs)
        finally:
            logging.debug("Rolling back environmental changes")
            os.environ["PATH"] = path_before
            if virtual_env_before is not None:
                os.environ["VIRTUAL_ENV"] = virtual_env_before
            sys.prefix = sys_prefix_before
            sys.path = sys_path_before

    return wrapper


def prepare_executor_to_run_in_fake_live_venv(func):
    """
    Modifies the PATH and VIRTUAL_ENV environment variables as well
    as the sys.prefix and sys.path variables to point to a venv with
    the stubs installed.

    The AstroPiExecutor should then pick these changes up when
    detecting the ExecutionMode.
    """

    def wrapper(live_venv, tmp_path, capfd, sense_hat_program, *args, **kwargs):
        logging.debug("Copying original values in case of a problem")
        path_before: Optional[str] = os.environ.get("PATH")
        virtual_env_before: Optional[str] = os.environ.get("VIRTUAL_ENV")
        if path_before is None:
            raise Exception(
                f"Cannot execute {func.__name__} as PATH env does not exist"
            )
        sys_prefix_before = sys.prefix
        sys_path_before = sys.path.copy()

        venv_dir: Path = live_venv.resolve()
        venv_bin: str = str(venv_dir / "bin")
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

        try:
            logger.debug("Setting sys.path and friends")
            os.environ["PATH"] = ":".join([venv_bin, path_before])
            os.environ["VIRTUAL_ENV"] = str(venv_dir)
            sys.prefix = venv_dir
            sys.path.append(str(venv_dir / "lib" / python_version / "site-packages"))

            logger.debug(f"PATH: {os.environ['PATH']}")
            logger.debug(f"VIRTUAL_ENV: {os.environ['VIRTUAL_ENV']}")
            logger.debug(f"sys.prefix: {sys.prefix}")
            logger.debug(f"sys.path: {sys.path}")

            for module in AstroPiExecutor.MODULES_TO_STUB:
                if module in sys.modules:
                    importlib.reload(sys.modules[module])

            sig = inspect.signature(func)
            mapping = {
                "tmp_path": tmp_path,
                "capfd": capfd,
                "live_venv": live_venv,
                "sense_hat_program": sense_hat_program,
            }
            for fixture_name, fixture in mapping.items():
                if fixture_name in sig.parameters:
                    kwargs[fixture_name] = fixture
            func(*args, **kwargs)
        finally:
            logging.debug("Rolling back environmental changes")
            os.environ["PATH"] = path_before
            if virtual_env_before is not None:
                os.environ["VIRTUAL_ENV"] = virtual_env_before
            sys.prefix = sys_prefix_before
            sys.path = sys_path_before

    return wrapper
