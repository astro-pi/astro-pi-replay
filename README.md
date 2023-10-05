![Build and test workflow](https://github.com/astro-pi/Astro-Pi-Replay/actions/workflows/build_and_test_scheduler.yml/badge.svg?branch=main)
![Build and test workflow](https://github.com/astro-pi/Astro-Pi-Replay/actions/workflows/build_and_test_worker.yml/badge.svg?branch=main)

# Astro Pi Replay

A CLI to replay historic data from previous ISS missions.

All function calls from the `picamera`, `picamera2`, `sense_hat`, `skyfield`, and `orbit` libraries
will be mocked to return data from an historic run from the ISS, rather than from attached hardware.
This allows teams to test their code with representative data and provide a confidence boost that
their code will work

## Quickstart

Change to your project directory (`cd my-project`), install `Astro-Pi-Replay` using `pip`, and then run your program with `Astro-Pi-Replay run main.py`.

For more detailed installation instructions, checkout the docs site.

This will prepare a sequence of near-infrared images (NIR) images, together with the corresponding
data collected from the Sense Hat, to be returned by all calls to `picamera`, `sense_hat`, etc.
The CLI allows for some configuration of this behaviour - see the [Documentation](#documentation) for more details.

## Documentation

See the [docs](../docs) page.


