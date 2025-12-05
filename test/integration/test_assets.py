import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import boto3
import exif
import jsonschema
import pytest
from botocore.config import Config

from astro_pi_replay.resources.downloader import (
    BUCKET_NAME,
    METADATA_FILE_NAME,
    asset_prefix,
    get_resource,
)
from scripts.uploader import GPS_TAGS

logger = logging.getLogger(__name__)

if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)

S3_HTTP_PROXY: str = "S3_HTTP_PROXY"


@pytest.fixture(scope="module")
def s3_client():
    if os.environ.get(S3_HTTP_PROXY, None):
        http_proxy: str = str(os.environ.get(S3_HTTP_PROXY))
        logger.info(f"Using s3 http proxy: {http_proxy}")
        s3_client = boto3.client("s3", config=Config(proxies={"http": http_proxy}))
    else:
        s3_client = boto3.client("s3")
    return s3_client



@pytest.fixture(scope="module")
def asset_keys(s3_client) -> list[str]:
    response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=asset_prefix)
    asset_keys: list[str] = []
    if "Contents" in response:
        asset_keys = [obj["Key"] for obj in response["Contents"]]

    return asset_keys


@pytest.fixture(scope="module")
def download_all_assets(
        tmp_path_factory, s3_client, asset_keys) -> list[Path]:
    """
    Downloads all the zip assets from S3 into the
    current test directory."
    """
    tmpdir: Path = tmp_path_factory.mktemp("asset_dir")

    photo_zip_keys = [key for key in asset_keys \
            if key.endswith(".zip") and not key.endswith("_videos.zip")]
    filepaths: list[Path] = []
    logger.info("Fetching all photo assets...")
    for key in photo_zip_keys:
        filepath: Path = Path(key)
        logger.info(f"Fetching {key}...")
        destination: Path = tmpdir / filepath.name
        s3_client.download_file(BUCKET_NAME, key, str(destination))
        filepaths.append(destination)
    return filepaths


@pytest.fixture(autouse=True)
def cwd(tmpdir, monkeypatch):
    """
    This fixture changes the current working directory before
    each test in this file to to a temporary directory so that
    image / video clean up is taken care of by the OS.
    """
    monkeypatch.chdir(tmpdir)


@pytest.fixture(autouse=True)
def photo_assets(
        tmpdir, download_all_assets: list[Path]) -> list[Path]:
    """
    Copies the downloaded assets into a temporary directory
    for isolated testing.
    """
    assets: list[Path] = []
    for asset in download_all_assets:
        destination: Path = tmpdir / asset.name
        shutil.copyfile(asset, destination)
        assets.append(destination)
    return assets


def test_assets_match_sequences_csv(
        asset_keys: list[str]) -> None:
    s3: set[str] = set()
    for asset in asset_keys:
        s3.add(Path(asset).name)

    with get_resource("sequences.csv").open() as f:
        sequences = f.read().strip().splitlines()[1:]
    for sequence in sequences:
        id = sequence.split(",")[0]
        assert f"{id}.zip" in s3
        assert f"{id}.zip.sha256" in s3
        assert f"{id}.zip.sig" in s3
        assert f"{id}_videos.zip" in s3
        assert f"{id}_videos.zip.sha256" in s3
        assert f"{id}_videos.zip.sig" in s3
        if id in s3:
            s3.remove(id)
    if len(s3) > 0:
        logger.info(
            f"There are some assets in s3 " +
            "not found in sequences.csv")


def test_asset_metadata_matches_schema(photo_assets: list[Path]):
    with get_resource("metadata_schema.json").open() as f:
        schema: dict = json.load(f)

    for asset_path in photo_assets:
        asset_path = Path(asset_path)
        logger.info(f"Checking {str(asset_path)}")
        # unzip
        tmpdir: Path = Path(tempfile.mkdtemp())
        shutil.unpack_archive(asset_path.name, tmpdir)

        metadata_file = tmpdir / asset_path.stem / METADATA_FILE_NAME
        assert metadata_file.exists()
        with metadata_file.open() as f:
            to_validate = json.load(f)
        jsonschema.validate(to_validate, schema)


def test_asset_photos_do_not_have_gps_tags(photo_assets: list[Path]):
    for asset in photo_assets:
        asset = Path(asset)
        # unzip
        tmpdir: Path = Path(tempfile.mkdtemp())
        shutil.unpack_archive(asset, tmpdir)

        photo_dir: Path = tmpdir / asset.stem / "photos"
        for photo in photo_dir.iterdir():
            im: Optional[exif.Image]
            try:
                im = exif.Image(str(photo))
            except ValueError:
                continue

            exif_tags: dict = im.get_all()

            for gps_tag in GPS_TAGS:
                assert gps_tag not in exif_tags
