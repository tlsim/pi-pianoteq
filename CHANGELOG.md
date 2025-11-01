# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - Unreleased

### Breaking Changes

**Migration required for existing installations.** See TESTING.md for migration guide.

- Package distribution name changed from `pi_pianoteq` to `pi-pianoteq` for consistency with project name
- Systemd service name changed from `pi_pianoteq.service` to `pi-pianoteq.service`
- Virtual environment path in deploy.sh changed from `~/pi_pianoteq_venv` to `~/pi-pianoteq-venv`
- Installation method simplified to `pip install --user` for normal users

### Added

- Console script entry point: users can now run `pi-pianoteq` command directly
- Src-layout directory structure (`src/pi_pianoteq/`) for cleaner project organization
- Dual-install pattern documentation for developers (venv + user install coexistence)
- TESTING.md guide for migration and testing new structure

### Changed

- Adopted application-oriented packaging (console script vs library imports)
- Systemd service uses `~/.local/bin/pi-pianoteq` for user installations
- deploy.sh generates service file dynamically instead of using template
- Simplified installation documentation: single command for users, separate workflow for developers
- Systemd setup now clearly marked as optional (not required for normal use)

### Migration Notes

Existing users must:
1. Stop and remove old systemd service (`pi_pianoteq.service`)
2. Remove old installation (venv or pip uninstall)
3. Follow updated installation instructions in README.md
4. Recreate systemd service with new name if needed

See TESTING.md for detailed migration steps.

## [1.6.0] - 2025-10-26

### Added
- Automatic instrument discovery via Pianoteq JSON-RPC API (replaces manual instruments.json configuration)
- Structured logging system with timestamps, module names, and log levels
- `--include-demo` CLI flag to include demo instruments with limited functionality
- Smart retry logic with stable count detection for instrument loading
- Configurable log level via `PI_PIANOTEQ_LOG_LEVEL` environment variable

### Changed
- Pianoteq now starts with `--serve` flag to enable JSON-RPC API
- Instruments and presets automatically discovered from running Pianoteq instance
- Only licensed instruments shown by default (demo instruments filtered out)
- INFO/DEBUG logs sent to stdout, WARNING/ERROR logs sent to stderr
- Simplified command-line options documentation in README

### Removed
- Manual `instruments.json` configuration file (automatic discovery replaces it)
- `--init-instruments` and `--show-instruments` CLI commands (no longer needed)

## [1.5.1] - 2025-10-25

### Added
- MIT License and disclaimer
- GitHub Actions workflows for CI/CD
- GitHub issues tracking future enhancements

### Changed
- Updated README with project background and improved documentation
- Installation now uses releases instead of building from source
- Archived old research files to separate branch

## [1.5.0] - 2025-10-25

### Added
- Full-featured instrument selection menu in CLI client (feature parity with GFX HAT)
- Arrow key navigation (Up/Down for presets, Left/Right for instruments)
- Emacs-style keybindings (Ctrl-P/N for presets, Ctrl-F/B for instruments, Ctrl-I for menu)
- Two-mode CLI interface: Normal mode and Menu mode with scrollable instrument list

### Changed
- CLI client now uses prompt_toolkit Frame widget and formatted text tuples
- Simplified on-screen help to show arrow keys (Emacs bindings still supported)

### Removed
- "Hello world" placeholder text from CLI client

## [1.4.1] - 2025-10-25

### Fixed
- Race condition in MIDI port detection by adding 2-second delay for Pianoteq to detect virtual port
- Python output not appearing in systemd/journalctl logs by adding `-u` flag for unbuffered mode
- Warning message instructions now clarify that pi_pianoteq must be running when enabling MIDI port

### Changed
- Updated systemd service documentation to include `-u` flag for unbuffered Python output
- Improved MIDI configuration warning message clarity

## [1.4.0] - 2025-10-24

### Added
- `--cli` flag to run CLI client without GFX HAT hardware (for development/testing)
- MIDI configuration validation and startup warning when PI-PTQ device not enabled
- `pi_pianoteq.util.pianoteq_prefs` module for reading Pianoteq preferences
- Documentation for MIDI configuration in README.md and DEVELOPMENT.md
- CLI client controls documented in README.md

### Changed
- CLI client warning waits for keypress acknowledgment (non-blocking in headless mode)
- Improved warning messages to accurately describe impact of missing MIDI configuration
- Updated MIDI configuration instructions to match Pianoteq 9 UI (Edit → Preferences → Devices)

## [1.3.0] - 2025-10-24

### Added
- Scrolling text support for GFX HAT display (marquee-style for long text)
- `Preset.get_display_name()` method to strip instrument prefix from preset names
- Tests for preset display name formatting

### Changed
- Improved display clarity by removing redundant instrument prefix from preset names
- Enhanced scrolling text with better threading, configurable delays and wrap gaps
- Improved code documentation for scrolling text components

## [1.2.0] - 2025-10-23

### Added
- Multi-source configuration: environment variables > user config > bundled default
- User configuration at `~/.config/pi_pianoteq/pi_pianoteq.conf` (persists across upgrades)
- `--show-config` command to display active configuration and sources
- `--init-config` command to initialize user configuration
- pytest test suite with 20 unit tests

### Changed
- `PIANOTEQ_HEADLESS` default now `true`
- Hardware dependencies imported lazily (enables `--show-config` on dev machines)

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
