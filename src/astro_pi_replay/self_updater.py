import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import mkdtemp
from typing import Optional

import requests
from requests.exceptions import RequestException

from astro_pi_replay import PROGRAM_CMD_NAME, PROGRAM_NAME, __version__
from astro_pi_replay.resources import get_replay_dir
from astro_pi_replay.venv_resolver import VenvResolver

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
            response: requests.Response = requests.get(
                PYPI_URL,
                headers={"Accept": "application/vnd.pypi.simple.v1+json"},
                timeout=3,
            )
            if response.status_code != 200:
                return to_return
            json_data: dict = json.loads(response.content.decode("utf-8"))

            latest_available: str = json_data["versions"][-1]
            if SelfUpdater.compare_semver(latest_available, __version__) == 1:
                to_return.append(f"An update to {PROGRAM_CMD_NAME} is available")
                to_return.append(f"To update, run {PROGRAM_CMD_NAME} update")
        except (
            RequestException,
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

    def _update(self, venv: VenvResolver) -> None:
        subprocess.run(  # nosec B603
            [str(venv.venv_info.pip), "install", "--update", "astro_pi_replay"],
            check=True,
        )
        logger.info("Update complete")

    def update(self, venv_dirname: Optional[Path] = None) -> None:
        """
        Update requested (via Astro-Pi-Replay update)
        """
        venv_path: Path = venv_dirname if venv_dirname is not None else Path(sys.prefix)
        venv: VenvResolver = VenvResolver(venv_path, init_venv=False)

        # move the replay dirs to a temporary location to avoid redownloading them
        temp_dir: Path = Path(mkdtemp())
        replay_dir: Path = get_replay_dir()
        shutil.move(replay_dir, temp_dir)
        success: bool = False
        try:
            # now the replay dir is currently temp_dir / replay_dir.name
            self._update(venv)
            success = True
        finally:
            if success:
                shutil.move(
                    temp_dir / replay_dir.name,
                    venv.venv_info.site_packages_dir / PROGRAM_NAME / "resources",
                )
            else:
                shutil.move(temp_dir / replay_dir.name, replay_dir.parent)
