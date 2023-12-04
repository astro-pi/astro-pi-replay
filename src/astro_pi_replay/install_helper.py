import shutil
import sys
from pathlib import Path
from traceback import TracebackException
from typing import Optional


class PackageManager:
    _bins: dict[str, list[str]] = {
        "linux": ["apt", "pacman", "nix"],
        "darwin": ["brew", "macports"],
        "win32": ["choco"],
    }

    def __init__(self) -> None:
        bin: Optional[str] = None
        if sys.platform == "linux":
            for name in PackageManager._bins["linux"]:
                path: Optional[str] = shutil.which(name)
                if path is not None:
                    bin = path
                    break
        elif sys.platform == "darwin":
            pass
        elif sys.platform == "win32":
            pass

        if bin is None:
            raise Exception("Could not find supported package manager")

        self.bin: Path = Path(bin)

    def check(self):
        self.bin
        pass


class Apt:
    def suggest_package_to_search(self):
        """
        numpy -> python3-numpy
        """
        pass

    def run(self, package_names: list[str]) -> list[str]:
        return ["apt-cache", "depends", "--no-suggests", " ".join(package_names)]

    # def parse_run_output(self, result: str):
    #     # lines: list[str] = result.split("\n")
    #     # build a dependency tree

    #     # whitespace seems to be important (2 whitespace = indent?)
    #     # |Depends is the start of an OR
    #     pass


class InstallHelper:
    """
    The aim of this class is to try and offer
    suggestions for users missing shared libraries on Raspberry Pi OS.
    """

    @staticmethod
    def test_shared_libraries() -> None:
        try:
            # TODO register handler instead of importing now...
            import pandas  # noqa F401
        except Exception as e:
            e2 = TracebackException.from_exception(e)
            if (
                "libcblas.so.3: cannot open shared object file: "
                + "No such file or directory"
                in e2.text
            ):
                raise Exception(
                    "If you are on a Raspberry Pi, you can fix this "
                    + "by installing libatlas3-base: "
                    + "sudo apt-get install libatlas3-base"
                )

    # TODO - either parse debian packages (or calculate
    # missing deps using apt) or piwheels...
    # apt-cache depends --no-suggests python3-numpy python3-pandas python3-scipy
