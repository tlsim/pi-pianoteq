# Pi-Pianoteq

Pi-Pianoteq is a Python/MIDI remote control for Pianoteq on Raspberry Pi.

## About

Pi-Pianoteq provides a simplified hardware interface for controlling Pianoteq on a Raspberry Pi 4B using the [Pimoroni GFX HAT](https://github.com/pimoroni/gfx-hat) - a HAT with 128x64 LCD display, 6 touch buttons and RGB backlight. After configuration, you can run Pianoteq without needing a monitor, using the GFX HAT as your interface.

This project was built in 2019, before Pianoteq's jsonRPC API existed. Instead of using the API, it works by generating MIDI mapping files for Pianoteq and sending MIDI control change messages over a virtual rtmidi port. The scope is intentionally limited to instrument and preset selection - it's designed for the Pianoteq STAGE workflow (playing rather than deep customization).

A CLI client is also included for testing and development without the GFX HAT hardware.

## Features

- GFX HAT hardware interface (primary) and CLI client (testing/development)
- MIDI virtual port communication
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

Download the latest `.whl` file from [Releases](https://github.com/tlsim/pi-pianoteq/releases/latest) and install:
```bash
pip install pi_pianoteq-*.whl
```

Or install from source (for development):
```bash
git clone https://github.com/tlsim/pi-pianoteq.git
cd pi-pianoteq
pip install .
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full development workflow.

## Configuration

Initialize your configuration:
```bash
python -m pi_pianoteq --init-config
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
python -m pi_pianoteq --show-config
```

### Configuration Priority

Configuration is loaded with the following priority (highest to lowest):
1. Environment variables
2. User config (`~/.config/pi_pianoteq/pi_pianoteq.conf`)
3. Bundled default

User config persists across package upgrades.

## Customizing Instruments

Pi-Pianoteq uses an `instruments.json` file to define which Pianoteq instruments appear in the interface. You can customize this to match the instruments you own.

### Creating Your Custom Instruments File

Initialize a customizable instruments file in your user config:
```bash
python -m pi_pianoteq --init-instruments
```

This creates `~/.config/pi_pianoteq/instruments.json` as a starting template containing all bundled instruments.

### Instruments File Priority

Like config files, instruments are loaded with priority:
1. User instruments (`~/.config/pi_pianoteq/instruments.json`) - if exists
2. Bundled default - fallback

### File Format

The `instruments.json` file is a JSON array of instrument objects:

```json
[
  {
    "name": "Grand C. Bechstein DG",
    "preset_prefix": "C. Bechstein DG",
    "background_primary": "#040404",
    "background_secondary": "#2e3234"
  },
  {
    "name": "Vintage Tines MKI",
    "preset_prefix": "MKI",
    "background_primary": "#af2523",
    "background_secondary": "#1b1b1b"
  }
]
```

**Required Fields:**
- `name`: Display name shown in the interface
- `preset_prefix`: String that must appear at the **start** of Pianoteq preset names to match this instrument

**Optional Fields:**
- `background_primary`: Hex color (`#RRGGBB`) for main backlight buttons (defaults to `#000000`)
- `background_secondary`: Hex color (`#RRGGBB`) for edge backlight buttons (defaults to `#333333`)

### How Preset Matching Works

Presets are matched to instruments using **case-sensitive prefix matching** at position 0:

- ✅ Preset "C. Bechstein DG Prelude" matches prefix "C. Bechstein DG"
- ✅ Preset "MKI Classic" matches prefix "MKI"
- ❌ Preset "My C. Bechstein DG" does NOT match "C. Bechstein DG" (prefix not at start)
- ❌ Preset "c. bechstein dg" does NOT match "C. Bechstein DG" (case-sensitive)

**⚠️ Critical: Order Matters!**

The **first** matching instrument in the array wins. If you have overlapping prefixes, list more specific ones first:

```json
[
  {"name": "C. Bechstein DG", "preset_prefix": "C. Bechstein DG"},  // More specific - list first
  {"name": "C. Bechstein 1899", "preset_prefix": "C. Bechstein"}    // Less specific - list second
]
```

If reversed, "C. Bechstein DG" presets would incorrectly match "C. Bechstein" first.

### What Happens to Unmatched Presets?

Presets that don't match any `preset_prefix` are **silently excluded** from the interface. Only instruments with at least one matched preset appear in the selector.

This means you can:
- Remove instruments you don't own (they won't appear if no presets match)
- Add instruments you do own (they'll appear when presets match)
- Organize instruments in your preferred order

### Common Customization Examples

**Only include instruments you own:**
```json
[
  {"name": "Grand K2", "preset_prefix": "K2", "background_primary": "#040404", "background_secondary": "#2e3234"},
  {"name": "Vintage Tines MKI", "preset_prefix": "MKI", "background_primary": "#af2523", "background_secondary": "#1b1b1b"}
]
```

**Reorder by preference (e.g., most-used first):**
```json
[
  {"name": "Vintage Tines MKI", "preset_prefix": "MKI", ...},
  {"name": "Grand K2", "preset_prefix": "K2", ...},
  {"name": "Celesta", "preset_prefix": "Celesta", ...}
]
```

**Custom colors without full customization:**
```json
[
  {
    "name": "Grand K2",
    "preset_prefix": "K2"
    // Colors optional - will use defaults (#000000 and #333333)
  }
]
```

### Troubleshooting

**My presets aren't appearing:**
1. Check that `preset_prefix` exactly matches the start of your preset names (case-sensitive)
2. Check for overlapping prefixes - more specific ones must come first
3. Check for typos in the JSON syntax

**Colors aren't working:**
1. Ensure colors are in `#RRGGBB` format (e.g., `#af2523`, not `af2523` or `#af25`)
2. If invalid, defaults will be used and a warning logged

**My custom file isn't loading:**
- Verify it exists at `~/.config/pi_pianoteq/instruments.json`
- Check JSON syntax with a validator
- If the file has errors, pi_pianoteq will fall back to the bundled default and log warnings

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

See [SYSTEMD.md](SYSTEMD.md) for instructions on setting up a systemd service.

## Development

For developers who want to build and deploy to a remote Pi, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Documentation

- [SYSTEMD.md](SYSTEMD.md) - Running as a systemd service
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development and deployment workflow
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
