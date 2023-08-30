#!/usr/bin/env bash

cleanup() {
  unset ASTRO_PI_EXECUTOR_REPLAY_DIR
  unset PYTEST_PROFILE
}

trap 'cleanup' EXIT

VENV=venv
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -r requirements.txt
export ASTRO_PI_EXECUTOR_REPLAY_DIR=replay_tests
export PYTEST_PROFILE=SMOKE_TESTS
pytest -o log_cli=true --log-cli-level=DEBUG --noconftest
