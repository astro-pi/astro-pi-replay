import json
import logging
import os
import shutil
from pathlib import Path
from test.test_utils import (
    TestConfiguration,
    get_original_replay_dir,
    get_test_asset_path,
)
from unittest.mock import patch

import numpy as np
import pytest

from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.picamzero import Camera
from astro_pi_replay.orbit import ISS
from astro_pi_replay.resources.downloader import (
    REPLAY_DIR_ENV_VAR,
    get_replay_dir,
    get_replay_sequence_dir,
)
from astro_pi_replay.sense_hat import SenseHat

logger = logging.getLogger(__name__)
DOWNLOADER_URL: str = "astro_pi_replay.resources.downloader.Downloader"
SEQUENCE_ID: str = "streaming_mode_sequence"


# Used to enable streaming mode for tests
@pytest.fixture
def test_configuration():
    conf = TestConfiguration(True, True, False)
    conf.streaming_mode = True
    conf.sequence = SEQUENCE_ID
    return conf


@pytest.fixture
def set_replay_dir(tmp_path_factory):
    """
    Sets the REPLAY_DIR_ENV_VAR environment variable to point to a
    blank replay directory.
    """
    replay_dir: Path = tmp_path_factory.mktemp("replay")
    value: str = str(replay_dir)
    logger.debug(f"Setting {REPLAY_DIR_ENV_VAR} to {value}")
    os.environ[REPLAY_DIR_ENV_VAR] = value
    yield
    os.environ.pop(REPLAY_DIR_ENV_VAR, None)


#########
# Tests #
#########


def test_get_replay_sequence_dir_downloads_metadata_file(
    set_replay_dir, test_configuration, tmp_path_factory
):
    # tests that the metadata.json file is downloaded
    # in streaming mode

    # given
    photography_type = "IR"
    tmp_path: Path = tmp_path_factory.mktemp("files")
    metadata: Path = tmp_path / "metadata.json"

    sequence_dir: Path = (
        get_replay_dir() / photography_type / test_configuration.sequence
    )

    with metadata.open("w") as f:
        f.write(json.dumps({"photography_type": photography_type}))

    assert test_configuration.sequence == SEQUENCE_ID
    assert not sequence_dir.exists()

    with patch(f"{DOWNLOADER_URL}.fetch_metadata") as mock_fetch_metadata:
        mock_fetch_metadata.return_value = metadata

        # when
        get_replay_sequence_dir(download_metadata=True)

    # then
    assert sequence_dir.exists()
    assert (sequence_dir / "metadata.json").exists()


def test_sense_hat_data_is_fetched_in_streaming_mode(
    set_replay_dir, test_configuration
):
    # Given
    replay_dir: Path = get_replay_dir()
    photography_type: str = "IR"
    metadata = {"photography_type": photography_type}
    sequence_path: Path = replay_dir / photography_type / SEQUENCE_ID
    sequence_path.mkdir(parents=True)
    metadata_path: Path = sequence_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata))
    data_path: Path = sequence_path / "data" / "data.csv"

    assert not data_path.exists()

    # patch the fetcher to return the test_data asset.
    with patch(f"{DOWNLOADER_URL}.fetch_sequence_file") as mock_fetch_sequence_file:
        mock_fetch_sequence_file.side_effect = get_mock_downloader(sequence_path)
        executor = AstroPiExecutor(configuration=test_configuration)
        sh = SenseHat(executor)

        # when
        pressure = sh.get_pressure()

    # Then
    # should download data/data.csv
    assert type(pressure) is np.float64
    assert data_path.exists()


def test_images_are_fetched_in_streaming_mode(set_replay_dir, test_configuration, tmp_path):
    # Given
    replay_dir: Path = get_replay_dir()
    test_metadata_path: Path = (
        get_original_replay_dir().joinpath(get_test_asset_path()) / "metadata.json"
    )
    test_metadata = json.loads(test_metadata_path.read_text())

    photography_type: str = test_metadata["photography_type"]
    sequence_path: Path = replay_dir / photography_type / SEQUENCE_ID
    sequence_path.mkdir(parents=True)
    metadata_path: Path = sequence_path / "metadata.json"
    shutil.copy2(test_metadata_path, metadata_path)
    image_path: Path = sequence_path / "photos"

    assert not image_path.exists()

    # patch the fetcher to return the test_data asset.
    with patch(f"{DOWNLOADER_URL}.fetch_sequence_file") as mock_fetch_sequence_file:
        mock_fetch_sequence_file.side_effect = get_mock_downloader(sequence_path)
        executor = AstroPiExecutor(configuration=test_configuration)
        cam = Camera(executor)

        # when
        photo_path: Path = tmp_path / "my_photo.jpg"
        cam.take_photo(photo_path)

    # Then
    # should download image
    assert photo_path.exists()
    assert image_path.exists()
    assert (image_path / "image1.jpg").exists()


def test_orbit_should_fetch_tle_file(
    set_replay_dir, test_configuration
):
    # Given

    replay_dir: Path = get_replay_dir()
    test_metadata_path: Path = (
        get_original_replay_dir().joinpath(get_test_asset_path()) / "metadata.json"
    )
    test_metadata = json.loads(test_metadata_path.read_text())

    photography_type: str = test_metadata["photography_type"]
    sequence_path: Path = replay_dir / photography_type / SEQUENCE_ID
    sequence_path.mkdir(parents=True)
    metadata_path: Path = sequence_path / "metadata.json"
    shutil.copy2(test_metadata_path, metadata_path)

    tle_path: Path = sequence_path / Path(test_metadata["tle"]["file"])

    assert not tle_path.exists()

    with patch(f"{DOWNLOADER_URL}.fetch_sequence_file") as mock_fetch_sequence_file:
        mock_fetch_sequence_file.side_effect = get_mock_downloader(sequence_path)
        executor = AstroPiExecutor(configuration=test_configuration)
        iss = ISS(executor)

        # when
        coordinates = iss.coordinates()
    
    # Then
    assert coordinates is not None
    assert tle_path.exists()


def test_should_not_redownload_files():
    pass


def test_should_warn_when_download_takes_over_delta():
    pass


def get_mock_downloader(current_sequence_dir: Path):
    def mock_download(path: Path) -> Path:
        """
        Copies the given asset (that is inside the test asset dir)
        to the current replay dir (which will be overriden in these
        tests), to simulate a download.

        path: Absolute Path to an asset inside VIS/test_data
        """

        relative_path: Path = path.relative_to(current_sequence_dir)

        original_replay_dir: Path = get_original_replay_dir()
        test_sequence_path: Path = original_replay_dir.joinpath(get_test_asset_path())
        test_asset_path = test_sequence_path.joinpath(relative_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Copying from {test_asset_path} to {path}")
        shutil.copy2(test_asset_path, path)
        return path

    return mock_download
