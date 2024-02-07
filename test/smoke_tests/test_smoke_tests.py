import logging
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import Iterable, Optional

import pytest

logger = logging.getLogger(__name__)

VENV_NAME = "smoke_venv"
IMAGE_FILE = "image1.jpg"

if os.environ.get("PYTEST_PROFILE", None) != "SMOKE_TESTS":
    pytest.skip("Skipping smoke tests", allow_module_level=True)


def get_program_name_and_version() -> tuple[str, str, str]:
    src: str = str(Path(__file__).parent.parent / "src")
    try:
        sys.path.append(src)
        from astro_pi_replay import PROGRAM_CMD_NAME, PROGRAM_NAME, __version__

        return PROGRAM_NAME, PROGRAM_CMD_NAME, __version__
    finally:
        sys.path.remove(src)


def get_venv_script_dir() -> Path:
    script_dir: str = "Scripts" if sys.platform == "win32" else "bin"
    return Path(VENV_NAME) / script_dir


def get_executor() -> Path:
    _, program_cmd_name, _ = get_program_name_and_version()
    return get_venv_script_dir() / program_cmd_name


# TODO cache this using config.cache fixture
# https://docs.pytest.org/en/7.1.x/reference/reference.html#std-fixture-cache
# probably want to hash the function + any business code it pulls in
@pytest.fixture(scope="session", autouse=True)
def smoke_test_venv():
    logger.debug(f"Creating {VENV_NAME}")
    venv.create(env_dir=VENV_NAME, symlinks=sys.platform != "win32", with_pip=True)

    program_name, cmd_name, version = get_program_name_and_version()
    logger.debug(f"Installing {cmd_name} version {version} into venv")
    venv_pip: Path = get_venv_script_dir() / "pip"
    logger.debug(os.listdir(venv_pip.parent))

    version_to_test: Optional[str] = os.environ.get("VERSION_TO_TEST", None)
    logger.debug(f"Version to test: {version_to_test}")
    version_to_use: str = (
        version
        if version_to_test is None or not version_to_test.strip()
        else version_to_test
    )

    cmd: list[str] = [
        rf"{str(venv_pip)}",
        "install",
        "--index-url",
        "https://test.pypi.org/simple/",
        "--extra-index-url",
        "https://pypi.org/simple/",
        f"{program_name}=={version_to_use}",
    ]
    local_wheel: Optional[str] = os.environ.get("SMOKE_TEST_LOCAL_WHEEL", None)
    if local_wheel is not None:
        logger.debug(f"Using local wheel instead of TestPyPI: {local_wheel}")
        cmd = [rf"{str(venv_pip)}", "install", local_wheel]
    logger.debug(" ".join(cmd))
    subprocess.run(cmd, check=True)  # nosec B603

    logger.debug("Downloading test assets")
    cmd = [str(get_executor()), "download", "--test-assets-only"]
    logger.debug(" ".join(cmd))
    subprocess.run(cmd, check=True)  # nosec B603


@pytest.fixture(scope="session")
def example_program(tmp_path_factory) -> Iterable[Path]:
    filename: Path = tmp_path_factory.mktemp("smoke_test_program") / "main.py"
    with filename.open("w") as f:
        f.write(
            os.linesep.join(
                [
                    "from picamera import PiCamera",
                    "cam = PiCamera()",
                    f"cam.capture('{IMAGE_FILE}')",
                ]
            )
        )
    yield filename
    shutil.rmtree(filename.parent)


@pytest.fixture(autouse=True)
def teardown() -> Iterable[None]:
    yield
    try:
        os.remove(IMAGE_FILE)
    except FileNotFoundError:
        pass


def test_smoke_test(example_program):
    cmd: list[str] = [rf"{str(get_executor())}"]
    if os.environ.get("PYTEST_DEBUG") is not None:
        cmd.append("--debug")
    cmd += [
        "run",
        str(example_program),
        "--no-match-original-photo-intervals",
    ]
    logger.debug(f"Executing {' '.join(cmd)}")
    subprocess.run(cmd, check=True)  # nosec B603
    expected_file: Path = Path(IMAGE_FILE)
    assert expected_file.exists()  # and is an image
