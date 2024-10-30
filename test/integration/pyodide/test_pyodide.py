from pathlib import Path
from typing import Generator, Any
import dataclasses
import os
import pytest
import tempfile
import uuid

from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs
import requests

CURRENT_DIR: Path = Path(__file__).parent
PROJECT_DIR: Path = Path(__file__).parent.parent.parent.parent
WHEEL_DIR: Path = CURRENT_DIR / "wheels"
WORKER_UTILS: Path = CURRENT_DIR / "worker-utils.js"
REPLAY_TOOL_ONLINE_R3_URL: str = "https://astro-pi-replay-online-static.astro-pi.org/releases/v0.4/"


if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)


@dataclasses.dataclass
class Script:
    script: str
    filepath: str
    expected_string: str 


@pytest.fixture()
def script() -> Generator[Script, Any, Any]:
    """
    Generates a script to install the replay tool into
    Pyodide.
    """
    script: str = """\
    import { loadPyodide } from 'pyodide';
    import { installAstroPiReplayTool } from './worker-utils.js';
    
    async function install() {
      let pyodide = await loadPyodide();
      return installAstroPiReplayTool(pyodide);
    }
    
    await install();
    """
    expected_string: str = f"Done installing {uuid.uuid4()}"
    script += f'console.log("{expected_string}");';
    with tempfile.NamedTemporaryFile(mode="w") as temp_file:
        temp_file.write(script)
        yield Script(script, temp_file.name, expected_string)

def fetch_replay_tool_online_assets():
    # Install the custom wheels
    if not WORKER_UTILS.exists():
        requests.get(f"{REPLAY_TOOL_ONLINE_R3_URL}/worker-utils.js")
        with WORKER_UTILS.open() as f:
            contents = f.read()
        # Use the kkkm dir instead of test_data
        # TODO add env var into astro-pi-replay
        with WORKER_UTILS.open("w") as f:
            f.write(contents.replace("kkkm", "test_data"))


def test_installs_in_pyodide(script: Script):
    with DockerImage(
        path=CURRENT_DIR,
        tag="replay-test") as image:

        # Creates volumes for the wheels dir and
        # set the environment variable to install
        # a custom wheel
        with DockerContainer(str(image)) \
            .with_volume_mapping(
                host=str(CURRENT_DIR / "wheels"), 
                container="/wheels") \
            .with_env(
                key="ASTRO_PI_REPLAY_INSTALL_URL",
                value="/wheels"
            ) \
            .with_volume_mapping(
                  host=script.filepath,
                  container="/opt/pyodide-tests/script.js") \
            as container:

            wait_for_logs(container, script.expected_string)

