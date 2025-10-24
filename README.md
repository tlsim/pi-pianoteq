# Pi-Pianoteq

Pi-Pianoteq is a Python/MIDI remote control for Pianoteq on Raspberry Pi.

## Features

- Control Pianoteq via MIDI virtual port
- [GFX HAT](https://github.com/pimoroni/gfx-hat) interface for instrument/preset selection
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

Note: `linux-cpupower` is required if using the systemd service (for CPU performance management).

### 3. Install pi_pianoteq

Clone and install from source:
```bash
git clone https://github.com/tlsim/pi-pianoteq.git
cd pi-pianoteq
pip install .
```

Or using pipenv (recommended for development):
```bash
pipenv install
```

## Configuration

Initialize your configuration:
```bash
python -m pi_pianoteq --init-config
```

Edit the config file:
```bash
nano ~/.config/pi_pianoteq/pi_pianoteq.conf
```

Update the paths to match your Pianoteq installation:

```ini
[Pianoteq]
PIANOTEQ_DIR = ~/pianoteq/Pianoteq 8 STAGE/arm-64bit/
PIANOTEQ_BIN = Pianoteq 8 STAGE
PIANOTEQ_PREFS_FILE = ~/.config/Modartt/Pianoteq84 STAGE.prefs
PIANOTEQ_HEADLESS = true
```

View your active configuration:
```bash
python -m pi_pianoteq --show-config
```

### Configuration Priority

Configuration is loaded with the following priority (highest to lowest):
1. Environment variables
2. User config (`~/.config/pi_pianoteq/pi_pianoteq.conf`)
3. Bundled default

User config persists across package upgrades.

## MIDI Configuration

After installing pi_pianoteq, you need to enable the PI-PTQ MIDI port in Pianoteq:

1. Launch Pianoteq
2. Go to **Edit → Preferences → Devices**
3. Under "Active MIDI Inputs", check the box next to **PI-PTQ**
4. Click OK

This is a one-time setup. The setting persists in your Pianoteq preferences.

**Note:** pi_pianoteq will warn you on startup if this is not configured, but will continue running.

## Running

### Run Manually

```bash
python -m pi_pianoteq
```

Or with pipenv:
```bash
pipenv run python -m pi_pianoteq
```

### Run with CLI Client (for testing/development)

For usage without GFX HAT hardware, use the CLI client:

```bash
python -m pi_pianoteq --cli
```

Controls:
- `Ctrl-K`: Show current preset
- `Ctrl-N`: Next preset
- `Ctrl-P`: Previous preset
- `Ctrl-C`: Exit

### Run as a Service (Auto-start on Boot)

See [SYSTEMD.md](SYSTEMD.md) for instructions on setting up a systemd service.

## Development

For developers who want to build and deploy to a remote Pi, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Documentation

- [SYSTEMD.md](SYSTEMD.md) - Running as a systemd service
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development and deployment workflow
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Requirements

- Python 3.13+
- Pianoteq (any version)
- Raspberry Pi (tested on Pi 4B) with:
  - python3-rtmidi (system package)
  - [Pimoroni GFX HAT](https://github.com/pimoroni/gfx-hat) (optional, for hardware interface)

## License

MIT
