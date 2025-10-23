# Pi-Pianoteq

Pi-Pianoteq is a Python/Midi remote control for Pianoteq

# Setup on Raspberry Pi

## 1. Install Pianoteq

Install Pianoteq on the Raspberry Pi (arm-64bit version):
- Download from [Modartt](https://www.modartt.com/pianoteq)
- Extract to a location like `~/pianoteq/Pianoteq 8 STAGE/arm-64bit/`
- Note the installation path for configuration

## 2. System Dependencies

Install python3-rtmidi via apt:
```bash
sudo apt install python3-rtmidi
```

This avoids compiling from source (which requires ALSA development headers). The deployment script will automatically install other dependencies (gfxhat, prompt-toolkit, etc.) into the virtual environment.

## 3. Configure pi_pianoteq

Edit `pi_pianoteq/pi_pianoteq.conf` to match your Pianoteq installation:

```ini
[Pianoteq]
PIANOTEQ_DIR = ~/pianoteq/Pianoteq 8 STAGE/arm-64bit/
PIANOTEQ_BIN = Pianoteq 8 STAGE
PIANOTEQ_PREFS_FILE = ~/.config/Modartt/Pianoteq84 STAGE.prefs
```

Update these paths to match:
- `PIANOTEQ_DIR`: Directory containing the Pianoteq binary
- `PIANOTEQ_BIN`: Name of the Pianoteq executable
- `PIANOTEQ_PREFS_FILE`: Pianoteq preferences file (version-specific)

# Usage

## Using pipenv (recommended)

Install dependencies
```bash
pipenv install
```

Build and deploy in one command
```bash
pipenv run build-and-deploy
```

Or run separately:
```bash
pipenv run package  # Build the package using pyproject.toml
pipenv run deploy   # Deploy to remote Raspberry Pi
```

## Direct commands

Build the package (using modern pyproject.toml)
```bash
python3 -m build
```

Deploy to remote Raspberry Pi
```bash
./deploy.sh
```

Or build and deploy
```bash
python3 -m build && ./deploy.sh
```

**Note:** Building requires the `build` package:
```bash
pip3 install --user build
```

## Deployment Details

Deployment uses a virtual environment for proper isolation:
- Creates `~/pi_pianoteq_venv` with access to system packages (`--system-site-packages`)
- Installs `pi_pianoteq` and dependencies into the venv
- Systemd service uses the venv Python

PEP 668 compliant and follows Python best practices.

