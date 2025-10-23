# Pi-Pianoteq

Pi-Pianoteq is a Python/Midi remote control for Pianoteq

# System Dependencies (Raspberry Pi)

On the Raspberry Pi, install python3-rtmidi via apt:
```bash
sudo apt install python3-rtmidi
```

This avoids compiling from source (which requires ALSA development headers). The deployment script will automatically install other dependencies (gfxhat, prompt-toolkit, etc.) into the virtual environment.

# Usage

First, check and update the configuration in `pi_pianoteq/pi_pianoteq.conf`

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

