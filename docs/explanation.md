# Explanation

This page covers how the library works in detail, for any curious Astro Pi participants.

# Virtual environments
The first time you run `Astro-Pi-Replay` it will create a virtual environment (`venv`) in your home folder (configurable, but `~/.astro_pi_replay` by default) so that its runtime trickery does not affect the rest of the system.

Inside the `venv`, some fake modules (called stubs) for `picamera`, `picamera2`, `sense_hat` are installed that conform to the same API as the real modules, but return replayed data from a previous mission from a file. Since the original modules are NOT cross-platform and `Astro-Pi-Replay` is designed to be cross-platform, it is not possible to depend on them directly.

However, not all of the outputs of every API method is recorded - in this scenario the call will just return the default value for the type, or else a random value depending on the configuration of `Astro-Pi-Replay`

# Modes

There are two modes - REPLAY mode and LIVE mode.
LIVE mode is only supported on Raspberry Pi OS, where `Astro-Pi-Replay` effectively is a symlink
to the system Python executable.
REPLAY mode is cross-platform and spins up a venv that replays data.

# Replay resources

The photo and video assets are organised into `sequences`, which are ordered collections of photos. Each sequence is downloaded into the `replay` directory in `src/astro_pi_replay/resources`. To simplify lookup of assets, there is a strict naming convention for each subdirectory of `replay`:

    replay/photography_type/img_resolution/sequence_id/

The sequence id is a unique alphanumeric string - typically the team id from which the sequence is derived. As an example, team AstroX's photos, which are visible light photos and have a resolution of (4056,304) are located at:

    replay/VIS/4056_3040/AstroX/

However, if there were multiple sequences, the next sequence would have to use a different sequence id.

In addition to the constraints above, each sequence directory itself is organised as per the following:

    sequence-id/
    ├─ data/
    │  ├─ data.csv
    ├─ metadata.json
    ├─ photos/
    │  ├─ img_0.jpg
    │  ├─ img_1.jpg
    │  ├─ ...
    ├─ videos/
    │  ├─ video0.mp4


The `data.csv` contains the SenseHat data to be replayed in tandem with the images.
The `photos` directory contains all the images for the sequence - should be zero-indexed.
The `video0.mp4` is an mp4 of the images in the `photos` directory.
The `metadata.json` file provides essential metadata for the sequence, including:

* The lens and camera used to capture the images.
* The start and end datetimes of the image sequence.
* The team whose code originally captured the images.
* The ground sampling distance (GSD) to use when doing geospatial analysis with the images.
* The filename prefix and suffixes used for `photos` and `videos`.

# TODO create a script that:
1. Downloads the original team asset from the internal google drive
2. Transforms it into the required asset (defines the numbers)(etc.)
3. Produces a zipfile in the above format, providing the supplementary data

# Precedence

Environment variables take precedence over cli arguments
