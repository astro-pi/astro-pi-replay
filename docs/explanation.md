# Explanation

This page covers how the library works in detail, for any curious Astro Pi participants.

# Virtual environments
The first time you run `astro_pi_executor` it will create a virtual environment (`venv`) in your home folder (configurable, but `~/.astro_pi_executor` by default) so that its runtime trickery does not affect the rest of the system.

Inside the `venv`, some fake modules (called stubs) for `picamera`, `picamera2`, `sense_hat` are installed that conform to the same API as the real modules, but return replayed data from a previous mission from a file. Since the original modules are NOT cross-platform and `astro_pi_executor` is designed to be cross-platform, it is not possible to depend on them directly.

However, not all of the outputs of every API method is recorded - in this scenario the call will just return the default value for the type, or else a random value depending on the configuration of `astro_pi_executor`

# Modes

There are two modes - REPLAY mode and LIVE mode.
LIVE mode is only supported on Raspberry Pi OS, where `astro_pi_executor` effectively is a symlink
to the system Python executable.
REPLAY mode is cross-platform and spins up a venv that replays data.
