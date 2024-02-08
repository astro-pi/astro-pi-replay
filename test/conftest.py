import logging
import os
import shutil
import site
import uuid
from pathlib import Path
from test.test_utils import (
    TEST_PYPI_URL,
    ProgramFixture,
    TestConfiguration,
    get_test_asset_path,
)
from typing import Iterable
from unittest.mock import patch

import pytest

from astro_pi_replay import PROGRAM_NAME
from astro_pi_replay.configuration import (
    CONFIG_FILE_ENV_VAR,
    CONFIG_FILE_NAME,
    Configuration,
)
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import REPLAY_SEQUENCE_ENV_VAR
from astro_pi_replay.venv_resolver import VenvResolver

logger = logging.getLogger(__name__)


@pytest.fixture
def exception_program(tmp_path: Path) -> Path:
    main_path: Path = tmp_path / (str(uuid.uuid4()) + ".py")
    contents: str = "raise Exception('Woops! Something went wrong')"
    with main_path.open("w") as f:
        f.write(contents)
    return main_path


@pytest.fixture
def debug_log_program(tmp_path: Path) -> Path:
    main_path: Path = tmp_path / (str(uuid.uuid4()) + ".py")
    contents: str = os.linesep.join(
        [
            "import logging",
            "logger = logging.getLogger(__name__)",
            "logger.debug('foo')",
        ]
    )
    with main_path.open("w") as f:
        f.write(contents)
    return main_path


@pytest.fixture
def sense_hat_program(tmp_path: Path, uuid4: str) -> ProgramFixture:
    """
    Writes a basic main.py program - file A - that reads from the SenseHat
    into the tmp_path. When the main.py program is executed it should write
    a value to another file - file B.

    Returns a three-tuple consisting of the path to the main.py program (file A),
    the expected path to be created (file B) when main.py is executed.
    """
    file_path: Path = tmp_path / (uuid4 + ".txt")
    contents: str = os.linesep.join(
        [
            "import sys",
            "print(sys.prefix)",
            "from sense_hat import SenseHat",
            "sh = SenseHat()",
            "rgb = sh.colour.colour",
            f"with open(r'{str(file_path)}', 'w') as f:",
            "    f.write(repr(rgb[:3]))",
            f"print('{uuid4}', rgb){os.linesep}",
        ]
    )
    main_path: Path = tmp_path / "main.py"
    with main_path.open("w") as f:
        f.write(contents)
    return ProgramFixture(main=main_path, expected_file=file_path)


@pytest.fixture
def uuid4() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def smoke_test_venv(tmp_path_factory) -> VenvResolver:
    """Basic venv for use in smoke-tests"""
    venv_dir: Path = tmp_path_factory.mktemp("smoke_test_venv")
    logger.debug(f"venv_dir is {venv_dir}")

    venv = VenvResolver(venv_dir / "smoke_test_venv")

    venv.install("pandas")  # FIXME direct install shouldn't be necessary
    venv.install(PROGRAM_NAME, flags=["--index-url", TEST_PYPI_URL])

    return venv


@pytest.fixture(scope="session")
def __standard_venv(tmp_path_factory) -> VenvResolver:
    """
    A venv created by the Astro-Pi-Replay tool to be copied
    directly (as a cache) for subsequent tests
    """
    parent_dir: Path = tmp_path_factory.mktemp("standard_venv")
    venv_dir: Path = parent_dir / "standard_venv"
    AstroPiExecutor._setup_venv(parent_dir, venv_dir.name)
    logger.debug("Base standard venv is setup")
    return VenvResolver(venv_dir, modify_venv_dir=False)


@pytest.fixture
def standard_venv(tmp_path: Path, __standard_venv: VenvResolver) -> VenvResolver:
    venv_dir: Path = tmp_path / "venv"
    logger.debug("Copying base venv...")
    VenvResolver._copy_venv(__standard_venv.venv_dir, venv_dir)
    logger.debug("Finished copying base venv")

    return VenvResolver(venv_dir, modify_venv_dir=False)


