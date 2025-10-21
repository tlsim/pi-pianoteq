# Pi-Pianoteq

Pi-Pianoteq is a Python/Midi remote control for Pianoteq

# Usage

First, check and update the configuration in `pi_pianoteq/pi_pianoteq.conf`

## Using pipenv (recommended)

Install dependencies
`pipenv install`

Build and deploy in one command
`pipenv run build-and-deploy`

Or run separately:
`pipenv run package` - Build the package
`pipenv run deploy` - Deploy to remote Raspberry Pi

## Direct commands

Build the package
`python3 setup.py sdist`

Deploy to remote Raspberry Pi
`./deploy.sh`

Or build and deploy
`python3 setup.py sdist && ./deploy.sh`

## Manual install
`pip3 install pi_pianoteq-1.0.0`

