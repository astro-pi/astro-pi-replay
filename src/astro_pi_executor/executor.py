import functools
import importlib.util
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from datetime import datetime, timedelta
from functools import partial, wraps
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from astro_pi_executor import PROGRAM_NAME
from astro_pi_executor.custom_types import ExecutionMode
from astro_pi_executor.resources import get_resource, get_start_time

logger = logging.getLogger(__name__)


class AstroPiExecutorState:
    """
    Wrapper class for the executor instance's shared, mutable state.
    """

    def __init__(self) -> None:
        self._last_sense_hat_row_index: int = 0
        self._last_picamera_photo_index: int = 0
        self._start_time: datetime = datetime.now()


class AstroPiExecutorRuntimeError(RuntimeError):
    pass


class AstroPiExecutorException(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(message)

    def __repr__(self) -> str:
        return self.message

    def __str__(self) -> str:
        return self.message


class AstroPiExecutor:
    """
    Class containing the replaying logic (as instance methods)
    + the CLI main methods (as static methods).

    This class is instantiated (by the API adapter classes) only
    when ExecutionMode is REPLAY, in order control the replaying
    of data. Otherwise, its static methods are used to setup a
    venv and run main.py files.

    The class is a singleton
    """

    # MODULES_TO_STUB: list[str] = ["sense_hat", "picamera", "orbit", "skyfield"]
    MODULES_TO_STUB: list[str] = ["sense_hat", "picamera"]
    NOT_FOUND = f"{PROGRAM_NAME} not found"

    """
    Checks whether the current interpreter is running in a venv,
    as defined here in https://docs.python.org/3/library/venv.html#how-venvs-work
    """
    is_in_venv: bool = sys.prefix != sys.base_prefix
    _instance: Optional["AstroPiExecutor"] = None

    # def __init__(
    #     self,
    #     datetime_col: str = "datetime",
    #     # example: 2022-01-31 12:21:15.123456
    #     datetime_format: str = "%Y-%m-%d %H:%M:%S.%f",
    #     replay_mode: bool = True,
    #     state: AstroPiExecutorState = AstroPiExecutorState(),
    # ) -> None:
    #        cls.datetime_col: str = datetime_col
    #        cls.datetime_format: str = datetime_format
    #        cls.replay_mode: bool = replay_mode
    #        cls._state: AstroPiExecutorState = state

    def __new__(
        cls,
        datetime_col: str = "datetime",
        # example: 2022-01-31 12:21:15.123456
        datetime_format: str = "%Y-%m-%d %H:%M:%S.%f",
        replay_mode: bool = True,
        state: AstroPiExecutorState = AstroPiExecutorState(),
    ) -> "AstroPiExecutor":
        if cls._instance is None:
            cls._instance = super(AstroPiExecutor, cls).__new__(cls)

            cls.datetime_col: str = datetime_col
            cls.datetime_format: str = datetime_format
            cls.replay_mode: bool = replay_mode
            cls._state: AstroPiExecutorState = state

            # TODO add option to be a bit like easyrandom / haskell type testing
            # random_mode = False # whether or not to randomly generate data
            # mode: ir or vis

        return cls._instance

    def picamera_replay(self) -> Callable:
        """
        Decorator used to conditionally replay photos from file for the PiCamera
        """
        return lambda: 1

    def sense_hat_replay(self, *args, **kwargs) -> Callable:
        """
        Decorator used to conditionally replay data from file for the SenseHat.
        """
        filename = str(get_resource("OrbitAz") / "data.csv")

        if "filename" not in kwargs:
            kwargs["filename"] = filename
        return self.replay(*args, **kwargs)

    def replay(
        self,
        reducer: Callable[[pd.DataFrame], object] = lambda df: df[0],
        filename: Optional[str] = None,
        col_names: Optional[list[str]] = None,
        *args,
        **kwargs,
    ) -> Callable:
        """
        Decorator used to replay data from files, conditionally.
        """

        # TODO check args and kwargs for unexpected inputs (it should
        # only be the func to be decorated)

        # This is the actual decorator
        def decorator(func: Callable):
            # Activity here is processed at load-time
            logger.debug(f"Decorating function '{func.__name__}'")

            # This defines the functionality the decorator should do
            @wraps(func)
            def _replay(*_args, **_kwargs):
                if self.replay_mode:
                    nonlocal filename, col_names, reducer
                    if filename is None:
                        raise AstroPiExecutorException("Cannot have empty filename")
                    if col_names is None:
                        col_names = [func.__name__]

                    return self._replay_next(
                        filename, self.datetime_col, col_names, reducer
                    )
                else:
                    return func(*_args, **_kwargs)

            return _replay

        # This deals with the standard decorator case (no brackets)
        # whereby: no kwargs + standard func positional arg
        # is given.
        if len(kwargs) == 0 and len(args) > 0 and callable(args[0]):
            logger.debug("Standard decorator")
            return partial(decorator, args[0])
        # Otherwise, return the actual decorator function
        else:
            logger.debug("Returning actual decorator")
        return decorator

    @staticmethod
    def run(
        execution_mode: Optional[ExecutionMode],
        venv_dirname: Optional[Path],
        main: Path,
    ) -> None:
        """
        This method runs the given main file using the given execution mode.
        If the passed in execution mode is Replay mode, then creates a venv
        in the venv_dirname if it does not already exist.

        execution_mode: Whether to replay data or capture live data.
        venv_dirname: The directory to create the venv in replay mode, if it does not
        exist.
        main: The filename to execute - generally called main.py.
        """

        if execution_mode is None:
            execution_mode = AstroPiExecutor._detect_execution_mode()
            logging.debug(f"Detected execution mode: {execution_mode}")
        if not main.exists() or not main.is_file():
            raise AstroPiExecutorException(f"File {main} is not a regular file")

        env: Optional[dict[str, str]]
        python3: str

        # Conditionally create the venv
        if execution_mode == ExecutionMode.REPLAY:
            if venv_dirname is None:
                logging.debug("venv_dirname is None - fetching value from env")
                venv_dirname = (
                    Path(os.environ.get("HOME", tempfile.gettempdir()))
                    / f".{PROGRAM_NAME}"
                )
                logging.debug(f"Found {venv_dirname}")

            venv_dir: Path = AstroPiExecutor._setup_venv(venv_dirname)

            # Prepare the environment to be used in the subprocess.
            env = os.environ.copy()
            env["PATH"] = ":".join([str(Path(venv_dir) / "bin"), env["PATH"]])
            env["VIRTUAL_ENV"] = str(venv_dir)

            python3 = str(venv_dir / "bin" / "python3")
        else:
            logging.debug("Running in live mode")
            env = None
            python3 = "python3"

        # Add if __name__ == "__main__" guard as needed
        # (required by multiprocessing in CameraPreview currently FIXME)
        main = AstroPiExecutor.add_name_is_main_guard(main)

        # Run the program that was passed in
        if platform.system() in ["Linux", "Darwin", "Windows"]:
            # -u is for unbuffered Python, which is what is used on the
            # Astro Pis on the ISS.
            args: list[str] = [python3, "-u", str(main.resolve())]
            logging.debug(f"Executing '{' '.join(args)}' in subprocess")
            subprocess.run(
                args, env=env if env is not None else env, check=True
            )  # nosec B603: runs main as intended
        else:
            raise OSError(f"Unsupported system {os}")

    def _find_next_datum(self, df: pd.DataFrame) -> int:
        """
        Finds the next row in the given dataframe indexed by
        datetime, based on the elapsed time.
        """
        start_time = self._state._start_time
        now = datetime.now()
        delta_in_seconds = pd.Timedelta(
            round((now - start_time).total_seconds()), "seconds"
        )
        first_time = df.iloc[0].name
        proposed_time = first_time + delta_in_seconds

        # Find the nearest time using the proposed time
        nearest_i = df.index.get_indexer(pd.Index([proposed_time]), method="nearest")[0]
        logging.debug(f"Nearest i: {nearest_i}")
        self._state._last_sense_hat_row_index = nearest_i
        return nearest_i

    def time_since_start(self) -> datetime:
        """Time relative to the original start time, as specified
        in the metadata.json file"""
        execution_start_time: datetime = self._state._start_time
        now: datetime = datetime.now()
        delta: timedelta = now - execution_start_time

        original_start_time: datetime = get_start_time()
        return original_start_time + delta

    # Static methods

    @staticmethod
    def _detect_execution_mode() -> ExecutionMode:
        return (
            ExecutionMode.LIVE
            if all(
                importlib.util.find_spec(module) is not None
                for module in AstroPiExecutor.MODULES_TO_STUB
            )
            else ExecutionMode.REPLAY
        )

    @functools.cache
    def _df_from_replay_file(self, filename: str, datetime_col: str) -> pd.DataFrame:
        # Detect file type
        suffix = filename.split(".")[-1]
        if suffix == "csv":
            df = pd.read_csv(filename, parse_dates=[datetime_col])
        elif suffix == "tsv":
            df = pd.read_csv(filename, sep="\t", parse_dates=[datetime_col])
        elif suffix == "parquet":
            df = pd.read_parquet(
                filename,
            )
        else:
            raise AstroPiExecutorException(f"Unsupported filetype '{suffix}'.")
        df = df.set_index(datetime_col)
        return df

    def _replay_next(
        self,
        filename: str,
        datetime_col: str,
        col_names: list[str],
        reducer: Callable[[pd.DataFrame], object] = lambda s: s[0],
    ) -> object:
        """Internal method that opens the given filename and
        returns the given col names, using the reducer. In effect,
        this replays the data."""

        df = self._df_from_replay_file(filename, datetime_col)

        for col_name in col_names:
            if col_name not in df.columns:
                raise AstroPiExecutorException(
                    f"Column '{col_name}' not found "
                    + f"in file '{filename}'.\n\n"
                    + "Detected columns: \n\t"
                    + ", ".join(df.columns)
                )

        nearest_i = self._find_next_datum(df)

        return reducer(df[col_names].iloc[nearest_i])

    @staticmethod
    def _check_package_installed(venv_python3) -> subprocess.CompletedProcess[str]:
        """
        Runs a program using the venv Python to check if
        the current package is installed.
        """
        dynamic_program: str = "; ".join(
            [
                "import importlib.util",
                "from pathlib import Path",
                "module = importlib.util.find_spec(" + f"'{PROGRAM_NAME}')",
                f"to_print = '{AstroPiExecutor.NOT_FOUND}' if module is None "
                + "else Path(module.origin).parent",
                "print(to_print)",
            ]
        )

        out = subprocess.run(  # nosec B603: no user input
            [venv_python3, "-c", dynamic_program],
            check=True,
            capture_output=True,
            text=True,
        )
        return out

    @staticmethod
    def add_name_is_main_guard(main: Path) -> Path:
        """
        Checks if the file at the given path includes an if name == "__main__"
        expression. If it does, returns the same file.
        Otherwise, returns a modified copy of the file with the original contents
        inside the if expression.
        """
        substrings: list[str] = [
            'if __name__ == "__main__":',
            "if __name__ == '__main__':",
        ]
        with main.open("r") as f:
            contents = f.read().strip()

        includes_guard = False
        for substring in substrings:
            if substring in contents:
                includes_guard = True
        logger.debug(f"Main file includes guard: {includes_guard}")

        if includes_guard:
            return main
        else:
            tabbed = os.linesep.join([f"    {line}" for line in contents.splitlines()])
            if len(tabbed) == 0:
                tabbed = "    pass"

            tempdir = Path(tempfile.gettempdir())
            main_copy: Path = tempdir / "main.py"
            if main_copy.exists():
                os.remove(main_copy)
            with main_copy.open("w") as f:
                f.write(substrings[0] + os.linesep)
                f.write(tabbed)
            return main_copy

    @staticmethod
    def _setup_venv(venv_dirname: Path, name: str = "venv") -> Path:
        """
        Creates a new venv with the given name in the given venv_dirname
        using the venv module.
        """
        # 1. Create or copy the venv to the venv_dir, depending on if we're
        # already in one
        venv_dir: Path = venv_dirname / name

        if venv_dir.exists():
            logger.debug("venv already created - skipping")
            return venv_dir
        else:
            logging.debug("Creating venv")

        if AstroPiExecutor.is_in_venv:
            logger.info(
                "Detected that you running in a venv:"
                + f"\n\t{sys.prefix}.\n"
                + "However, running in replay mode will use a "
                + "separate copied (modified) venv."
            )
            shutil.copytree(sys.prefix, venv_dir, symlinks=True)
        else:
            venv.create(
                venv_dir, symlinks=True, system_site_packages=True, with_pip=True
            )

        # 2. Install the executor package as required
        logger.debug("Installing stubbed modules in the venv...")

        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        venv_site_packages_dir = venv_dir / "lib" / python_version / "site-packages"
        venv_pip = str(venv_dir / "bin" / "pip")
        venv_python3 = str(venv_dir / "bin" / "python3")

        # Is astro_pi_executor already installed in the new venv?
        out = AstroPiExecutor._check_package_installed(venv_python3)

        if out.stdout.strip() == AstroPiExecutor.NOT_FOUND:
            # install the module
            logger.debug(f"Installing {PROGRAM_NAME} into venv...")
            subprocess.run(
                [venv_pip, "install", "."], check=True
            )  # nosec B603: no user input
            out = AstroPiExecutor._check_package_installed(venv_python3)

        executor_installed_path = Path(out.stdout.strip())
        if not executor_installed_path.exists():
            raise AstroPiExecutorException(
                f"Could not set up {PROGRAM_NAME} environment"
            )

        logger.debug(f"Found {PROGRAM_NAME} installed at {executor_installed_path}")

        # 3. Install stubs into the venv
        logger.debug("Installing stubbed modules in the venv...")

        for module in AstroPiExecutor.MODULES_TO_STUB:
            logger.debug(f"Installing {module}")
            shutil.copytree(
                executor_installed_path / module, venv_site_packages_dir / module
            )

        return venv_dir


# TODO check that sense_hat can be imported when executed via astro_pi_executor

# Integration tests:
# - using qemu?
# - On Windows, Linux, Darwin ensure that the adapter can be installed
# - On RP4, ensure it calls the real lib (integration test) - I should test this now...!
# perhaps an i2c bus can be emulated...
