@echo off

rem GLOBALS
set LOCAL="local"
set VENV_NAME=venv
set TRUE=true
for %%I in ("%~dp0\..") do set PROJECT_ROOT=%%~dpI
for %%I in (%0) do set SCRIPT_NAME=%%~nxI

goto :main

rem HELPER FUNCTIONS
:findActivationScript
  setlocal enabledelayedexpansion
  for %%I in ("%VENV_NAME%\Scripts\*.bat") do (
    if "%%~nI"=="Activate" (
      set activation_script=%VENV_NAME%\Scripts\Activate.bat
    ) else if "%%~nI"=="activate" (
      set activation_script=%VENV_NAME%\Scripts\activate.bat
    )
  )
  endlocal & set ACTIVATION_SCRIPT="%activation_script%"
exit /b

:bold
  setlocal enabledelayedexpansion
  echo [1m %~1 [0m
  endlocal
exit /b

:usage
  call :bold "NAME"
  echo     %SCRIPT_NAME%
  call :bold "SYNOPSIS"
  echo     %SCRIPT_NAME% [--%LOCAL% ^| -h]
  call :bold "DESCRIPTION"
  echo     Execute the smoke tests in this directory using the latest installable
  echo     wheel from TestPyPI. The test simply consists of taking a picture using
  echo     the PiCamera API.
  echo.
  echo     The following options are available:
  echo.
  echo         --%LOCAL% Use a local wheel instead of the one from TestPyPI.
exit /b

:parse_args
  setlocal enabledelayedexpansion
  if "%1"=="" (
    exit /b
  ) else if "%1"=="--local" (
    set USE_LOCAL_WHEEL="%TRUE%"
  ) else if "%1"=="-h" (
    call :usage
    exit /b
  ) else (
    call :usage
    exit /b 1
  )
  endlocal & set "USE_LOCAL_WHEEL=%USE_LOCAL_WHEEL%"
exit /b

:mktempd
  setlocal enabledelayedexpansion
  set "temp_template=%TEMP%\TempDir_"
  set "tempdir=!temp_template!!random!"
  if exist "!tempdir!" goto mktempd
  mkdir "!tempdir!"
  endlocal & set "tempdir=%tempdir%"
exit /b

rem MAIN SCRIPT START ####
:main

rem Parse the first arg
call :parse_args %1

rem Create the virtual environment
python -m venv %VENV_NAME%

rem Activate the virtual environment
call :findActivationScript
call %ACTIVATION_SCRIPT%

if "%USE_LOCAL_WHEEL%"=="%TRUE%" (
  echo Installing local wheel
  call :mktempd
  pip install build
  python -m build --outdir "%tempdir%" "%PROJECT_ROOT%"
  set wheel_count=0
  for %%F in ("%tempdir%\*.whl") do (
    set \a wheel_count+=1
    set wheel=%%F
  )
  if not %wheel_count% equ 1 (
    echo There was a problem building the wheel
    exit /b 1
  )
  set SMOKE_TEST_LOCAL_WHEEL=%wheel%
) else (
  rem Install dependencies
  pip install -r requirements.txt
)

rem Provide user instructions
echo Virtual environment "%VENV_NAME%" has been created and activated.
echo Use "deactivate" to exit the virtual environment.

rem Execute the smoke tests
set ASTRO_PI_EXECUTOR_REPLAY_SEQUENCE="VIS/test_data"
set PYTEST_PROFILE=SMOKE_TESTS
pytest -o log_cli=true --log-cli-level=DEBUG --noconftest
set PYTEST_ERROR=%ERRORLEVEL%
echo %PYTEST_ERROR%
rem Unset environment variables
set ASTRO_PI_EXECUTOR_REPLAY_SEQUENCE=
set PYTEST_PROFILE=
set SMOKE_TEST_LOCAL_WHEEL=
if %PYTEST_ERROR% GEQ 1 EXIT /B %PYTEST_ERROR%
