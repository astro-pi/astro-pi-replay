from contextlib import ExitStack
from unittest.mock import Mock, patch
import argparse
import io
import os
import re
import tempfile

import pytest

from astro_pi_replay.args import field_metadata
from astro_pi_replay.configuration import Configuration, populate_argparser_from_dataclass
import test.test_utils as test_utils


@pytest.fixture
def parser():
    return argparse.ArgumentParser()

def filter_option_strings(opts):
    """Returns the 'positive' option string"""
    if len(opts) == 2:
        for opt in opts:
            if not opt.startswith("--no"):
                return opt
    return opts[-1]


def strip_whitespace(string: str) -> str:
    # return re.sub(r'\s+', '', string)
    return string

def normalise(string: str) -> str:
    """
    Normalise the given help string to make it comparable
    across Python versions.
    """
    return strip_whitespace(
            string.replace("optional arguments", "options")
    )

@pytest.mark.asyncio
class TestArgBuilding:

    @pytest.fixture(autouse=True)
    def set_terminal_width(self, monkeypatch):
        monkeypatch.setenv("COLUMNS", "100")
    
    async def test_populate_argparser_from_dataclass(
        self,
        parser: argparse.ArgumentParser
    ) -> None:
        # Given
        field_metadata_map = {
            m.name: m for m in field_metadata.values()
        }

        # WHEN

        parser = await populate_argparser_from_dataclass(parser, Configuration)
        parsed_actions = parser._actions

        # THEN
        # there should be 9 actions, plus 1 help action
        assert len(parsed_actions) == 9 + 1


        parsed_actions_map = {
            filter_option_strings(action.option_strings): action \
                    for action in parsed_actions \
                    if action.dest != "help"
        }
        assert len(parsed_actions_map) == 9

        for name, metadata in field_metadata_map.items():
            assert name in parsed_actions_map
            parsed_action = parsed_actions_map[name]

            assert parsed_action.default is None

            assert parsed_action.help is not None
            assert metadata.help in parsed_action.help

            if metadata.type is not None:
                assert parsed_action.type == metadata.type
            if metadata.choices is not None:
                assert parsed_action.choices == metadata.choices

            # dest
            if metadata.dest is not None:
                assert parsed_action.dest == metadata.dest
            assert name in parsed_action.option_strings

            # action
            if metadata.action == argparse.BooleanOptionalAction:
                assert len(parsed_action.option_strings) == 2
                assert isinstance(parsed_action, argparse.BooleanOptionalAction)
            else:
                assert isinstance(parsed_action, argparse._StoreAction)


    async def test_populate_argparser_from_dataclass_populates_help(
        self,
        parser: argparse.ArgumentParser
    ) -> None:

        parser = await populate_argparser_from_dataclass(parser, Configuration)

        expected = test_utils.get_test_resource(
                "expected_help_string.txt").read_text()
        buffer= io.StringIO()
        parser.print_help(buffer)

        actual = buffer.getvalue()

        try:
            assert normalise(actual) == normalise(expected)
        except AssertionError as e:
            fd, name = tempfile.mkstemp()
            os.write(fd, actual.encode())
            print(f"The actual value has been saved to {name}")
            raise e

    async def test_help_string(
        self, parser
    ) -> None:
        # GIVEN
        spies = {}


        with ExitStack() as stack:
            for m in field_metadata.values():
                if m._map_help_default:
                    spy = stack.enter_context(
                            patch.object(
                                m,
                                "_map_help_default",
                                wraps=m._map_help_default)
                    )
                    spies[m.name] = spy

            # WHEN
            parser = await populate_argparser_from_dataclass(
                    parser, Configuration)
            buffer= io.StringIO()
            parser.print_help(buffer)

            # THEN
            for spy in spies.values():
                spy.assert_called_once()
