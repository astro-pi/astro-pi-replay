import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

from astro_pi_replay import PROGRAM_CMD_NAME, PROGRAM_NAME, __version__
from astro_pi_replay.resources import get_replay_dir

logger = logging.getLogger(__name__)
PYPI_URL: str = f"https://pypi.org/simple/{PROGRAM_NAME.replace('_','-')}"


class SelfUpdater:
    @staticmethod
    def compare_semver(first: str, second: str) -> int:
        """
        Returns 0 when first is equal to second
        Returns 1 when first is greater than second
        Returns -1 when first is less than second
        """
        if first == second:
            return 0
        first_as_list: list[str] = first.split(".")
        second_as_list: list[str] = second.split(".")
        for i in range(len(first_as_list)):
            if first_as_list[i] < second_as_list[i]:
                return -1
        return 1

    def _check_for_updates(self) -> list[str]:
        """
        Check PyPi for a new version
        """

        to_return: list[str] = []
        try:
            logger.debug(f"Checking {PYPI_URL} for a new version")
            request = urllib.request.Request(
                PYPI_URL, headers={"Accept": "application/vnd.pypi.simple.v1+json"}
            )
            with urllib.request.urlopen(request, timeout=3) as response:  # nosec: B310
                if response.status != 200:
                    return to_return
                data: bytes = response.read()
                json_data: dict = json.loads(data.decode("utf-8"))

            latest_available: str = json_data["versions"][-1]
            if SelfUpdater.compare_semver(latest_available, __version__) == 1:
                to_return.append(f"An update to {PROGRAM_CMD_NAME} is available")
                to_return.append(f"To update, run {PROGRAM_CMD_NAME} update")
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
        ) as e:
            logger.debug(e)
        return to_return

    def check_for_updates(self) -> None:
        for line in self._check_for_updates():
            logger.info(line)

    def update(self) -> None:
        """
        Update requested (via Astro-Pi-Replay update)
        """
        # temp_dir: Path = Path(mkdtemp())
        replay_dir: Path = get_replay_dir()
        import astro_pi_replay

        logger.debug(f"{PROGRAM_CMD_NAME} package is at: {astro_pi_replay.__path__}")
        logger.debug(f"Replay resource dir is at {replay_dir}")
        is_relative: bool = all(
            (replay_dir.is_relative_to(pth) for pth in astro_pi_replay.__path__)
        )
        logger.debug(f"Resource dir is relative to package: {is_relative}")

        # subprocess.run(["pip", "install", "--update", "astro_pi_replay"], check=True)
        # try:

        #     # import astro_pi_replay.__path__
        #     # Backup current location Move the resources dir to a temp directory
        #     shutil.move(replay_dir, temp_dir)

        #     logger.debug("Running with pip")
        #     subprocess.run([
        #         "pip",
        #         "install",
        #         "--update",
        #         "astro_pi_replay"
        #     ], check=True)

        # finally:
        #     # move the resources back
        #     shutil.move(temp_dir, replay_dir)
