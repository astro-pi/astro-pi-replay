![Build and test workflow](https://github.com/astro-pi/astro_pi_executor/actions/workflows/build_and_test_scheduler.yml/badge.svg?branch=main)
![Build and test workflow](https://github.com/astro-pi/astro_pi_executor/actions/workflows/build_and_test_worker.yml/badge.svg?branch=main)

# Astro Pi Executor

A CLI to execute Mission Space Lab experiments for 2023-2024.

All function calls from the `picamera`, `picamera2`, `sense_hat`, `skyfield`, and `orbit` libraries
will be mocked to return data from an historic run from the ISS, rather than from attached hardware.
This allows teams to test their code with representative data and provide a confidence boost that
their code will work

## Usage

Change to your project directory (`cd my-project`), install the `astro_pi_executor`, and download the assets using `astro_pi_executor download`. Then execute your program with `astro_pi_executor run main.py`.

This will prepare a sequence of near-infrared images (NIR) images, together with the corresponding
data collected from the Sense Hat, to be returned by all calls to `picamera`, `sense_hat`, etc.
The CLI allows for some configuration of this behaviour - see the [Documentation](#documentation) for more details.

## Documentation

See the [docs](../docs) page.


