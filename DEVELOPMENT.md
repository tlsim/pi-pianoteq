# Development Guide

This guide is for developers who want to build pi_pianoteq on a development machine and deploy it to a remote Raspberry Pi.

## Prerequisites

### On Your Development Machine

Install pipenv:
```bash
pip install --user pipenv
```

### On Your Raspberry Pi

Install system dependencies:
```bash
sudo apt install python3-rtmidi linux-cpupower
```

- `python3-rtmidi`: Avoids compiling from source (which requires ALSA development headers)
- `linux-cpupower`: Required for CPU performance management in the systemd service

Other Python dependencies will be installed automatically into a virtual environment during deployment.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tlsim/pi-pianoteq.git
cd pi-pianoteq
```

### 2. Install Dependencies

```bash
pipenv install --dev
```

### 3. Configure Deployment

Create `deploy.conf` with your Pi's connection details:

```ini
[Deploy]
USER = <username>
PI_HOST = <hostname-or-ip>
```

Replace `<username>` with your Raspberry Pi username and `<hostname-or-ip>` with your Pi's hostname or IP address.

## Building and Deploying

### Build and Deploy in One Command

```bash
pipenv run build-and-deploy
```

### Or Run Separately

Build the package:
```bash
pipenv run package
```

Deploy to the Pi:
```bash
pipenv run deploy
```

The `deploy.sh` script will:
- Create a virtual environment on the Pi (if needed)
- Install the package
- Set up the systemd service
- Start the service

## Development Workflow

### Running Tests

```bash
pipenv run test
```

### Code Checks

```bash
pipenv run check
```

### Manual Testing

You can test commands without deploying:

```bash
pipenv run pi-pianoteq --show-config
pipenv run pi-pianoteq --init-config
pipenv run pi-pianoteq --cli  # Run CLI client for local testing
```

**Note:** Full testing requires hardware (MIDI, gfxhat) which may not be available on your dev machine. Use `--cli` flag to run the CLI client for testing without the GFX HAT.

## What deploy.sh Does

The deployment script:

1. Builds the wheel file (if not already built)
2. Copies the wheel to the Pi
3. Creates a virtual environment on the Pi with `--system-site-packages` (for python3-rtmidi)
4. Installs the package with `--force-reinstall --no-deps`
5. Generates and installs the systemd service file
6. Enables and restarts the service

## Updating the Version

When releasing a new version:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
4. Build and test
5. Commit and tag

## Direct Commands (without pipenv)

If you prefer not to use pipenv:

Build:
```bash
python3 -m build
```

Deploy:
```bash
./deploy.sh
```

**Note:** You'll need to install the `build` package first:
```bash
pip3 install --user build
```
