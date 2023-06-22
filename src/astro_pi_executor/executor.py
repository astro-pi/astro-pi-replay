from datetime import datetime
from typing import Callable, Optional
from pathlib import Path
import logging
from functools import wraps, partial

import pandas as pd
import sys
import venv
import shutil
from importlib.machinery import ModuleSpec
import importlib.util
from astro_pi_executor import PROGRAM_NAME
from astro_pi_executor.types import ExecutionMode
import subprocess
import platform
import os
import tempfile

logger = logging.getLogger(__name__)

class AstroPiExecutorState:
    """
    Wrapper class for the executor's shared, mutable state.
    """
    
    def __init__(self):
        self._last_row_index: int = 0
        self._start_time: datetime = datetime.now()

class AstroPiExecutorException(Exception):

    def __init__(self, message: str):
        self.message: str = message
        super().__init__(message)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message

class AstroPiExecutor:
    """
    Class containing the replaying logic + the CLI main m

    This class is instantiated (by the API adapter classes) only
    when ExecutionMode is REPLAY, in order control the replaying
    of data. Otherwise, its static methods are used to setup a 
    venv and run main.py files.
    """
    # TODO refactor to expose function style in addition to decorator style

    # MODULES_TO_STUB: list[str] = ["sense_hat", "picamera", "orbit", "skyfield"]
    MODULES_TO_STUB: list[str] = ["sense_hat"]

    """
    Checks whether the current interpreter is running in a venv,
    as defined here in https://docs.python.org/3/library/venv.html#how-venvs-work
    """
    is_in_venv: bool = sys.prefix != sys.base_prefix

    def __init__(self, 
                 datetime_col: str="Date/Time",
                 # example: 2022-01-31 12:21:15
                 datetime_format: str= "%Y-%m-%d %H:%M:%S",
                 replay_mode: bool=True,
                 state: AstroPiExecutorState=AstroPiExecutorState()):
        self.datetime_col: str = datetime_col
        self.datetime_format: str = datetime_format
        self.replay_mode: bool = replay_mode
        self._state: AstroPiExecutorState = state

        # TODO add option to be a bit like easyrandom / haskell type testing
        #random_mode = False # whether or not to randomly generate data
        # mode: ir or vis

    def sense_hat_replay(self, *args, **kwargs):
        """
        Decorator used to conditionally replay data from file for the SenseHat.
        """
        # TODO use the data dir
        filename = str(Path(__file__).parent / "sense_hat" / "data" / "astro_pi_mark_2_commissioning_data_ir.tsv")
        if "filename" in kwargs:
            filename = kwargs["filename"]
        return self.replay(filename=filename, *args, **kwargs)

    def replay(self, 
               reducer: Callable[[pd.Series], object]=lambda s: s[0],
               filename: Optional[str]=None, 
               col_names: Optional[list[str]]=None, 
               *args, 
               **kwargs) -> Callable:
        """
        Decorator used to replay data from files, conditionally.
        """

        # TODO check args and kwargs for unexpected inputs (it should
        # only be the func to be decorated)

        #This is the actual decorator
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

                    # Detect file type
                    suffix = filename.split(".")[-1]
                    if suffix == "csv":
                        df = pd.read_csv(filename, 
                                         parse_dates=[self.datetime_col])
                    elif suffix == "tsv":
                        df = pd.read_csv(filename, 
                                         sep="\t",
                                         parse_dates=[self.datetime_col])
                    elif suffix == "parquet":
                        df = pd.read_parquet(filename, )
                    else: 
                        raise AstroPiExecutorException(f"Unsupported filetype '{suffix}'.")
                    df = df.set_index(self.datetime_col)

                    for col_name in col_names:
                        if col_name not in df.columns:
                            raise AstroPiExecutorException(f"Column '{col_name}' not found " +
                                                           f"in file '{filename}'.\n\n" +
                                                           "Detected columns: \n\t" +
                                                           ", ".join(df.columns))


                    # Now to find the most appropriate row, based on the amount of time
                    # elapsed. This area needs to be optimised.
                    start_time = self._state._start_time
                    now = datetime.now()
                    delta_in_seconds = pd.Timedelta(round((now - start_time).total_seconds()), "seconds")
                    first_time = df.iloc[0].name
                    proposed_time = first_time + delta_in_seconds

                    # Find the nearest time using the proposed time
                    nearest_i = df.index.get_indexer(pd.Index([proposed_time]), method="nearest")[0]
                    self._state._last_row_index = nearest_i

                    return reducer(df[col_names].iloc[nearest_i])
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
    def _detect_execution_mode() -> ExecutionMode:
        return ExecutionMode.LIVE if all(importlib.util.find_spec(module) is not None \
                for module in AstroPiExecutor.MODULES_TO_STUB) \
                else ExecutionMode.REPLAY

    @staticmethod
    def run(execution_mode: Optional[ExecutionMode], 
            venv_dirname: Optional[Path], main: str):
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

        # Conditionally create the venv
        if execution_mode == ExecutionMode.REPLAY:

            if venv_dirname is None:
                venv_dirname = Path(os.environ.get("HOME", 
                                                   tempfile.gettempdir())) / f".{PROGRAM_NAME}"


            venv_dir: Path = AstroPiExecutor._setup_venv(venv_dirname)

            # Prepare the environment to be used in the subprocess.
            env: Optional[dict[str,str]] = os.environ.copy()
            env["PATH"] = ":".join([str(Path(venv_dir) / "bin"), env["PATH"]])
            env["VIRTUAL_ENV"] = str(venv_dir)

            python3: str = str(venv_dir / "bin" / "python3")
        else:
            env: Optional[dict[str,str]] = None
            python3: str = "python3"

        # Run the program that was passed in 
        if platform.system() in ["Linux", "Darwin", "Windows"]:
            # -u is for unbuffered Python, which is what is used on the
            # Astro Pis on the ISS.
            subprocess.run([python3, "-u", main], 
                           env=env if env is not None else env,
                           check=True)
        else:
            raise OSError(f"Unsupported system {os}")


    @staticmethod
    def _setup_venv(venv_dirname: Path, 
                    name:str ="venv") -> Path:
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
            logger.info(f"Detected that you running in a venv:" +
                         f"\n\t{sys.prefix}.\n" +
                         "However, running in replay mode will use a " +
                         "separate copied (modified) venv.")
            shutil.copytree(sys.prefix, venv_dir)
        else:
            venv.create(venv_dir, symlinks=True,
                        system_site_packages=True,
                        with_pip=True)

        # 2. Install the stubbed modules as required
        logger.debug("Installing stubbed modules in the venv...")

        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        venv_site_packages_dir = venv_dir / "lib" / python_version / "site-packages"
        venv_pip = str(venv_dir / "bin" / "pip")
        venv_python3 = str(venv_dir / "bin" / "python3")
        
        # It's not guaranteed that the executor will be installed directly
        # in the current venv's site-packages dir. Therefore, check if it is
        # installed using importlib.util.find_spec.
        module_info: Optional[ModuleSpec] = importlib.util.find_spec(PROGRAM_NAME)
        if module_info is None:
            logger.debug(f"Installing {PROGRAM_NAME} into venv...")
            subprocess.run([venv_pip, "install", "."], check=True)
        else:
            executor_installed_path: Path = Path(str(module_info.origin)).parent

        logger.debug("Installing stubbed modules in the venv...")
        dynamic_program = "; ".join([
                "import importlib.util",
                "from pathlib import Path",
                f"print(Path(importlib.util.find_spec('{PROGRAM_NAME}').origin).parent)"
        ])

        out = subprocess.run([venv_python3, "-c", dynamic_program], 
                             check=True, capture_output=True, text=True)
        executor_installed_path = Path(out.stdout.strip())

        logger.debug(f"Found {PROGRAM_NAME} installed at {executor_installed_path}")

        for module in AstroPiExecutor.MODULES_TO_STUB:
            shutil.copytree(executor_installed_path / module,
                            venv_site_packages_dir / module)

        return venv_dir

# TODO tests!
# TODO check that sense_hat can be imported when executed via astro_pi_executor

# Integration tests:
# - using qemu?
# - On Windows, Linux, Darwin ensure that the adapter can be installed
# - On RP4, ensure it calls the real lib (integration test) - I should test this now...!
    # perhaps an i2c bus can be emulated...
