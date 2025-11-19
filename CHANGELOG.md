# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Parameter randomization with two access methods
  - GFX HAT: "Randomise" option in preset menu (long-press ENTER)
    - Switches to the instrument if viewing different instrument's presets, then randomizes
    - Shows "(modified)" suffix after randomization
  - GFX HAT: "Randomise" option in control menu (press ENTER on main display)
    - Randomly selects instrument and preset, then randomizes parameters
  - CLI: Direct keyboard shortcuts for randomization
    - Press 'r' to randomize current preset parameters
    - Press 'R' (Shift+r) to randomly select instrument, preset, and randomize parameters
- CLI logs view (press 'l' to view startup and runtime logs, press Esc or 'q' to return)
- Control menu on GFX HAT: new top-level menu accessed via middle button press
  - Instrument selection moved to first menu item
  - Provides framework for additional control functions in future releases
- Key repeat for all navigation and action buttons on GFX HAT with intelligent held event threshold
  - Hold down arrow buttons for continuous scrolling through instruments, presets, and menus
  - Long press ENTER button to open preset menu (with threshold to prevent accidental triggers)
  - Intelligent threshold distinguishes between short press and hold
    - Short press: immediate single-step navigation or menu action
    - Hold: continuous scrolling/long-press action starts after brief delay (2 held events)
    - Prevents accidental over-navigation or unintended long-press activation

### Changed
- GFX HAT shutdown option moved from instrument selection menu to control menu for easier access

## [2.2.0] - 2025-11-15

### Changed
- Preset selection now uses JSON-RPC `loadPreset()` instead of MIDI Program Change messages
- Faster startup time: ~5 seconds from launch to ready (eliminated MIDI initialization delay)

### Removed
- Obsolete MIDI output configuration options (MIDI input capabilities preserved for future features)

## [2.1.0] - 2025-11-15

### Added
- CLI client improvements
  - Preset menu (press 'p' to open)
    - Access from main display to browse current instrument's presets
    - Access from instrument menu to browse any instrument's presets before switching
    - Current preset automatically highlighted when viewing current instrument
  - Search functionality (press '/' to search)
    - Search instruments from instrument menu
    - Search presets from preset menu
    - Combined search from main display (searches both instruments and presets)
    - Real-time filtering as you type
    - Case-insensitive substring matching
  - Dynamic menu sizing: menus adapt to terminal height automatically
  - Log line truncation during loading to prevent horizontal overflow
- GFX HAT improvements
  - Preset selection menu (long press ENTER to open)
    - Access from main display to browse current instrument's presets
    - Access from instrument menu to browse any instrument's presets before switching
    - Current preset automatically highlighted when viewing current instrument
    - Menu headings distinguish instrument menu ("Select Instrument:") from preset menu ("Select Preset:")
  - Button suppression window to prevent accidental menu activation when navigating with arrow buttons
- Comprehensive test suite covering all client and process functionality
- Startup preset sync: matches Pianoteq's current preset instead of always resetting to first

### Changed
- Preset display names now use longest common word prefix of preset names instead of instrument "instr" field
- Client API simplified to return Instrument and Preset objects instead of primitive types

### Fixed
- Pianoteq now exits cleanly on service restart using JSON-RPC quit command instead of SIGTERM
- Preset display names for hyphenated instrument names (e.g., "SK-EX") now calculate correctly

## [2.0.0] - 2025-11-06

### Breaking Changes

- Package name: `pi_pianoteq` → `pi-pianoteq`
- Service name: `pi_pianoteq.service` → `pi-pianoteq.service`
- Venv path: `~/pi_pianoteq_venv` → `~/pi-pianoteq-venv`

### Added

- Console script: `pi-pianoteq` command replaces `python -m pi_pianoteq`
- Src-layout directory structure

### Changed

- Systemd service uses console script from venv
- User installation via `pip install --user`

## [1.8.0] - 2025-11-04

### Changed
- Renamed all Python modules to snake_case for PEP 8 consistency
- Reorganized internal structure with dedicated subdirectories (config/, logging/, rpc/)
- Updated test filenames to follow pytest conventions (test_*.py)

## [1.7.0] - 2025-10-30

### Added
- Loading screen with visual feedback during startup (#13)
  - GFX HAT: Blue backlight with loading messages
  - CLI: Full-screen interface with live log window
  - Messages: "Starting...", "Loading..."
- License detection using `getActivationInfo()` API endpoint
- CLI log window showing real-time startup messages

### Fixed
- Licensed versions no longer incorrectly fall back to demo instruments

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
