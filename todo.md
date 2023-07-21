Current:
--------
- Finish basic PiCamera API
  - start/stop/split recording
  - etc.
- Finish sense hat API coverage
  - I think it's just the raw methods left now?
- Orbit support
  - Ensure from orbit import ISS gets the correct TLE file.
- Add wait mode to the library to ensure photo timestamps will match roughly
the timestamps of the original).
- Test velocity calculations using the library using the basic project
- Add picamera2 support
- skyfield support?

Bonuses:
- Annotation over video
- add proper process job control to the executor to ensure
all processes are killed when the interpreter is killed (using module atexit)
- add interpolation for sense hat
- add photo interpolation or schedule another run...
- fix the name == main hack used for the picamera preview
- misc refactoring (check for TODOs and FIXMes).

Admin & Best-practices:
- add repo to RPF foundation in TestPypi
- complete smoke tests
- integration tests (qemu + docker based)
- Ensure CD builds wheels for many OS and arch types.
- Complete the documentation and request translations
- Add dependabot

Now:
-----

- Create CI for PRs to `main` branch that
 - runs tests and build
 - passing tests required to merge
- Create CI for `main` that run same build and test, any system or integration tests,
and then promotes to the `test` env.

- Smoke tests: download package from PyPi and check that functions are callable

Medium-term:
------------

Later:
------
- PR hook - version number checker.
replace "Mission Space Lab" with the new name.
replace astro_pi_executor and Astro Pi Executor with the new name
