# from mock import Mock
from packaging import version
from packaging.version import Version

from astro_pi_replay import __version__


def test_check_for_updates_returns_true_when_update_available():
    current_version: Version = version.parse(__version__)
    incremented_version: str = (
        f"{current_version.major}."
        + f"{current_version.minor}."
        + f"{current_version.micro}"
    )
    print(incremented_version)

    # TODO mock version from pypi api

    pass


def test_check_for_updates_returns_false_when_updates_unavailable():
    current_version: Version = version.parse(__version__)
    print(current_version)
    # TODO mock version from pypi api
    pass


def test_self_updater_updates_files_successfully():
    # TODO mock pip install --update or implement using copy...
    # assert that new files are added, files are modified, and files are deleted.
    # check especially what happens if the current (self_updater.py) is modified
    pass