@pytest.fixture(scope="session")
def live_venv(tmp_path_factory) -> VenvResolver:
    """
    A venv with all the expected AstroPiExecutor.MODULES_TO_STUB
    already installed. However, the stubs are not the same
    as the ones defined in the real implementation. Rather, they
    just return unittest.mock.MagicMock objects.
    """
    venv_dir: Path = tmp_path_factory.mktemp("smoke_test_venv")
    logger.debug(f"tmp_path is {venv_dir}")

    venv: VenvResolver = VenvResolver(venv_dir / "smoke_test_venv")

    module_files: dict[str, list[str]] = {
        "sense_hat": ["from unittest.mock import MagicMock", "SenseHat = MagicMock()"],
        "picamera": ["from unittest.mock import MagicMock", "PiCamera = MagicMock()"],
        "orbit": ["from unittest.mock import MagicMock", "ISS = MagicMock()"],
    }

    for module in AstroPiExecutor.MODULES_TO_STUB:
        module_file = venv.venv_info.site_packages_dir / f"{module}.py"
        with module_file.open("w") as f:
            f.write(os.linesep.join(module_files[module]))
    return venv


@pytest.fixture(scope="session", autouse=True)
def set_replay_dir() -> Iterable:
    """
    Sets the REPLAY_SEQUENCE_ENV_VAR environment variable to point to the test data
    dir.
    """
    value: str = get_test_asset_path()
    logger.debug(f"Setting {REPLAY_SEQUENCE_ENV_VAR} to {value}")
    os.environ[REPLAY_SEQUENCE_ENV_VAR] = value

    with patch("astro_pi_replay.main.Downloader.has_installed") as f:
        f.return_value = True
        yield
    logger.debug(f"Unsetting {REPLAY_SEQUENCE_ENV_VAR}")
    os.environ.pop(REPLAY_SEQUENCE_ENV_VAR, None)


@pytest.fixture(scope="session", autouse=True)
def remove_old_test_modifications() -> None:
    """Ensures that any old modifications to the test
    venv from previous test runs are removed prior to
    executing tests.
    """
    current_site_packages: Path = Path(site.getsitepackages()[0])
    fake_dep: Path = current_site_packages / "fake_dep"
    if fake_dep.exists():
        shutil.rmtree(fake_dep)


@pytest.fixture(autouse=True)
def test_configuration():
    return TestConfiguration(False, False, False)


def clear_caches():
    """
    Ensure that each test always starts with a fresh state.
    """
    AstroPiExecutor._reset()


clear_caches_function = pytest.fixture(clear_caches, autouse=True)
clear_caches_module = pytest.fixture(clear_caches, scope="module", autouse=True)


clear_caches_function = pytest.fixture(clear_caches, autouse=True)
clear_caches_module = pytest.fixture(clear_caches, scope="module", autouse=True)


@pytest.fixture(autouse=True)
def mock_config_filepath(test_configuration: Configuration, tmp_path: Path):
    test_config_path: Path = tmp_path / CONFIG_FILE_NAME
    with patch("astro_pi_replay.configuration.CONFIG_FILE", test_config_path):
        test_configuration.save()
        yield test_config_path


@pytest.fixture(autouse=True)
def set_config_dir(mock_config_filepath) -> Iterable:
    """
    Sets/unsets the CONFIG_FILE_ENV_VAR before and
    after each test
    """
    logger.debug(f"Setting {CONFIG_FILE_ENV_VAR} to {mock_config_filepath}")
    os.environ[CONFIG_FILE_ENV_VAR] = str(mock_config_filepath)

    yield
    logger.debug(f"Unsetting {CONFIG_FILE_ENV_VAR}")
    os.environ.pop(str(CONFIG_FILE_ENV_VAR), None)
