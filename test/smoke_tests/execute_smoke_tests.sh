#!/usr/bin/env bash

LOCAL="local"
VENV=venv
PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")")")
SCRIPT_NAME=$(echo "$0" | sed 's#^\.\/##')

bold() {
  # ansi escape codes for bold and then normal
  printf "\033[1m%s\033[0m\n" "$1"
}

usage() {
  bold "NAME"
  echo "    ${SCRIPT_NAME}"
  bold "SYNOPSIS"
  echo "    ${SCRIPT_NAME} [--${LOCAL}]"
  bold "DESCRIPTION"
  echo "    Execute the smoke tests in this directory using the latest installable"
  echo "    wheel from TestPyPI. The test simply consists of taking a picture using"
  echo "    the PiCamera API."
  echo ""
  echo "    The following options are available:"
  echo ""
  echo "        --${LOCAL} Use a local wheel instead of the one from TestPyPI."
}

# parse CLI arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    "--${LOCAL}") USE_LOCAL_WHEEL=true;;
    "-h") usage; exit 0;;
    *) usage; exit 1;;
  esac
  shift
done

cleanup() {
  unset ASTRO_PI_EXECUTOR_REPLAY_SEQUENCE
  unset PYTEST_PROFILE
  unset USE_LOCAL_WHEEL
}

trap 'cleanup' EXIT

python3 -m venv "$VENV"
source "$VENV/bin/activate"
if [ -n "$USE_LOCAL_WHEEL" ]; then
  echo "Installing local wheel"
  tempdir=$(mktemp -d)
  pip install build
  python -m build --outdir "${tempdir}" "${PROJECT_ROOT}"
  wheels=$(find "${tempdir}" -name "*.whl")
  if [ "$(echo "$wheels" | wc -l)" -ne 1 ]; then
    echo "There was a problem building the wheel"
    exit 1
  fi
  SMOKE_TEST_LOCAL_WHEEL=$(echo "$wheels" | head -n 1)
else
  pip install -r requirements.txt
fi
export ASTRO_PI_EXECUTOR_REPLAY_SEQUENCE='VIS/test_data'
export PYTEST_PROFILE=SMOKE_TESTS
if [ -n "$SMOKE_TEST_LOCAL_WHEEL" ]; then
  export SMOKE_TEST_LOCAL_WHEEL
fi
pytest -o log_cli=true --log-cli-level=DEBUG --noconftest
