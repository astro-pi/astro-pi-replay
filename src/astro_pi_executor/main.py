import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from astro_pi_executor import PROGRAM_NAME
from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.types import ExecutionMode

logger = logging.getLogger(__name__)


def main() -> None:
    arg_parser = ArgumentParser(prog=PROGRAM_NAME, description="")

    arg_parser.add_argument("main", type=Path, help="Path to the main.py file to run")
    arg_parser.add_argument("--debug", action="store_true", help="Emit debug messages")
    # TODO
    # arg_parser.add_argument("--force-reinstall", action="store_true",
    #                        help="Forcibly reinstall the venv used to replay data")
    arg_parser.add_argument(
        "--mode",
        type=ExecutionMode,
        required=False,
        # default=detect_execution_mode(),
        help="Whether to replay data or fetch" + "live data",
    )
    # arg_parser.add_argument("--data_dir", type=Path,
    #                        required=False,
    #                        # default=default_dir,
    #                        help="Path to place downloaded data files")
    arg_parser.add_argument(
        "--venv_dir",
        type=Path,
        required=False,
        # default=default_dir,
        help="Path to place the venv",
    )

    args: Namespace = arg_parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    print(args)
    return AstroPiExecutor.run(args.mode, args.venv_dir, args.main)


# TODO tests!
# TODO check that sense_hat can be imported when executed via astro_pi_executor

# Integration tests:
# - using qemu?
# - On Windows, Linux, Darwin ensure that the adapter can be installed
# - On RP4, ensure it calls the real lib (integration test) - I should test this now...!
# perhaps an i2c bus can be emulated...
