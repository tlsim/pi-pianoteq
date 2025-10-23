# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-10-23

### Added
- Multi-source configuration system with priority: environment variables > user config > bundled default
- User configuration directory at `~/.config/pi_pianoteq/pi_pianoteq.conf`
- `--show-config` command to display active configuration and sources for debugging
- `--init-config` command to initialize user configuration file
- Comprehensive test suite with pytest (20 unit tests for configuration system)
- Configuration source tracking for debugging

### Changed
- Configuration is now loaded from `~/.config/pi_pianoteq/` when available
- User configuration persists across package upgrades
- `PIANOTEQ_HEADLESS` default changed to `true` for reliable boot without X11/VNC
- Command-line argument handling moved to argparse
- Hardware dependencies (rtmidi, gfxhat) are now imported only when needed (allows `--show-config` on dev machines)

### Fixed
- Service now starts reliably at boot in headless mode without requiring VNC/X11
- No more zombie Pianoteq processes from failed GUI initialization

## [1.1.0] - 2025-10-21

### Added
- Modern build system using pyproject.toml (PEP 517/518/621)
- Virtual environment deployment for proper Python isolation
- Deployment configuration via deploy.conf

### Changed
- Requires Python 3.13+ (previously 2.7/3.5+)
- Updated python-rtmidi to ~1.5.8 (from 1.4.0)
- Updated Pillow to ~11.1 (from ~7.1)
- Updated prompt-toolkit to ~3.0.52 (from 3.0.5)
- Build command changed from `python3 setup.py sdist` to `python3 -m build`
- Deployment now uses wheel files (.whl) instead of source distributions
- Deployment script creates and manages virtual environment

### Fixed
- Pillow 11 compatibility (replaced deprecated getsize() with getbbox())

### Removed
- setup.py (replaced by pyproject.toml)

## [1.0.0] - 2020-04-11

### Added
- Initial release
- MIDI control for Pianoteq via python-rtmidi
- GFX HAT interface for instrument/preset selection
- CLI interface using prompt-toolkit
- Systemd service for headless operation
- MIDI mapping generation
- Instrument and preset management
- Configuration file support
