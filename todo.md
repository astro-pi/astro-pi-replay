Current
--------
- AstroPiExecutor.setup_venv should check the venv python version (it will break
if a different version of python is used later on) - FIX
- Add upgrader that deletes any invalid replay dirs
- Fix resources being versioned in AWS - currently breaks CI when package version changes.
  -> temporarily copy to aws ?
  - This may entail having to put my token in the CI - bad idea?

    VERSION THE RESOURCES THEMSELVES?

- fix ffmpeg tests on Windows
  FAILED test/test_picamera_api.py::test_replay_start_recording_supports_all_video_formats[bgr] - AssertionError: assert False
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[mjpeg] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[yuv] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[rgb] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[rgba] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[bgr] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_start_recording_into_stream[bgra] - assert 0 > 0
  FAILED test/test_picamera_api.py::test_replay_records_to_a_circular_stream - AssertionError: assert 0 == 2764800

Bonuses:
- Add picamera2 support
- Add option to make Thonny aware of picamera/sense_hat/orbit stubs (aka install into the environment rather than a separate venv)
- test what happens if a different versoin of Python is used than the astro_pi_replay venv.
- Install all the Astro Pi deps into the replay tool to avoid a difficult install procedure.
- check stdout is not being polluted
- remote attach to the executor subprocess
  python3 -m debugpy --listen 1.2.3.4:5678 --wait-for-client -m main
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
- add photo interpolation or schedule another run...
- implement encoders so to reduce the number of deviations from the original i.e. keep more original implementation
- fix the name == main hack used for the picamera preview
- misc refactoring (check for TODOs and FIXMes).
    - look for opportunities to improve mocking with `wraps`=
- Replace ffmpeg subproc with either ffmpeg-python or pyav
- PIR sensor?
- move de421.bsp and tle files out of the github and into the resources download
- add more photos to help children
- Complete the documentation and request translations
- integration tests (qemu + docker based)
- PR hook - version number checker.
- CLI completion
