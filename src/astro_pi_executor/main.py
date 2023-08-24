import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from astro_pi_executor import PROGRAM_NAME
from astro_pi_executor.configuration import Configuration
from astro_pi_executor.custom_types import ExecutionMode
from astro_pi_executor.downloader import Downloader
from astro_pi_executor.executor import AstroPiExecutor, AstroPiExecutorException
from astro_pi_executor.resources import RESOURCE_DIR, get_resource

logger = logging.getLogger(__name__)

RUN_CMD: str = "run"
DOWNLOAD_CMD: str = "download"


def get_argument_parser() -> ArgumentParser:
    arg_parser = ArgumentParser(prog=PROGRAM_NAME, description="")
    arg_parser.add_argument("--debug", action="store_true", help="Emit debug messages")
    subparsers = arg_parser.add_subparsers(help="sub-command help")

    download_parser = subparsers.add_parser(
        DOWNLOAD_CMD, help="Download the photos to use during run (required)"
    )
    # download_parser.add_argument("--force-reinstall", action="store_true",
    #                            help="Forcibly reinstall the venv used to replay data")
    download_parser.set_defaults(cmd="download")

    run_parser = subparsers.add_parser(RUN_CMD, help="Run a main.py program")
    run_parser.add_argument("main", type=Path, help="Path to the main.py file to run")
    run_parser.add_argument(
        "--no-match-original-photo-intervals",
        action="store_true",
        default=False,
        help="Disable this mode to stop sleeping in between successive captures to "
        + "try and match the timestamps of the original photos.",
    )
    run_parser.add_argument(
        "--mode",
        type=ExecutionMode,
        required=False,
        help="Whether to replay data (REPLAY) or fetch" + "live data (LIVE)",
    )
    run_parser.add_argument(
        "--venv_dir",
        type=Path,
        required=False,
        help=f"Path to venv (if not using ~/.{PROGRAM_NAME})",
    )
    run_parser.set_defaults(cmd="run")

    return arg_parser


def _main(args: Namespace) -> None:
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    logger.debug(args)
    if hasattr(args, "cmd"):
        downloader = Downloader()
        if args.cmd == "run":
            if not downloader.has_installed():
                raise AstroPiExecutorException(
                    "Photos not yet downloaded. Please run "
                    + f"{PROGRAM_NAME} {DOWNLOAD_CMD} to download the photos "
                )
            with get_resource("motd").open("r") as f:
                sys.stdout.write(f.read())

            Configuration.from_args(args).save()
            AstroPiExecutor.run(args.mode, args.venv_dir, args.main, args.debug)
        elif args.cmd == "download":
            if downloader.has_installed():
                logger.info("Assets already downloaded and installed - skipping")
            else:
                downloader.download(RESOURCE_DIR)
                logger.info("Installing images...")
                downloader.install(RESOURCE_DIR)
                logger.info("Installation complete")
        else:
            get_argument_parser().print_usage()
            sys.exit(1)


def main() -> None:
    arg_parser = get_argument_parser()
    args: Namespace = arg_parser.parse_args(sys.argv[1:])
    _main(args)
