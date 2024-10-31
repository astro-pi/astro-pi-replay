# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Removed

### Fixed

## [1.0.1] - 2024-09-12

### Fixed

- Assets were missing the `datetime_original` tags.
- Immutable arrays were being passed to opencv instead of mutable ones.

## [1.0.0] - 2024-09-12

### Added

- This CHANGELOG.md file

### Changed

- The default image sequence is now from team `kkkm`, chosen by Richard Hayler.
- TLE files are now stored in assets so that `orbit` gives a more accurate estimate of the location of the ISS.

[unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/astro-pi/Astro-Pi-Replay/releases/tag/v1.0.0
