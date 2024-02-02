import pytest

from astro_pi_replay.version_utils import compare_semver, decrement_semver


@pytest.mark.parametrize(
    "v1,v2,ignore_patch,expected",
    [
        # - Include patch
        # less than
        ("2.9.0", "3.10.0", False, -1),
        ("3.9.0", "3.10.0", False, -1),
        ("3.9.0", "3.9.1", False, -1),
        # equals
        ("3.9.0", "3.9.0", False, 0),
        # greater than
        ("3.10.0", "2.9.0", False, 1),
        ("3.10.0", "3.9.0", False, 1),
        ("3.10.1", "3.10.0", False, 1),
        # - Ignore patch
        # less than
        ("2.9.0", "3.10.0", True, -1),
        ("3.9.0", "3.10.0", True, -1),
        ("3.9.0", "3.9.1", True, 0),
        # equals
        ("3.9.0", "3.9.0", True, 0),
        # greater than
        ("3.10.0", "2.9.0", True, 1),
        ("3.10.0", "3.9.0", True, 1),
        ("3.10.1", "3.10.0", True, 0),
    ],
)
def test_compare_semver(v1: str, v2: str, ignore_patch: bool, expected: int):
    actual: int = compare_semver(v1, v2, ignore_patch=ignore_patch)
    assert actual == expected


@pytest.mark.parametrize(
    "version,expected", [("1.1.1", "1.1.0"), ("1.1.0", "1.0.0"), ("1.0.0", "0.0.0")]
)
def test_decrement_semver_decrements(version: str, expected: str):
    assert decrement_semver(version) == expected


def test_decrement_semver_raises_exception_when_nothing_to_decrement():
    with pytest.raises(ValueError):
        decrement_semver("0.0.0")
