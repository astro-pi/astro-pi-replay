Current:
--------
- Fix resources being versioned in AWS - currently breaks CI when package version changes.
  -> temporarily copy to aws ?
  - This may entail having to put my token in the CI - bad idea?

- Add picamera2 support

Bonuses:
- check stdout is not being polluted
- profile mode to profile the main.py being executed
- remote attach to the executor subprocess
  python3 -m debugpy --listen 1.2.3.4:5678 --wait-for-client -m main
- profile tests to identify easy winnings
  - could offer a test download to avoid having to download 800MB each time in CI.
- Refactor the stubbing of no_wait to make the tests cleaner and more isolated.
- Fix the picamera previewer
- copy over picamera exc
- Bayer support for picamera
- frames support (pyav, but it always segfaults for me...)
- Annotation over video for picamera
- add proper process job control to the executor to ensure
all processes are killed when the interpreter is killed (using module atexit) or a finally clause
  - this includes the picamera previewer process and the sense hat displayer process
- refactor picamera implementation (move around the state and ensure
resources are closed properly)
- add interpolation for sense hat
- add photo interpolation or schedule another run...
- implement encoders so to reduce the number of deviations from the original i.e. keep more original implementation
- fix the name == main hack used for the picamera preview
- misc refactoring (check for TODOs and FIXMes).
- Replace ffmpeg subproc with either ffmpeg-python or pyav
- PIR sensor?
- move de421.bsp and tle files out of the github and into the resources download
- add more photos to help children

Admin & Best-practices:
- add repo to RPF foundation in TestPypi
- integration tests (qemu + docker based)
- Ensure CD builds wheels for many OS and arch types.
- Complete the documentation and request translations
- Add dependabot
- Test on RP4 and Windows machine
- Thonny support
- Licence

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
