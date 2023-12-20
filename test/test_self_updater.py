import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

from packaging import version
from packaging.version import Version
from requests import Response

from astro_pi_replay import PROGRAM_CMD_NAME, PROGRAM_NAME, __version__
from astro_pi_replay.self_updater import SelfUpdater
from astro_pi_replay.venv_resolver import VenvResolver
from test_utils import get_test_resource, prepare_executor_to_run_in_standard_venv

PROJECT_ROOT: Path = Path(__file__).parent.parent
SRC_DIR: Path = PROJECT_ROOT / "src"
# helper methods


def fake_pypi_response(test_resource: Path) -> MagicMock:
    response = MagicMock(spec=Response)
    type(response).status_code = PropertyMock(return_value=200)
    type(response).content = PropertyMock(return_value=test_resource.read_bytes())
    return response


def calculate_base64_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        # Read the file in chunks to handle large files

        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return base64.urlsafe_b64encode(sha256_hash.digest()).decode("latin1").rstrip("=")


def create_record_line(file_path: str) -> str:
    """
    Adheres to the RECORD file format used inside Python wheel metadata directories.
    """
    return f"{file_path},sha256={calculate_base64_sha256},{os.path.getsize(file_path)}"


# tests


def test_check_for_updates_returns_message_when_update_available(tmp_path: Path):
    # Given
    current_version: Version = version.parse(__version__)
    incremented_version: str = (
        f"{current_version.major}."
        + f"{current_version.minor}."
        + f"{current_version.micro + 1}"
    )
    resource_name: str = "pypi_simple_api_response.json"
    with get_test_resource(resource_name).open() as f:
        response: dict = json.loads(f.read())
        version_list: list[str] = response["versions"]
        version_list.append(incremented_version)
    with (tmp_path / resource_name).open("w") as f:
        f.write(json.dumps(response))

    self_updater: SelfUpdater = SelfUpdater()

    # When
    with patch("astro_pi_replay.self_updater.requests") as mock_requests:
        mock_requests.get.return_value = fake_pypi_response(tmp_path / resource_name)
        result: list[str] = self_updater._check_for_updates()
    assert len(result) == 2
    assert "An update to Astro-Pi-Replay is available" == result[0]
    assert "To update, run Astro-Pi-Replay update" == result[1]


def test_check_for_updates_returns_empty_when_updates_unavailable():
    self_updater: SelfUpdater = SelfUpdater()

    # When
    with patch("astro_pi_replay.self_updater.requests") as mock_requests:
        mock_requests.get.return_value = fake_pypi_response(
            get_test_resource("pypi_simple_api_response.json")
        )
        result: list[str] = self_updater._check_for_updates()

    assert len(result) == 0


def custom_ignore(cur_dir: str, dir_contents: list[str]) -> list[str]:
    """
    Ignore these directories below
    """
    # Allow only the src dir
    cur_path: Path = Path(cur_dir)
    if cur_path == PROJECT_ROOT:
        # Ignore all subnodes except those listed in the set
        return [
            contents
            for contents in dir_contents
            if contents
            not in set(
                [
                    "src",
                    "README.md",
                    "MANIFEST.in",
                    "Makefile",
                    "pyproject.toml",
                    "requirements.txt",
                    "requirements-dev.txt",
                ]
            )
        ]
    elif cur_path.is_relative_to(SRC_DIR):
        if cur_path.name in set(["replay", "scripts"]):
            # ignore the contents of the replay and scripts directories
            return dir_contents
        else:
            # ignore all *.pyc files
            return [
                contents for contents in dir_contents if re.match(r".*.pyc$", contents)
            ]
    else:
        # ignore nothing
        return []


@prepare_executor_to_run_in_standard_venv
def test_self_updater_updates_files_successfully(
    tmp_path: Path, standard_venv: VenvResolver
):
    # GIVEN
    copied_project_root: Path = tmp_path / "copied"

    # 1. Copy all source files (excluding resources) to tmp_path
    shutil.copytree(
        PROJECT_ROOT,
        copied_project_root,
        ignore=custom_ignore,
        ignore_dangling_symlinks=True,
    )

    # 2. Modify the version number and self_updater.py of the copy
    # the new self_updater.py will just print out something to a
    # file when executed - which we can assert
    current_version: Version = version.parse(__version__)
    next_version: str = (
        f"{current_version.major}.{current_version.minor}.{current_version.micro + 1}"
    )
    copied_init: Path = copied_project_root / "src" / "astro_pi_replay" / "__init__.py"
    with copied_init.open() as f:
        lines: list[str] = [
            line
            if "__version__" not in line
            else f'__version__ = "{str(next_version)}"{os.linesep}'
            for line in f.readlines()
        ]
    with copied_init.open("w") as f:
        f.writelines(lines)
    copied_self_updater: Path = (
        copied_project_root / "src" / "astro_pi_replay" / "self_updater.py"
    )
    expected_message: str = f"I was updated with invocation id: {str(uuid.uuid4())}"
    expected_file: Path = tmp_path / "expected_file.txt"
    with copied_self_updater.open("w") as f:
        content: str = os.linesep.join(
            [
                "from typing import Optional",
                "from pathlib import Path",
                "",
                "",
                "class SelfUpdater:",
                "    def update(self, venv_dir: Optional[Path]):",
                f"        with open('{str(expected_file)}', 'w') as f:",
                f"            f.write('{expected_message}')",
                os.linesep,
                os.linesep,
            ]
        )
        f.write(content)

    # 3. Build a new wheel from the copy
    subprocess.run(
        [str(standard_venv.venv_info.pip), "install", "build"], check=True
    )  # nosec: B
    # TODO speed this up as it's slow - it creates a stdist before a wheel
    # creates a new venv etc...
    subprocess.run(  # nosec B603
        [
            str(standard_venv.venv_info.python),
            "-m",
            "build",
            "--outdir",
            str(tmp_path / "dist"),
            str(copied_project_root),
        ],
        check=True,
    )

    # WHEN
    # 4. Install the new wheel
    self_updater: SelfUpdater = SelfUpdater()
    with patch.object(self_updater, "_update") as mock_update:
        with patch(
            "astro_pi_replay.self_updater.shutil.move",
            side_effect=lambda source, dest: shutil.copytree(
                source, dest / source.name
            ),
        ):
            mock_update.side_effect = lambda _: subprocess.run(  # nosec B603
                [
                    str(standard_venv.venv_info.pip),
                    "install",
                    "--upgrade",
                    tmp_path
                    / "dist"
                    / f"{PROGRAM_NAME}-{next_version}-py3-none-any.whl",
                ],
                check=True,
            )
            self_updater.update()

    # THEN
    # 5. Verify everything was updated
    proc = subprocess.run(  # nosec B603
        [PROGRAM_CMD_NAME, "version"], check=True, text=True, capture_output=True
    )

    assert next_version in proc.stdout
    assert not expected_file.exists()

    # The next time the updater is executed, it should
    # just create the file since it is has now been overwritten
    subprocess.run([PROGRAM_CMD_NAME, "update"], check=True)  # nosec B603
    assert expected_file.exists()
    assert expected_message in expected_file.read_text()

    # 6. And that resources were not deleted
    venv_replay_dir: Path = (
        standard_venv.venv_info.site_packages_dir
        / PROGRAM_NAME
        / "resources"
        / "replay"
    )
    assert venv_replay_dir.exists() and (vis_dir := venv_replay_dir / "VIS").exists()
    assert len(list(vis_dir.iterdir())) > 0
