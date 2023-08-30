@echo off

rem Set the desired virtual environment name
set VENV_NAME=venv

rem Create the virtual environment
python -m venv %VENV_NAME%

rem Activate the virtual environment
call %VENV_NAME%\Scripts\activate

rem Install dependencies
pip install -r requirements.txt

rem Provide user instructions
echo Virtual environment "%VENV_NAME%" has been created and activated.
echo Use "deactivate" to exit the virtual environment.

rem Execute the smoke tests
set ASTRO_PI_EXECUTOR_REPLAY_DIR=replay_tests
set PYTEST_PROFILE=SMOKE_TESTS
pytest -o log_cli=true --log-cli-level=DEBUG --noconftest
set ASTRO_PI_EXECUTOR_REPLAY_DIR=
set PYTEST_PROFILE=
