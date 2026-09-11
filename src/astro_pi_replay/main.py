import argparse
import asyncio
import cProfile
import datetime
import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from requests.exceptions import ConnectionError, HTTPError, Timeout

from astro_pi_replay import LOGGING_FORMAT, PROGRAM_CMD_NAME, PROGRAM_NAME, __version__
from astro_pi_replay.configuration import Configuration, populate_argparser_from_dataclass
from astro_pi_replay.runtime_state import state
from astro_pi_replay.custom_types import ExecutionMode
from astro_pi_replay.exception import AstroPiReplayRuntimeError
from astro_pi_replay.executor import AstroPiExecutor
from astro_pi_replay.resources import Downloader, get_resource
from astro_pi_replay.resources.downloader import has_installed
from astro_pi_replay.runtime_state import state
from astro_pi_replay.self_updater import SelfUpdater

logger = logging.getLogger(__name__)
logging.Formatter.formatTime = (  # type: ignore[method-assign]
    lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(
        record.created, datetime.timezone.utc
    )
    .astimezone()
    .isoformat(sep="T", timespec="milliseconds")
)


RUN_CMD: str = "run"
DOWNLOAD_CMD: str = "download"
UPDATE_CMD: str = "update"
VERSION_CMD: str = "version"
INSTALL_CMD: str = "install"
CONFIGURE_CMD: str = "configure"

DEFAULT_PHOTOGRAPHY_TYPE: str = "VIS"
DEFAULT_RESOLUTION: tuple[int,int] = (4056, 3040)

async def get_argument_parser() -> ArgumentParser:
    arg_parser = ArgumentParser(prog=PROGRAM_CMD_NAME, description="")
    arg_parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        help="Emit debug messages",
        default=os.environ.get(f"{PROGRAM_NAME.upper()}_DEBUG", None),
    )
    arg_parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable profiling (to stdout unless " + "--profile-filename is specified)",
    )
    arg_parser.add_argument(
        "--profile-filename", help="Redirect profiling output to " + "a file"
    )
    subparsers = arg_parser.add_subparsers(help="sub-command help")

    download_parser = subparsers.add_parser(
        DOWNLOAD_CMD, help="Download the photos to use during run (required)"
    )
    download_parser.set_defaults(cmd="download")
    download_parser.add_argument(
        "--test-assets-only",
        action="store_true",
        default=False,
        help="Downloads only the files required " + "for the automated tests to pass.",
    )
    download_parser.add_argument(
        "--with-video",
        action="store_true",
        default=False,
        help="Whether to download the video assets",
    )
    download_parser.add_argument(
        "--resolution",
        default=None,
        choices=((4056, 3040), (1280, 720)),
        help="The resolution of images to playback. Default is (4056, 3040)",
    )
    download_parser.add_argument(
        "--photography-type",
        default=None,
        choices=(("VIS", "IR")),
        help="Whether to playback visible light photos "
        + "(VIS) or infrared light (IR). Default is VIS.",
    )
    download_parser.add_argument(
        "--sequence", default=None,
        help="The sequence id to use in replays."
    )

    run_parser = subparsers.add_parser(RUN_CMD, help="Run a main.py program")
    run_parser.add_argument("main", type=Path, help="Path to the main.py file to run")
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

    await populate_argparser_from_dataclass(
        run_parser,
        Configuration
    )

    run_parser.set_defaults(cmd="run")
    update_parser = subparsers.add_parser(
        UPDATE_CMD, help="Check for updates to the Astro-Pi-Replay tool and update."
    )
    update_parser.set_defaults(cmd=UPDATE_CMD)
    update_parser.add_argument(
        "--venv_dir",
        type=Path,
        required=False,
        help=f"Path to venv (if not using ~/.{PROGRAM_NAME})",
    )
    version_parser = subparsers.add_parser(
        VERSION_CMD, help="Print out the current version of the tool."
    )
    version_parser.set_defaults(cmd=VERSION_CMD)

    install_parser = subparsers.add_parser(
        INSTALL_CMD, help="Installs the internal libraries globally"
    )
    install_parser.set_defaults(cmd=INSTALL_CMD)

    configure_parser = subparsers.add_parser(
        CONFIGURE_CMD, help="Resolve and save the requested configuration"
    )
    configure_parser.set_defaults(cmd=CONFIGURE_CMD)
    await populate_argparser_from_dataclass(
        configure_parser,
        Configuration
    )

    return arg_parser


async def _main(args: Namespace) -> None:
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=LOGGING_FORMAT
    )

    logger.debug(args)

    config = await Configuration.resolve_configuration(args)

    if hasattr(args, "cmd"):
        downloader = Downloader()
        self_updater: SelfUpdater = SelfUpdater()
        if args.cmd == "run":
            self_updater.check_for_updates()


            logger.debug(f"Selected {config.sequence}")

            if not config.streaming_mode and not await has_installed(
                config.resolution, config.photography_type, config.sequence
            ):
                try:
                    await downloader.install(
                        config.resolution, config.photography_type, config.sequence
                    )
                except (Timeout, ConnectionError, HTTPError) as e:
                    logger.debug(e)
                    state.is_offline = True

                if state.is_offline:
                    raise AstroPiReplayRuntimeError(
                        os.linesep.join(
                            [
                                "It looks like you are offline.",
                                "You must be online to download "
                                + f"the photo sequence '{config.sequence}'.",
                            ]
                        )
                    )

            with get_resource("motd").open("r") as f:
                sys.stdout.write(f.read())

            config.save() # overwrite

            AstroPiExecutor.run(args.mode, args.venv_dir, args.main, config.debug)
        elif args.cmd == "download":
            await downloader.check_for_sequences_override()
            await downloader.install(
                config.resolution,
                config.photography_type,
                config.sequence,
                args.test_assets_only,
                args.with_video
            )
        elif args.cmd == UPDATE_CMD:
            self_updater.update(args.venv_dir)
            sys.exit(0)
        elif args.cmd == VERSION_CMD:
            print(f"{PROGRAM_CMD_NAME}: {__version__}")
            sys.exit(0)
        elif args.cmd == INSTALL_CMD:
            AstroPiExecutor.install_global()
        elif args.cmd == CONFIGURE_CMD:
            logger.debug("Saving config")
            config.save()
        else:
            (await get_argument_parser()).print_usage()
            sys.exit(1)


def main() -> None:
    arg_parser = asyncio.run(get_argument_parser())

    args: Namespace = arg_parser.parse_args(sys.argv[1:])
    if args.profile:
        logger.debug("Profiling enabled")
        if hasattr(args, "profile_filename"):
            logger.debug(f"Redirecting profile output to {args.profile_filename}")
            cProfile.runctx(
                "_main(args)",
                globals(),
                locals(),
                filename=args.profile_filename,
                sort="cumulative",
            )
            logger.info(
                "Convert profile output to svg: gprof2dot -f pstats "
                + f"{args.profile_filename} | dot -Tsvg -o {args.profile_filename}.svg"
            )
        else:
            cProfile.runctx("_main(args)", globals(), locals(), sort="cumulative")
    else:
        asyncio.run(_main(args))

if __name__ == "__main__":
    sys.exit(main())
