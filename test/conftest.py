import logging
import os
import subprocess
import sys
import uuid
import venv
from pathlib import Path

import pytest

from astro_pi_executor.executor import AstroPiExecutor
from test_utils import TEST_PYPI_URL, ProgramFixture

logger = logging.getLogger(__name__)


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
            "from sense_hat import SenseHat",
            "sh = SenseHat()",
            "rgb = sh.colour.rgb",
            f"with open('{str(file_path)}', 'w') as f:",
            "    f.write(repr(rgb))",
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
def smoke_test_venv(tmp_path_factory) -> Path:
    """Basic venv for use in smoke-tests"""
    tmp_path: Path = tmp_path_factory.mktemp("smoke_test_venv")
    logger.debug(f"tmp_path is {tmp_path}")

    venv_dir: Path = tmp_path / "smoke-test-venv"
    venv.create(env_dir=venv_dir, symlinks=True, with_pip=True)

    pip: Path = venv_dir / "bin" / "pip"
    # FIXME pandas direct install shouldn't be necessary:
    subprocess.run([pip, "install", "pandas"], check=True)  # nosec B603
    subprocess.run(
        [pip, "install", "--index-url", TEST_PYPI_URL, "astro_pi_executor"], check=True
    )  # nosec B603

    return venv_dir


@pytest.fixture(scope="session")
def live_venv(tmp_path_factory) -> Path:
    """
    A venv with all the expected AstroPiExecutor.MODULES_TO_STUB
    already installed. However, the stubs are not the same
    as the ones defined in the real implementation. Rather, they
    just return unittest.mock.MagicMock objects.
    """
    tmp_path: Path = tmp_path_factory.mktemp("smoke_test_venv")
    logger.debug(f"tmp_path is {tmp_path}")

    venv_dir: Path = tmp_path / "live-venv"
    venv.create(env_dir=venv_dir, symlinks=True, with_pip=False)
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    packages_dir: Path = venv_dir / "lib" / python_version / "site-packages"

    module_files: dict[str, list[str]] = {
        "sense_hat": ["from unittest.mock import MagicMock", "SenseHat = MagicMock()"],
        "picamera": ["from unittest.mock import MagicMock", "PiCamera = MagicMock()"],
    }

    for module in AstroPiExecutor.MODULES_TO_STUB:
        module_file = packages_dir / f"{module}.py"
        with module_file.open("w") as f:
            f.write(os.linesep.join(module_files[module]))
    return venv_dir


@pytest.fixture(autouse=True)
def clear_caches():
    """
    Ensure that each test always uses a fresh cache
    """
    AstroPiExecutor._df_from_replay_file.cache_clear()
