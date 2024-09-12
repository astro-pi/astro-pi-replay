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

from astro_pi_replay.downloader import BUCKET_NAME, asset_prefix
from astro_pi_replay.resources.utils import METADATA_FILE_NAME, get_resource
from scripts.uploader import GPS_TAGS

logger = logging.getLogger(__name__)

if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)

S3_HTTP_PROXY: str = "S3_HTTP_PROXY"


@pytest.fixture(scope="module")
def download_all_assets(tmp_path_factory) -> list[Path]:
    """
    Downloads all the zip assets from S3 into the
    current test directory."
    """
    tmpdir: Path = tmp_path_factory.mktemp("asset_dir")

    if os.environ.get(S3_HTTP_PROXY, None):
        http_proxy: str = str(os.environ.get(S3_HTTP_PROXY))
        logger.info(f"Using s3 http proxy: {http_proxy}")
        s3_client = boto3.client("s3", config=Config(proxies={"http": http_proxy}))
    else:
        s3_client = boto3.client("s3")

    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=asset_prefix)
    if "Contents" in response:
        keys = [
            obj["Key"]
            for obj in response["Contents"]
            if (key := obj["Key"]).endswith(".zip") and not key.endswith("_videos.zip")
        ]
        filepaths: list[Path] = []
        for key in keys:
            filepath: Path = Path(key)
            destination: Path = tmpdir / filepath.name
            s3_client.download_file(BUCKET_NAME, key, str(destination))
            filepaths.append(destination)
        return filepaths
    return []


@pytest.fixture(autouse=True)
def cwd(tmpdir, monkeypatch):
    """
    This fixture changes the current working directory before
    each test in this file to to a temporary directory so that
    image / video clean up is taken care of by the OS.
    """
    monkeypatch.chdir(tmpdir)


@pytest.fixture(autouse=True)
def assets(tmpdir, download_all_assets: list[Path]) -> list[Path]:
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


def test_asset_metadata_matches_schema(assets: list[Path]):
    with get_resource("metadata_schema.json").open() as f:
        schema: dict = json.load(f)
    assert len(assets) == 4

    for asset_path in assets:
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


def test_asset_photos_do_not_have_gps_tags(assets: list[Path]):
    assert len(assets) == 4
    for asset in assets:
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
