import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import test_utils
from test_utils import ProgramFixture

logger = logging.getLogger(__name__)

if os.environ.get("PYTEST_PROFILE") != "SMOKE_TESTS":
    pytest.skip("Skipping smoke tests", allow_module_level=True)


@test_utils.prepare_executor_to_run_in_smoke_test_venv
def test_is_installable_from_test_pypi(smoke_test_venv: Path):
    python_version: str = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_packages: Path = smoke_test_venv / "lib" / python_version / "site-packages"
    assert "astro_pi_executor" in os.listdir(site_packages)


@test_utils.prepare_executor_to_run_in_smoke_test_venv
def test_provides_data(smoke_test_venv: Path, sense_hat_program: ProgramFixture):
    astro_pi_executor: Path = smoke_test_venv / "bin" / "astro_pi_executor"
    subprocess.run(
        [astro_pi_executor, sense_hat_program.main], check=True
    )  # nosec B603
    assert sense_hat_program.expected_file.exists()
    with sense_hat_program.expected_file.open() as f:
        contents = f.read()
    logger.debug(f"File contents: {contents}")
    assert re.search(r"(29, 27, 24)", contents) is not None
