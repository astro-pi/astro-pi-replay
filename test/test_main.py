"""
These tests ensure that the venv is setup correctly and the appropriate
mode is selected
"""
from unittest import mock
import pytest
import astro_pi_executor.main 
from astro_pi_executor.main import ExecutionMode
from test_utils import raspberry_pi_os_only
from argparse import Namespace
from pathlib import Path
import os.path
import os

# TODO test commandline arg parse
def test_main_parses_args_correctly():
    pass

