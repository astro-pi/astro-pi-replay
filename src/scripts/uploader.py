import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import typing
import uuid
import weakref
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator, Optional

import exif
import jsonschema
import pandas as pd
from exif import DATETIME_STR_FORMAT, Image

# from numpy.typing import DateTime64DType, Float64DType, Int64DType
from tqdm import tqdm

from astro_pi_replay import PROGRAM_NAME
from astro_pi_replay.downloader import url_prefix
from astro_pi_replay.resources.utils import METADATA_FILE_NAME, get_metadata_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GDRIVE: str = "gdrive"

GPS_TAGS: set[str] = set(
    [
        "gps_latitude",
        "gps_longitude",
        "gps_latitude_ref",
        "gps_longitude_ref",
        "gps_altitude",
        "gps_altitude_ref",
    ]
)


class Uploader:
    def __init__(self):
        if sys.platform not in ["linux", "darwin"]:
            logger.error("Only uploading from Linux and Darwin supported currently")
            raise NotImplementedError

    def _create_sha256_checksum(self, file_to_sum: Path) -> Path:
        logger.info(f"Generating checksum for {file_to_sum}")
        with file_to_sum.open("rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        sha256_file = Path(str(file_to_sum) + ".sha256")
        with open(sha256_file, "w") as f:
            f.write(f"{checksum} {file_to_sum.name}")
        return sha256_file

    def _create_gpg_signature(self, file_to_sign: Path) -> Path:
        """ """
        logger.info(f"Generating gpg signature for {file_to_sign}")
        output_file = str(file_to_sign) + ".sig"
        command_args: list[str] = [
            "gpg",
            "--local-user",
            "enquiries@astro-pi.org",
            "--output",
            output_file,
            "--detach-sig",
            str(file_to_sign),
        ]
        logger.debug(f"Executing {' '.join(command_args)}")
        subprocess.run(command_args, check=True)  # nosec B603
        return Path(output_file)

    @staticmethod
    def deterministic_traversal(directory: Path) -> Iterator[str]:
        """Traverses the directory recursively using a deterministic (sorted)
        order that is portable across different OS."""
        yield str(directory)
        for root, dirs, files in os.walk(str(directory)):
            dirs.sort()  # modify inplace for deterministic order
            files.sort()
            for file in files:
                yield root + os.path.sep + file

    def _validate_metadata_schema(self, base_file: Path):
        """
        Ensures the metadata.json file exists and
        passes schema validation
        """
        metadata_filepath: Path = base_file / METADATA_FILE_NAME
        with metadata_filepath.open() as f:
            metadata = json.load(f)
        schema = get_metadata_schema()
        jsonschema.validate(metadata, schema)
        logger.info(f"{metadata_filepath} passed schema check")

    def _validate_video(self, base_file: Path):
        """
        Ensures the video referenced in the metadata file exists
        """
        metadata_filepath: Path = base_file / METADATA_FILE_NAME
        with metadata_filepath.open() as f:
            metadata = json.load(f)
        video: str = metadata["video"]
        if not (base_file / "videos" / video).exists():
            raise RuntimeError(f"Video {video} does not exist")

    def _validate_tle_file(self, base_file: Path):
        """
        Ensures the tle file given by the metadata file exists
        and has the correct SHA256 hash"""
        metadata_filepath: Path = base_file / METADATA_FILE_NAME
        with metadata_filepath.open() as f:
            metadata = json.load(f)
        file: str = metadata["tle"]["file"]
        expected_sha256: str = metadata["tle"]["sha256sum"]
        tle_file: Path = base_file / file
        if not tle_file.exists():
            raise RuntimeError(f"TLE file {tle_file} does not exist")
        with tle_file.open("rb") as f:
            actual_sha256: str = hashlib.sha256(f.read()).hexdigest()

        if expected_sha256 != actual_sha256:
            raise RuntimeError(
                os.linesep.join(
                    [
                        f"TLE file {tle_file} does not have the expected sha256 hash.",
                        f"Expected '{expected_sha256}' but got '{actual_sha256}'.",
                    ]
                )
            )

        with tle_file.open() as f:
            content = f.readlines()

        expected_start = "ISS (ZARYA)"
        if content[0] != expected_start:
            raise RuntimeError(f"TLE file must start with '{expected_start}'")

        logger.info(f"{base_file} passed TLE checks")

    def _validate_no_gps_tags(self, base_file: Path):
        """
        Ensures the photo files do not have exif tags
        """
        photos_dir: Path = base_file / "photos"
        for photo in photos_dir.iterdir():
            im: Optional[exif.Image] = None
            try:
                im = exif.Image(str(photo))
            except ValueError:
                continue
            if im:
                tags = im.get_all()
                logger.debug(f"Tags: {tags}")
                for tag in GPS_TAGS:
                    if tags.get(tag, None):
                        raise RuntimeError(
                            f"Image {photo.name} at path "
                            + f"{photo} has GPS exif tag: {tag}"
                        )

        logger.info(f"{base_file} passed (no) exif gps checks")

    def _create_zip(
        self,
        directory_to_zip: Path,
        zip_name: Optional[str] = None,
        include_filter: Optional[Callable[[str], bool]] = None,
    ) -> Path:
        logger.info(f"Creating zipfile for {directory_to_zip}")

        tempdir: Optional[Path] = None
        try:
            tempdir = Path(tempfile.mkdtemp())
            tempzip = tempdir / (str(uuid.uuid4()) + ".zip")

            # TODO make the zip deterministic:
            # use the -X (or --no-extra) flag,
            # and normalise ALL permissions  - chmod on Unix:
            #   https://stackoverflow.com/a/27500472/5509894 for Windows
            # and modified times of all files being zipped - os.utime
            logger.debug(f"Creating zipfile in {tempzip}")

            with zipfile.ZipFile(
                tempzip, mode="x", compression=zipfile.ZIP_DEFLATED
            ) as z:
                for f in tqdm(self.deterministic_traversal(directory_to_zip)):
                    logger.debug(f)
                    if include_filter is None or include_filter(f):
                        z.write(
                            f, arcname=str(Path(f).relative_to(directory_to_zip.parent))
                        )

            final_path: Path = (
                directory_to_zip.parent / (zip_name + ".zip")
                if zip_name is not None
                else Path(str(directory_to_zip) + ".zip")
            )
            shutil.copy2(tempzip, str(final_path))
            return final_path
        finally:
            if tempdir is not None:
                shutil.rmtree(tempdir)

    @staticmethod
    def hash_directory_content(directory: Path):
        r"""
        Analogous (but not exactly equivalent) to calling:
            find . -type f -exec sha256 {} \; | sort -k 2 | sha256sum"
        on a directory

        Note: this is not affected by file permissions,
        owners, access/modified/created times
        """
        # windows:str = "gci . -Recurse | where {$_.Name -like '*inspect*'}"
        m = hashlib.sha256()
        for file_path in Uploader.deterministic_traversal(directory):
            p = Path(file_path)
            m.update(file_path.encode())
            if not p.is_dir():
                logger.debug(p)
                with open(file_path, "rb") as f:
                    m.update(f.read())
        return m.hexdigest()

    def _upload_file(self, file: Path, url: Optional[str] = None) -> None:
        command_args: list[str] = [
            "aws",
            "s3",
            "cp",
            str(file),
            url if url is not None else url_prefix.replace("https://", "s3://") + "/",
        ]
        logger.debug(command_args)
        subprocess.run(command_args, check=True)  # nosec B603

    def upload(
        self,
        base_file: Path,
        zip_name: Optional[str] = None,
        include_filter: Optional[Callable[[str], bool]] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Zips, checksums, and signs a given directory/file to the s3 bucket.
        zip_name: The name to rename to (not including .zip) - otherwise uses
                  the base_file name
        include_filter: used to filter files under the base file in/out of the zip
        """
        # validations
        self._validate_metadata_schema(base_file)
        self._validate_video(base_file)
        self._validate_tle_file(base_file)
        self._validate_no_gps_tags(base_file)

        zip_file: Path = self._create_zip(
            base_file, zip_name=zip_name, include_filter=include_filter
        )
        sha256_file: Path = self._create_sha256_checksum(zip_file)
        gpg_file: Path = self._create_gpg_signature(zip_file)

        for f in [zip_file, sha256_file, gpg_file]:
            self._upload_file(f, url)


class AssetPreparer:
    CACHE_LOCATION = Path.home() / ".cache" / PROGRAM_NAME

    sequence_to_file_id_map: dict = {
        # TODO make this a type
        "OrbitAz": {
            "fileId": "1wjAQPWNN2Yp6JeabT8af1YNkpCwG-mvf",
            "sha256": "e9774acd6905d84e1c0a715a7b647e92"
            + "52c3578e1e4e0bf7717d140fb5bdfcda",
            "photography_type": "VIS",
            "photos": {"prefix": "image", "suffix": "jpg"},
            "videos": {"prefix": "video"},
            "sense_hat": {
                "data": "data.csv",
                "mapping": {"yaw": "", "pitch": "", "roll": ""},
            },
            # TODO will also need original datetime format
            # and also the time slice being taken (if not using all)
        },
        "AstroX": {
            "fileId": "",
            "sha256": "",
            "photography_type": "VIS",
            "photos": {"prefix": "", "suffix": "jpg"},
            "videos": {"prefix": "video"},
            "sense_hat": {
                "data": "data.csv",
                "mapping": {"yaw": "", "pitch": "", "roll": ""},
            },
        },
    }

    def __init__(self) -> None:
        if shutil.which("ffmpeg") is None:
            raise Exception("ffmpeg is not installed. Please install")
        self._files_to_close: list[str] = []
        # Called exactly once when object is garbage collected or
        # at interpreter shutdown
        self._finalizer: weakref.finalize = weakref.finalize(
            self, self._cleanup_files, self._files_to_close
        )

    @staticmethod
    def _cleanup_files(files: list[str]):
        logger.debug("Cleaning up files")
        for file in files:
            os.unlink(file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalizer()

    def _get_tempdir(self) -> Path:
        tempdir: Path = Path(tempfile.mkdtemp())
        self._files_to_close.append(str(tempdir))
        return tempdir

    def _download_to_temp(self, file_id: str) -> Path:
        """
        Internal method to download a given file/folder from Google
        Drive to a temporary directory
        """
        tempdir: Path = self._get_tempdir()

        # TODO: decide if use of gdrive is better
        # than directly accessing the API, since it doesn't offer
        # zip files and requires a huge Oauth scope
        args: list[str] = [
            GDRIVE,
            "files",
            "download",
            "--recursive",
            "--destination",
            rf"{str(tempdir)}",
            file_id,
        ]

        logger.debug(" ".join(args))
        subprocess.run(args, check=True, capture_output=False)  # nosec B603

        dir_items: list[str] = os.listdir(tempdir)
        if len(dir_items) == 0:
            raise Exception("Something went wrong - no files downloaded")
        elif len(dir_items) > 1:
            raise Exception("Something went wrong - too many files downloaded")
        return Path(dir_items[0])

    def download(self, file_id: str, sha256: str) -> Path:
        """
        Download the given file_id from Google Drive if it has
        not already been downloaded, returning the path to the
        file iff the checksum matches.
        """
        # Only download if it's not already downloaded
        downloaded: Path = self.CACHE_LOCATION / sha256
        if not downloaded.exists():
            logger.debug(f"Downloading {file_id}")
            downloaded = self._download_to_temp(file_id)
            actual_sha256sum: str = Uploader.hash_directory_content(downloaded)

            if actual_sha256sum != sha256:
                raise Exception(
                    os.linesep.join(
                        [
                            "sha256 checksums do not match.",
                            f"Expecting: {sha256}",
                            f"but received: {actual_sha256sum}",
                        ]
                    )
                )
            logger.debug(f"Caching {downloaded} since checksums match")
            shutil.move(downloaded, self.CACHE_LOCATION / actual_sha256sum)
            downloaded = self.CACHE_LOCATION / actual_sha256sum
        return downloaded

    def _verify_sense_hat_df(self, df: pd.DataFrame) -> None:
        # TODO check that all columns are accounted for
        # and are correctly named and described

        # TODO define (directed?) graph of dependencies
        # e.g. if we are missing compass, can derive from mag_[x|y|z]
        # col_[roll|pitch|yaw] can be derived from col_[x|y|z]and vice-versa
        # similarly, orientation can be derived from mag/acc/gyro
        # humidity can be derived from

        # Expected format:
        # for raw formats: col_[x|y|z]) e.g. accel_x
        # otherwise: col_[roll|pitch|yaw] e.g. accel_roll
        expected_columns: dict = {}
        # expected_columns: dict[
        #     str, type[Float64DType | Int64DType | DateTime64DType]
        # ] = {
        #     "acc_abs": Float64DType,
        #     "acc_x": Float64DType,
        #     "acc_y": Float64DType,
        #     "acc_z": Float64DType,
        #     # "acc_roll": Float64DType,
        #     # "acc_pitch": Float64DType,
        #     # "acc_yaw": Float64DType,
        #     # "gyro_roll": Float64DType,
        #     # "gyro_pitch": Float64DType,
        #     # "gyro_yaw": Float64DType,
        #     # "compass": Float64DType,
        #     "blue": Int64DType,
        #     "clear": Int64DType,
        #     "datetime": DateTime64DType,
        #     "green": Int64DType,
        #     "gyro_x": Float64DType,
        #     "gyro_y": Float64DType,
        #     "gyro_z": Float64DType,
        #     "h": Float64DType,
        #     "h_average": Float64DType,
        #     "h_max": Float64DType,
        #     "h_min": Float64DType,
        #     "hum": Float64DType,
        #     "mag_x": Float64DType,
        #     "mag_y": Float64DType,
        #     "mag_z": Float64DType,
        #     "pitch": Float64DType,
        #     "pres": Float64DType,
        #     "red": Int64DType,
        #     "roll": Float64DType,
        #     "temp": Float64DType,
        #     "yaw": Float64DType,
        # }
        actual_columns: set = set(df.columns)
        logger.debug("Checking column names...")
        expected_set: set = set(expected_columns.keys())
        if not expected_set.issubset(actual_columns):
            missing: set = expected_set.difference(actual_columns)
            raise Exception(f"Could not match {missing} columns")

        logger.debug("Checking column dtypes...")
        for col in df.columns:
            actual_type: type = typing.cast(type, df[col].dtype)
            expected_type: type = expected_columns[col]
            if not isinstance(actual_type, expected_type):
                raise Exception(
                    os.linesep.join(
                        [
                            f"The type of {col} is incorrect. ",
                            f"Expected {expected_type} but actual is {actual_type}.",
                        ]
                    )
                )

    def prepare_sequences(self) -> None:
        """
        Downloads the base assets from google drive and then processes them.
        """
        for sequence_id, metadata in self.sequence_to_file_id_map.items():
            logger.debug(f"Processing {sequence_id}")

            downloaded: Path = self.download(
                file_id=metadata["fileId"], sha256=metadata["sha256"]
            )

            # Now do the actual processing
            logger.debug(f"Copying {downloaded} to workdir")
            work_dir: Path = self._get_tempdir()
            shutil.copytree(downloaded, work_dir)
            final_dir: Path = self._get_tempdir()

            # TODO define these elsewhere to make them referencable
            photos_dir: Path = final_dir / "photos"
            videos_dir: Path = final_dir / "videos"
            data_dir: Path = final_dir / "data"
            # TODO read from resources.utils.SENSE_HAT_DATA_FILE
            data_file: Path = data_dir / "data.csv"
            metadata_file: Path = final_dir / "metadata.json"
            photo_index_file: Path = final_dir / "photo_index.csv"

            photos_dir.mkdir()
            videos_dir.mkdir()
            data_dir.mkdir()

            logger.debug("Moving photos and collecting exif datetime_digitized data")
            datetimes: list[tuple[datetime, str]] = []
            prefix: str = metadata["photos"]["prefix"]
            suffix: str = metadata["photos"]["suffix"]

            photos: list[Path] = [
                file
                for file in downloaded.iterdir()
                if file.name.startswith(prefix) and file.suffix == suffix
            ]
            logger.debug(
                f"Found {len(photos)} photos matching the prefix {prefix} and "
                + rf"suffix {suffix} in {downloaded}"
            )
            for photo in photos:
                datetimes.append(
                    (
                        datetime.strptime(
                            Image(str(photo)).datetime_digitized, DATETIME_STR_FORMAT
                        ),
                        str(photo),
                    )
                )

                # strip GPS tags and overwrite file
                im = exif.Image(str(photo))
                for gps_tag in GPS_TAGS:
                    if im.get(gps_tag) is not None:
                        im.delete(gps_tag)
                with open(photo, "wb") as f:
                    f.write(im.get_file())

                shutil.move(photo, photos_dir)

            logger.debug(f"Creating the {photo_index_file.name} file")
            # TODO define these columns names globally
            df = pd.DataFrame(datetimes, columns=["datetime", "name"])
            df["delta"] = df["datetime"].diff().dt.total_seconds().fillna(0)
            df.to_csv(photo_index_file, index=False)

            # Use ffmpeg to create a video of the sequence
            # with variable image duration
            logger.debug("Creating video sequence using ffmpeg...")
            logger.debug("Creating ffconcat file")
            series: pd.Series = (
                "file " + df["name"] + os.linesep + "duration " + df["delta"].map(str)
            )
            with (final_dir / "in.ffconcat").open("w") as f:
                f.write(os.linesep.join(["ffconcat version 1.0"] + series.to_list()))
            video_filename: str = f"{metadata['videos']['prefix']}.mp4"
            args: list[str] = [
                "ffmpeg",
                "-i",
                "in.ffconcat",
                "-vf",
                "fps=25",
                video_filename,
            ]
            logger.debug(" ".join(args))
            subprocess.run(args, check=True)  # nosec B603
            shutil.move(video_filename, videos_dir)

            logger.debug("Normalising the sense_hat csv column names")
            sense_hat = metadata["sense_hat"]
            csv_file = sense_hat["data"]
            if "mapping" in sense_hat:
                mapping = sense_hat["mapping"]
            else:
                mapping = {}
            df = pd.read_csv(csv_file)
            df = df.rename(
                columns=lambda col: col if col not in mapping else mapping[col]
            )
            self._verify_sense_hat_df(df)
            df.to_csv(data_file, index=False)
            # check if the file need pruning to match the segment

            logger.debug("Writing the metadata file")
            with metadata_file.open("w") as f:
                # TODO remove keys that are not needed
                f.write(json.dumps(metadata))

            logger.debug(f"Completed processing {sequence_id}")
