import collections
import hashlib
import itertools
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import uuid
import zipfile
from pathlib import Path
from typing import Iterable, Optional, TypeVar

import requests
from tqdm import tqdm

from astro_pi_executor import PROGRAM_NAME, __version__
from astro_pi_executor.executor import AstroPiExecutorException
from astro_pi_executor.resources import get_resource

logger = logging.getLogger(__name__)

GPG_EMAIL = "enquiries@astro-pi.org"
URL_BASE: str = "https://static.raspberrypi.org/files/astro-pi"
GPG_KEY_URL = f"{URL_BASE}/astro-pi.gpg"  # TODO add key-rotation
url_prefix: str = f"{URL_BASE}/{PROGRAM_NAME}/{__version__}"

ASSET_NAME = "OrbitAz.zip"

T = TypeVar("T")

ONE_HOUR: int = 60 * 60


def progress_bar(lst: Iterable[T], bound: Optional[int] = None) -> Iterable[T]:
    deq: collections.deque[str] = collections.deque()
    stop_printing = False
    stop_printing_lock = threading.Lock()

    def printer() -> None:
        spinner_generator = itertools.cycle(["|", "/", "-", "\\"])
        last_value: str = ""
        for spinner_state in spinner_generator:
            with stop_printing_lock:
                if stop_printing:
                    break
            try:
                last_value = deq.popleft().replace("\r", "")
            except IndexError:
                pass
            finally:
                print(end="\r[%s]%s" % (spinner_state, last_value))

    t1 = threading.Thread(target=printer)
    t1.start()

    if bound is not None:
        n = bound
        iterable: Iterable = lst
    else:
        iterable = list(lst)
        n = len(iterable)
    for i, elem in enumerate(iterable):
        deq.append("\r|%-80s|" % ("=" * (80 * (i + 1) // n)))
        yield elem
    with stop_printing_lock:
        stop_printing = True
    t1.join()
    print()


class Downloader:
    def __init__(self) -> None:
        tempdir: Path = Path(tempfile.gettempdir())
        tempdir /= str(uuid.uuid4())
        tempdir.mkdir()
        self.tempdir = tempdir

    def _check_sha256(self, sha256_file: Path) -> Optional[bool]:
        with sha256_file.open("r") as f:
            lines: list[str] = f.read().strip().split("\n")
        for line in lines:
            split_line: list[str] = re.split(r"\s+", line)
            if len(split_line) != 2:
                raise ValueError(f"File {sha256_file.name} has an invalid format")
            expected_sha256, filename = split_line[0], Path(split_line[1])
            with (sha256_file.parent / filename).open("rb") as f:
                actual_sha256 = hashlib.sha256(f.read()).hexdigest()
            if expected_sha256 != actual_sha256:
                return False
        return True

    def _check_gpg_signature(self, gpg_sig_file: Path) -> Optional[bool]:
        logger.debug("Checking if gpg is installed...")
        gpg_path = shutil.which("gpg")

        if gpg_path is not None and Path(gpg_path).exists():
            logger.debug("Checking if the astro pi GPG key has been imported...")
            command_args = ["gpg", "--list-public-keys", f"<{GPG_EMAIL}>"]
            logger.debug(" ".join(command_args))
            proc = subprocess.run(  # nosec B603
                command_args,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if proc.returncode != 0:
                logger.info(
                    f"GPG public key for {GPG_EMAIL} not found. "
                    + "Skipping integrity check"
                )
                commands: str = os.linesep.join(
                    [
                        f"wget {GPG_KEY_URL}",
                        f"gpg --import {GPG_KEY_URL.split('/')[-1]}",
                    ]
                )
                "\n"
                logger.info(f"You may import a key with: {commands}")
                return None

            logger.debug("Verifying the integrity of the download")
            command_args = [
                "gpg",
                "--verify",
                str(gpg_sig_file),
                str(gpg_sig_file).replace(gpg_sig_file.suffix, ""),
            ]
            logger.debug(" ".join(command_args))
            proc = subprocess.run(  # nosec B603
                command_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return True if proc.returncode == 0 else False
        return None

    def _unzip(self, zip_file: Path) -> Path:
        with zipfile.ZipFile(str(zip_file)) as z:
            for member in tqdm(z.infolist(), unit="iB"):
                try:
                    z.extract(member, self.tempdir)
                except zipfile.error as e:
                    logger.error(e)

            os.remove(zip_file)
            return self.tempdir

    def download_file(self, url: str, destination_dir: Path) -> Path:
        local_filename: str = url.split("/")[-1]
        with requests.get(url, stream=True, timeout=ONE_HOUR) as r:
            r.raise_for_status()
            total_length = int(r.headers.get("content-length", 0))
            chunk_size = 5 * 1024
            prog_bar = tqdm(total=total_length, unit="iB", unit_scale=True)
            with (self.tempdir / local_filename).open("wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    prog_bar.update(len(chunk))
                    f.write(chunk)
            if self.tempdir != destination_dir:
                shutil.copy2(
                    self.tempdir / local_filename, destination_dir / local_filename
                )

        return destination_dir / local_filename

    def download(self, destination_dir: Path) -> None:
        downloaded: list[Path] = []
        for file in [f"{ASSET_NAME}.sha256", f"{ASSET_NAME}.sig", ASSET_NAME]:
            logger.info(f"Downloading {file}...")
            url = f"{url_prefix}/{file}"
            downloaded.append(self.download_file(url, self.tempdir))

        logger.info("Checking the integrity of the downloaded data...")
        if not self._check_sha256(downloaded[0]):
            raise AstroPiExecutorException(
                "Downloaded file failed integrity check. Try again."
            )
        result: Optional[bool] = self._check_gpg_signature(downloaded[1])
        if result is not None and result is False:
            raise AstroPiExecutorException("Downloaded file failed security check.")

        # Copy zipfile to destination dir
        zip_file: Path = downloaded[2]
        shutil.copy2(zip_file, destination_dir / (zip_file.name))
        # Remove the .sig and .sha256 files
        os.remove(downloaded[0])
        os.remove(downloaded[1])

    def has_downloaded(self) -> bool:
        return f"{ASSET_NAME}" in os.listdir(self.tempdir)

    def has_installed(self) -> bool:
        try:
            return get_resource(Path(ASSET_NAME).stem).exists()
        except FileNotFoundError:
            return False

    def install(self, destination_dir: Path) -> None:
        if not self.has_downloaded():
            raise AstroPiExecutorException("Must download first")
        downloaded_file: Path = self.tempdir / ASSET_NAME
        unzipped_dir: Path = self._unzip(downloaded_file)
        if unzipped_dir != destination_dir:
            shutil.copytree(unzipped_dir, destination_dir, dirs_exist_ok=True)
        if ASSET_NAME in os.listdir(destination_dir):
            os.remove(destination_dir / ASSET_NAME)
