import collections
import functools
import importlib
import inspect
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Optional, Union
from unittest.mock import MagicMock, _patch, patch

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from astro_pi_replay import __version__
from astro_pi_replay.configuration import Configuration
from astro_pi_replay.executor import AstroPiExecutor

logger = logging.getLogger(__name__)

TEST_PYPI_URL: str = "https://test.pypi.org/simple/"
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

        try:
            logger.debug("Setting sys.path and friends")
            os.environ["PATH"] = os.path.pathsep.join(
                [str(smoke_test_venv.venv_info.script_dir), path_before]
            )
            os.environ["VIRTUAL_ENV"] = str(smoke_test_venv.venv_dir)
            sys.prefix = smoke_test_venv.venv_dir
            sys.path.append(str(smoke_test_venv.venv_info.site_packages_dir))

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

        try:
            logger.debug("Setting sys.path and friends")
            os.environ["PATH"] = os.path.pathsep.join(
                [str(live_venv.venv_info.script_dir), path_before]
            )
            os.environ["VIRTUAL_ENV"] = str(live_venv.venv_dir)
            sys.prefix = live_venv.venv_dir
            sys.path.append(str(live_venv.venv_info.site_packages_dir))

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


def prepare_executor_to_run_in_standard_venv(func):
    """
    Modifies the PATH and VIRTUAL_ENV environment variables as well
    as the sys.prefix and sys.path variables to point to a venv with
    the stubs installed.

    The AstroPiExecutor should then pick these changes up when
    detecting the ExecutionMode.
    """

    def wrapper(standard_venv, tmp_path, capfd, sense_hat_program, *args, **kwargs):
        logging.debug("Copying original values in case of a problem")
        path_before: Optional[str] = os.environ.get("PATH")
        virtual_env_before: Optional[str] = os.environ.get("VIRTUAL_ENV")
        if path_before is None:
            raise Exception(
                f"Cannot execute {func.__name__} as PATH env does not exist"
            )
        sys_prefix_before = sys.prefix
        sys_path_before = sys.path.copy()

        try:
            logger.debug("Setting sys.path and friends")
            os.environ["PATH"] = os.path.pathsep.join(
                [str(standard_venv.venv_info.script_dir), path_before]
            )
            os.environ["VIRTUAL_ENV"] = str(standard_venv.venv_dir)
            sys.prefix = standard_venv.venv_dir
            sys.path.append(str(standard_venv.venv_info.site_packages_dir))

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
                "standard_venv": standard_venv,
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


def set_index_side_effect(indices: list[int] = [0, 1]):
    """Workaround to patch pd.Index.get_indexer() since directly patching
    astro_pi_replay.executor.pd.DataFrame.index.get_indexer didn't work.
    """

    def _set_index_side_effect(method, col):
        """Workaround to patch pd.Index.get_indexer() since directly patching
        astro_pi_replay.executor.pd.DataFrame.index.get_indexer didn't work.
        """
        logger.debug("Mocked method")
        x = method(col)
        mock = MagicMock()
        # e.g. first element, then second
        mock.side_effect = [[i] for i in indices]
        x.index.get_indexer = mock
        return x

    return _set_index_side_effect


def _get_datetime_df(resource_name: str):
    df = pd.read_csv(get_test_resource(resource_name), parse_dates=["datetime"])
    return df


def patch_photo_indices(indices: list[int]) -> _patch:
    """
    Makes the indexer for the photo-indexing dataframe return the given indices
    """
    df: pd.DataFrame = _get_datetime_df("photo_indexes.csv")
    original_method = df.set_index
    return patch(
        "pandas.DataFrame.set_index",
        side_effect=functools.partial(set_index_side_effect(indices), original_method),
    )


def get_test_asset_path() -> str:
    return "VIS/test_data"


def TestConfiguration(
    no_wait_images: bool,
    interpolate_sense_hat: bool,
    debug: bool,
    snapshot_sense_hat_display: bool = False,
    sense_hat_snapshot_dir: Path = Path(__file__),
) -> Configuration:
    return Configuration(
        no_wait_images,
        interpolate_sense_hat,
        debug,
        get_test_asset_path(),
        snapshot_sense_hat_display,
        sense_hat_snapshot_dir,
        __version__,
        True,
    )


def assume(predicate: Union[bool, Iterable[bool]], reason: Optional[str] = None):
    if type(predicate) is bool:
        assert bool, reason
    else:
        for pred in predicate:
            assert pred, reason


def assert_images_equal(
    actual: Union[str, Path], expected: Union[str, Path], tolerance: float = 0.0
) -> float:
    """
    Calculates the mean squared error between the actual and
    expected images and asserts that it is below or equal to the
    given threshold.
    """
    actual_img: np.ndarray = np.array(Image.open(actual))
    expected_img: np.ndarray = np.array(Image.open(expected))

    if actual_img.shape != expected_img.shape:
        logger.warning("Images have different resolutions")
        logger.warning(f"actual: {actual_img.shape}")
        logger.warning(f"expected: {expected_img.shape}")

    mean_squared_error: float = float(
        np.square(np.subtract(actual_img, expected_img)).mean()
    )
    try:
        assert mean_squared_error <= tolerance
        return mean_squared_error
    except AssertionError as e:
        temp_file = Path(tempfile.mkdtemp())
        actual_as_path = Path(actual)
        expected_as_path = Path(expected)
        shutil.copy(actual, temp_file)
        # rename
        shutil.move(
            temp_file / actual_as_path.name,
            temp_file / f"actual{actual_as_path.suffix}",
        )
        shutil.copy(expected, temp_file)
        # rename
        shutil.move(
            temp_file / expected_as_path.name,
            temp_file / f"expected{expected_as_path.suffix}",
        )
        raise AssertionError(
            "You can compare the two images " f"by going to {temp_file}", e
        )


def assert_arrays_equal(
    actual: np.ndarray, expected: np.ndarray, tolerance: float = 0.0
) -> float:
    """
    Calculates the mean squared error between the actual and
    expected arrays and asserts that it is below or equal to the

    """
    mean_squared_error: float = float(np.square(np.subtract(actual, expected)).mean())
    assert mean_squared_error <= tolerance
    return mean_squared_error
