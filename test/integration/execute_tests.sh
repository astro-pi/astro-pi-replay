#!/usr/bin/env bash

set -euo pipefail
CURRENT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
TEST_DIR=$(dirname "$CURRENT_DIR")
PROJECT_DIR=$(dirname "$TEST_DIR")

usage() {
  echo "$0 [PYTEST_PROFILE]"
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

VENV="${CURRENT_DIR}/venv"
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -r "${PROJECT_DIR}/requirements.txt"
pip install -r "${CURRENT_DIR}/requirements.txt"
PYTEST_PROFILE="$1" pytest -s -o log_cli=true --log-cli-level=DEBUG --noconftest
