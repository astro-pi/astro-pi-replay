import hashlib
import logging
import re
import subprocess
from pathlib import Path

from scripts.uploader import Uploader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


GDRIVE: str = "gdrive"


def ls() -> list[dict[str, str]]:
    file_id: str = "1wjAQPWNN2Yp6JeabT8af1YNkpCwG-mvf"
    args: list[str] = [GDRIVE, "files", "list", "--parent", file_id]
    logger.debug(" ".join(args))
    proc: subprocess.CompletedProcess = subprocess.run(
        args, check=True, capture_output=True, text=True
    )  # nosec B603
    out: str = proc.stdout.strip()
    lines: list[list[str]] = [
        re.split(r"\s+", line) for line in "".join(out).splitlines()
    ]
    headers: list[str] = lines[0]
    final: list[dict[str, str]] = []
    for line in lines[1:]:
        d = {}
        for i, header in enumerate(headers):
            d[header] = line[i]
        final.append(d)
    return final


def download(fileId: str) -> None:
    args: list[str] = [GDRIVE, "files", "download", "--recursive", fileId]
    logger.debug(" ".join(args))
    subprocess.run(args, check=True, capture_output=False)  # nosec B603


def hash_directory(directory: str):
    r"""
    Analogous to calling
        find . -type f -exec sha256 {} \; | sort -k 2 | sha256sum"
    """
    # windows:str = "gci . -Recurse | where {$_.Name -like '*inspect*'}"
    u = Uploader()
    m = hashlib.sha256()
    for file_path in u.deterministic_traversal(Path(directory)):
        with open(file_path, "r") as f:
            m.update(f.read().encode("utf-8"))
    return m.hexdigest()


# the result of calling "find . -type f -exec md5sum {} \; | sort -k 2 | md5sum"
sequence_to_file_id_map: dict[str, dict[str, str]] = {
    "OrbitAz": {
        "fileId": "1wjAQPWNN2Yp6JeabT8af1YNkpCwG-mvf",
        "sha256": "b0424806fbf61c8abdf7c83a91996fcce39ddd3cce5bc7be7699280c56cb0024",
    },
    "AstroX": {},
}
