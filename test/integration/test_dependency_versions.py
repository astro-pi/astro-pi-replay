import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest
from packaging import version

from ..test_constants import PROJECT_ROOT

logger = logging.getLogger(__name__)

REQUIREMENTS_TXT = PROJECT_ROOT / "requirements.txt"
PIWHEELS_URL = "https://piwheels.org/simple"

if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)


def get_min_python_version() -> str:
    with (PROJECT_ROOT / "pyproject.toml").open() as f:
        lines: list[str] = [line for line in f.readlines() if "requires-python" in line]
    if len(lines) == 0:
        raise RuntimeError("Did not find a 'requires-python' line in pyproject.toml.")
    if len(lines) > 1:
        raise RuntimeError("Too many 'requires-python' lines in pyproject.toml.")
    line: str = lines[0]
    if ">=" not in line:
        raise RuntimeError(f"Expected >= but could not find in {line}")
    line = re.sub(r'[\\s">=]', "", line.split(" ")[-1])
    as_version = version.parse(line)
    return (
        f"{as_version.major}.{as_version.minor}"
        if as_version.minor is not None
        else str(as_version.major)
    )


@dataclass
class Platform:
    platform: str
    max_python_version: str
    index: Optional[str] = None

    def __len__(self):
        return 1


# May want to explore glibc builds of the form manylinux_2_x_
# e.g. bookworm glibc version is 2.36
MANYLINUX_X86_64 = "manylinux2014_x86_64"
MANYLINUX_ARCH64 = "manylinux2014_aarch64"
LINUX_ARMV7L = "linux_armv7l"
LINUX_ARMV6L = "linux_armv6l"
BOOKWORM_PYTHON_VERSION = "3.11.2"
BULLSEYE_PYTHON_VERSION = "3.9.2"

# Special test cases for Raspberry Pi OS / Debian
bookworm_arch64: Platform = Platform(MANYLINUX_ARCH64, BOOKWORM_PYTHON_VERSION)
bookworm_armv7l: Platform = Platform(
    LINUX_ARMV7L, BOOKWORM_PYTHON_VERSION, PIWHEELS_URL
)
bookworm_armv6l: Platform = Platform(
    LINUX_ARMV6L, BOOKWORM_PYTHON_VERSION, PIWHEELS_URL
)
bullseye_arch64: Platform = Platform(MANYLINUX_ARCH64, BULLSEYE_PYTHON_VERSION)
bullseye_armv7l: Platform = Platform(
    LINUX_ARMV7L, BULLSEYE_PYTHON_VERSION, PIWHEELS_URL
)
bullseye_armv6l: Platform = Platform(
    LINUX_ARMV6L, BULLSEYE_PYTHON_VERSION, PIWHEELS_URL
)

# For other hardware / Linux distro combinations,
# just use manylinux and the min python version
# supported
linux_x86_64: Platform = Platform(MANYLINUX_X86_64, get_min_python_version())
linux_arm64: Platform = Platform(MANYLINUX_ARCH64, get_min_python_version())

# Windows - just use min python version
# Win32 is being phased out, so might not want to put
# much effort into supporting.
windows_x86_64: Platform = Platform("win_amd64", get_min_python_version())
windows_x86_32: Platform = Platform("win32", get_min_python_version())

# Mac OS - in general, if current MacOS version is above
# it is backwards compatable


mac_catalina_arm64: Platform = Platform("macosx_12_0_arm64", get_min_python_version())
mac_bigsur_arm64: Platform = Platform("macosx_11_0_arm64", get_min_python_version())
mac_bigsur_x86_64: Platform = Platform("macosx_11_0_x86_64", get_min_python_version())
mac_mavericks_x86_64: Platform = Platform(
    "macosx_10_9_x86_64", get_min_python_version()
)
mac_mavericks_universal: Platform = Platform(
    "macosx_10_9_universal2", get_min_python_version()
)


@pytest.mark.parametrize(
    "platform",
    [
        pytest.param(bookworm_arch64, id="bookworm_arch64"),
        pytest.param(bookworm_armv7l, id="bookworm_armv7l"),
        pytest.param(bookworm_armv6l, id="bookworm_armv6l"),
        pytest.param(bullseye_arch64, id="bullseye_arch64"),
        pytest.param(bullseye_armv7l, id="bullseye_armv7l"),
        pytest.param(bullseye_armv6l, id="bullseye_armv6l"),
        pytest.param(windows_x86_32, id="windows_x86_32"),
        pytest.param(windows_x86_64, id="windows_x86_64"),
        pytest.param(mac_mavericks_x86_64, id="mac_mavericks_x86_64"),
        pytest.param(mac_bigsur_x86_64, id="mac_bigsur_x86_64"),
        pytest.param(mac_catalina_arm64, id="mac_catalina_arm64"),
    ],
)
def test_dependency_wheels_available(platform: Platform, tmp_path: Path):
    logger.debug(f"Trying to download wheels for platform '{platform.platform}'")
    cmd: list[str] = [
        "pip",
        "download",
        "--only-binary",
        ":all:",
        "-r",
        str(REQUIREMENTS_TXT.resolve()),
        "--disable-pip-version-check",
        "--dest",
        str(tmp_path),
        "--platform",
        platform.platform,
        "--python-version",
        platform.max_python_version,
    ]
    if platform.index is not None:
        cmd.append("--index-url")
        cmd.append(platform.index)

    logger.debug(f'Executing {" ".join(cmd)}')
    subprocess.run(cmd, check=True)  # nosec B603
