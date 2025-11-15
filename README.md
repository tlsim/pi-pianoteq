# Pi-Pianoteq

Pi-Pianoteq is a Python remote control for Pianoteq on Raspberry Pi.

## About

Pi-Pianoteq provides a simplified hardware interface for controlling Pianoteq on a Raspberry Pi 4B using the [Pimoroni GFX HAT](https://github.com/pimoroni/gfx-hat) - a HAT with 128x64 LCD display, 6 touch buttons and RGB backlight. After configuration, you can run Pianoteq without needing a monitor, using the GFX HAT as your interface.

This project started in 2019 using MIDI Program Change messages for preset selection (before Pianoteq's JSON-RPC API existed). As of v2.2.0, it uses Pianoteq's JSON-RPC API for direct preset control. The scope is intentionally limited to instrument and preset selection - it's designed for the Pianoteq STAGE workflow (playing rather than deep customization).

A CLI client is also included for testing and development without the GFX HAT hardware.

## Features

- GFX HAT hardware interface (primary) and CLI client (testing/development)
- JSON-RPC API communication with Pianoteq
- Flexible configuration system
- Headless operation support
- Systemd service for auto-start on boot

## Installation

### 1. Install Pianoteq

Download and install Pianoteq on your Raspberry Pi:
- Download from [Modartt](https://www.modartt.com/pianoteq)
- Extract to a location like `~/pianoteq/Pianoteq 8 STAGE/`

### 2. Install System Dependencies

```bash
sudo apt install python3-rtmidi python3-pip python3-venv linux-cpupower
```

Notes:
- `python3-rtmidi`: Required to avoid compiling rtmidi from source
- `linux-cpupower`: Required if using the systemd service (for CPU performance management)

### 3. Install pi-pianoteq

Download the latest `.whl` file from [Releases](https://github.com/tlsim/pi-pianoteq/releases/latest) and install:
```bash
pip install --user pi-pianoteq-*.whl
```

The `pi-pianoteq` command will be installed to `~/.local/bin/pi-pianoteq`.

**For developers:** See [docs/development.md](docs/development.md) for the development workflow.

## Configuration

Initialize your configuration:
```bash
pi-pianoteq --init-config
```

Edit `~/.config/pi_pianoteq/pi_pianoteq.conf` and update the paths to match your Pianoteq installation:

```ini
[Pianoteq]
PIANOTEQ_DIR = ~/pianoteq/Pianoteq 8 STAGE/arm-64bit/
PIANOTEQ_BIN = Pianoteq 8 STAGE
PIANOTEQ_PREFS_FILE = ~/.config/Modartt/Pianoteq84 STAGE.prefs
PIANOTEQ_HEADLESS = true
```

View your active configuration:
```bash
pi-pianoteq --show-config
```

### Configuration Priority

Configuration is loaded with the following priority (highest to lowest):
1. Environment variables
2. User config (`~/.config/pi_pianoteq/pi_pianoteq.conf`)
3. Bundled default

User config persists across package upgrades.

## Instruments

Instruments are automatically discovered from Pianoteq via its JSON-RPC API. Only licensed instruments are shown; demos are filtered out. Display colors are assigned automatically based on instrument type.

## Running

### Run Manually

```bash
pi-pianoteq
```

### Command Line Options

- `--cli`: Use CLI client instead of GFX HAT (for testing/development)
- `--include-demo`: Include demo instruments with limited functionality
- `--show-config`: Display current configuration and exit
- `--init-config`: Initialize user config file and exit

### Run with CLI Client (for testing/development)

For usage without GFX HAT hardware, use the CLI client:

```bash
pi-pianoteq --cli
```

The CLI client provides a full-featured terminal interface with instrument selection:

**Normal Mode Controls:**
- `↑/↓` (or `Ctrl-P/N`): Navigate presets
- `←/→` (or `Ctrl-B/F`): Quick instrument switch
- `i` (or `Ctrl-I`): Open instrument selection menu
- `q` (or `Ctrl-C`): Quit

**Instrument Menu Controls:**
- `↑/↓` (or `Ctrl-P/N`): Navigate menu
- `Enter`: Select instrument
- `Esc`, `q`, or `Ctrl-C`: Exit menu

### Run as a Service (Auto-start on Boot)

See [docs/systemd.md](docs/systemd.md) for instructions on setting up a systemd service.

## Development

For developers who want to build and deploy to a remote Pi, see [docs/development.md](docs/development.md).

## Documentation

- [docs/systemd.md](docs/systemd.md) - Running as a systemd service
- [docs/development.md](docs/development.md) - Development and deployment workflow
- [docs/pianoteq-api.md](docs/pianoteq-api.md) - Pianoteq JSON-RPC API reference
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Disclaimer

This is an independent project and is not affiliated with, endorsed by, or sponsored by Modartt (the creators of Pianoteq). Pianoteq is a registered trademark of Modartt. This software interacts with Pianoteq via standard MIDI protocols.

## Requirements

- Python 3.13+
- Pianoteq (any version, designed for STAGE)
- Raspberry Pi (tested on Pi 4B) with:
  - python3-rtmidi (system package)
  - [Pimoroni GFX HAT](https://github.com/pimoroni/gfx-hat) (for primary hardware interface; CLI available for testing without it)

## License

MIT
