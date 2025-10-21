# Pi-Pianoteq

Pi-Pianoteq is a Python/Midi remote control for Pianoteq

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

## Manual install
`pip3 install pi_pianoteq-1.0.0`

