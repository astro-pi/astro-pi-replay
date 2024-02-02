import sys
from pathlib import Path

from astro_pi_replay import __version__
from astro_pi_replay.venv_resolver import (
    VENV_CONFIG_FILE_NAME,
    VENV_REPLAY_VERSION_FILE_NAME,
    VenvResolver,
)
from astro_pi_replay.version_utils import decrement_semver


def test_when_venv_is_outdated_should_rebuild_venv(tmp_path: Path):
    mock_venv_config_file: Path = tmp_path / VENV_CONFIG_FILE_NAME
    version_string: str = f"version = {decrement_semver(sys.version.split()[0])}"
    mock_venv_config_file.write_text(version_string)

    assert VenvResolver._should_rebuild_venv(tmp_path) is True


def test_when_venv_replay_is_outdated_should_rebuild_venv(tmp_path: Path):
    # Given

    # same python version as current env
    mock_venv_config_file: Path = tmp_path / VENV_CONFIG_FILE_NAME
    version_string: str = f"version = {sys.version.split()[0]}"
    mock_venv_config_file.write_text(version_string)

    # lower replay tool version
    (tmp_path / VENV_REPLAY_VERSION_FILE_NAME).write_text(decrement_semver(__version__))

    # Then
    assert VenvResolver._should_rebuild_venv(tmp_path) is True


# TODO tests - given file missing raises exception, etc.
# def test_writes_file_version():pass
