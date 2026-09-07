import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from collections import namedtuple
import re
import tomllib

import pytest
from packaging import version
from packaging.markers import Marker
from packaging.requirements import Requirement

from ..test_constants import PROJECT_ROOT

logger = logging.getLogger(__name__)

PIWHEELS_URL = "https://piwheels.org/simple"

if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)



SkippedDependency = namedtuple("SkippedDependency", ["name", "reason"])

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

def get_dependencies(platform: Platform):
    with (PROJECT_ROOT / "pyproject.toml").open('rb') as f:
        pyproject = tomllib.load(f)
    raw_deps = pyproject.get("project", {}).get("dependencies", [])


    platform.platform
    arch = "x86_64" if "x86_64" in platform.platform else "aarch64"
    if "linux" in platform.platform:
        sys_plat, os_name = "linux", "posix"
    elif "win" in platform.platform:
        sys_plat, os_name = "win32", "nt"
    else:
        sys_plat, os_name = "darwin", "posix"

    env_context = {
        "python_version": platform.max_python_version,
        "python_full_version": platform.max_python_version,
        "sys_platform": sys_plat,
        "os_name": os_name,
        "platform_system": sys_plat.title(),
        "platform_machine": arch,
    }
    for dep_str in raw_deps:
        req = Requirement(dep_str)
        if req.marker is None or req.marker.evaluate(
                environment=env_context):
            req.marker = None
            yield str(req)

# May want to explore glibc builds of the form manylinux_2_x_
# e.g. bookworm glibc version is 2.36
MANYLINUX_X86_64 = "manylinux2014_x86_64"
MANYLINUX_ARCH64 = "manylinux2014_aarch64"
LINUX_ARMV7L = "linux_armv7l"
LINUX_ARMV6L = "linux_armv6l"
TRIXIE_PYTHON_VERSION = "3.13.5"
BOOKWORM_PYTHON_VERSION = "3.11.2"
BULLSEYE_PYTHON_VERSION = "3.9.2"

# Special test cases for Raspberry Pi OS / Debian
trixie_arch64: Platform = Platform(MANYLINUX_ARCH64, TRIXIE_PYTHON_VERSION)
trixie_armv7l: Platform = Platform(LINUX_ARMV7L, TRIXIE_PYTHON_VERSION, PIWHEELS_URL)
trixie_armv6l: Platform = Platform(LINUX_ARMV6L, TRIXIE_PYTHON_VERSION, PIWHEELS_URL)
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

#########
# Skips #
#########
skip_opencv_on_32bit_rpos = SkippedDependency(
    name="opencv-python", 
    reason=os.linesep.join([
        "Build failing on PiWheels: ",
        "",
        "  https://piwheels.org/project/opencv-python/",
        "",
        "This is unfortunate and means that users will need to install ",
        "opencv using apt and then create a --system-site-packages scoped venv.",
        "Bookworm brings in version 4.6.0 of python3-opencv though, so it",
        "is safe to skip this check."
    ])
)
skip_opencv_on_mavericks_x86= SkippedDependency(
    name="opencv-python", 
    reason=os.linesep.join([
        "This is unfortunate and means that users will need to install ",
        "opencv using homebrew or some other means and then create a ",
        "--system-site-packages scoped venv.",
        "Since mavericks is so old, it is acceptable to skip this check."
    ])
)

########
# Test #
########

@pytest.mark.parametrize(
    "platform,skipped_dependencies",
    [
        pytest.param(trixie_arch64, [], id="trixie_arch64"),
        pytest.param(trixie_armv7l, [], id="trixie_armv7l"),
        pytest.param(trixie_armv6l, [], id="trixie_armv6l"),

        pytest.param(bookworm_arch64, [], id="bookworm_arch64"),
        pytest.param(bookworm_armv7l, [skip_opencv_on_32bit_rpos], id="bookworm_armv7l"),
        pytest.param(bookworm_armv6l, [skip_opencv_on_32bit_rpos], id="bookworm_armv6l"),
        pytest.param(bullseye_arch64, [], id="bullseye_arch64"),
        pytest.param(bullseye_armv7l, [], id="bullseye_armv7l"),
        pytest.param(bullseye_armv6l, [], id="bullseye_armv6l"),
        pytest.param(windows_x86_32, [], id="windows_x86_32"),
        pytest.param(windows_x86_64, [], id="windows_x86_64"),
        pytest.param(mac_mavericks_x86_64, [skip_opencv_on_mavericks_x86], id="mac_mavericks_x86_64"),
        pytest.param(mac_bigsur_x86_64, [], id="mac_bigsur_x86_64"),
        pytest.param(mac_catalina_arm64, [], id="mac_catalina_arm64"),
    ],
)
def test_dependency_wheels_available(
        platform: Platform, 
        skipped_dependencies: list[SkippedDependency],
        tmp_path: Path):
    logger.debug(f"Trying to download wheels for platform '{platform.platform}'")
    skipped_dependency_names = [
        str(dep.name) for dep in skipped_dependencies]

    dependencies = get_dependencies(platform)
    for dependency in dependencies:
        if not dependency.startswith("#"):
            # Remove comments and leading/trailing whitespace
            dependency = dependency.split("#")[0].strip()
            name = re.split("(==|~=|>=|<=|!=|<|>|===)", dependency)[0]
            if name in skipped_dependency_names:
                continue # skip
            cmd: list[str] = [
                "pip",
                "download",
                "--only-binary",
                ":all:",
                dependency,
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


