#!/usr/bin/env bash

usage() {
  echo "$0 [PYTEST_PROFILE]"
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

VENV="venv"
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -r requirements.txt
PYTEST_PROFILE="$1" pytest -s -o log_cli=true --log-cli-level=DEBUG --noconftest
