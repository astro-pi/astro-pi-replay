from astro_pi_replay.install_helper import Apt
from test_utils import get_test_resource


def test_apt_run_parser():
    with get_test_resource("python3-numpy-bookworm.txt").open() as f:
        content: str = f.read()
    apt: Apt = Apt()
    apt.parse_run_output(content)
