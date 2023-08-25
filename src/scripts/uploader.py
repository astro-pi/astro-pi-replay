import hashlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Callable, Iterator, Optional

from tqdm import tqdm

from astro_pi_executor.downloader import url_prefix

logger = logging.getLogger(__name__)


def tqdm_thread():
    pass


class Uploader:
    def __init__(self):
        if sys.platform not in ["Linux", "darwin"]:
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

    def deterministic_traversal(self, directory_to_zip: Path) -> Iterator[str]:
        """Traverses the directory recursively using a deterministic (sorted)
        order that is portable across different OS."""
        yield str(directory_to_zip)
        for root, dirs, files in os.walk(str(directory_to_zip)):
            dirs.sort()  # modify inplace for deterministic order
            for file in files:
                yield root + os.path.sep + file

    def _create_zip(
        self,
        directory_to_zip: Path,
        name: Optional[str] = None,
        include_filter: Optional[Callable[[str], bool]] = None,
    ) -> Path:
        logger.info("Creating zipfile")

        tempdir: Path = Path(tempfile.gettempdir())
        tempzip = tempdir / (str(uuid.uuid4()) + ".zip")

        # TODO make the zip deterministic:
        # use the -X (or --no-extra) flag,
        # and normalise ALL permissions  - chmod on Unix:
        #   https://stackoverflow.com/a/27500472/5509894 for Windows
        # and modified times of all files being zipped - os.utime
        logger.debug(f"Creating zipfile in {tempzip}")

        with zipfile.ZipFile(tempzip, mode="x", compression=zipfile.ZIP_LZMA) as z:
            for f in tqdm(self.deterministic_traversal(directory_to_zip)):
                # TODO add filter
                logger.debug(f)
                if include_filter is not None and include_filter(f):
                    z.write(
                        f, arcname=str(Path(f).relative_to(directory_to_zip.parent))
                    )

        print(name)
        final_path: Path = (
            directory_to_zip.parent / (name + ".zip")
            if name is not None
            else Path(str(directory_to_zip) + ".zip")
        )
        shutil.copy2(tempzip, str(final_path))
        return final_path

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
        name: Optional[str] = None,
        include_filter: Optional[Callable[[str], bool]] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Zips, checksums, and signs a given directory/file to the s3 bucket.
        name: The name to rename to - otherwise uses the base_file name
        include_filter: used to filter files under the base file in/out of the zip
        """
        zip_file: Path = self._create_zip(
            base_file, name=name, include_filter=include_filter
        )
        sha256_file: Path = self._create_sha256_checksum(zip_file)
        gpg_file: Path = self._create_gpg_signature(zip_file)

        for f in [zip_file, sha256_file, gpg_file]:
            self._upload_file(f, url)
