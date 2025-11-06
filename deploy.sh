#!/usr/bin/env bash

# Read configuration from deploy.conf
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/deploy.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: deploy.conf not found!"
    exit 1
fi

# Parse config file
USER=$(grep -E '^USER\s*=' "$CONFIG_FILE" | sed 's/^USER\s*=\s*//' | tr -d ' ')
PI_HOST=$(grep -E '^PI_HOST\s*=' "$CONFIG_FILE" | sed 's/^PI_HOST\s*=\s*//' | tr -d ' ')

if [ -z "$USER" ] || [ -z "$PI_HOST" ]; then
    echo "Error: USER and PI_HOST must be set in deploy.conf"
    exit 1
fi

REMOTE="$USER@$PI_HOST"

# Generate service file from template
sed "s/{{USER}}/$USER/g" pi-pianoteq.service.template > pi-pianoteq.service

echo "Deploying to $REMOTE..."

# Find the built wheel file (most recent)
WHEEL_FILE=$(ls -t dist/pi_pianoteq-*-py3-none-any.whl | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "Error: No wheel file found in dist/"
    exit 1
fi
WHEEL_BASENAME=$(basename "$WHEEL_FILE")
echo "Deploying $WHEEL_FILE..."

scp "$WHEEL_FILE" $REMOTE:/tmp/$WHEEL_BASENAME
scp pi-pianoteq.service $REMOTE:/tmp/pi-pianoteq.service

ssh $REMOTE <<EOF
# Create virtual environment if it doesn't exist
VENV_PATH="/home/$USER/pi-pianoteq-venv"
if [ ! -d "\$VENV_PATH" ]; then
    echo "Creating virtual environment at \$VENV_PATH..."
    python3 -m venv --system-site-packages "\$VENV_PATH"
fi

# Install/upgrade package in venv (dependencies will use system packages where available)
echo "Installing pi-pianoteq into virtual environment..."
"\$VENV_PATH/bin/pip" install --upgrade --force-reinstall --no-deps /tmp/$WHEEL_BASENAME

# Update systemd service
sudo mv /tmp/pi-pianoteq.service /etc/systemd/system/pi-pianoteq.service
sudo chmod 644 /etc/systemd/system/pi-pianoteq.service

# Restart service
sudo systemctl daemon-reload
sudo systemctl enable pi-pianoteq
sudo systemctl restart pi-pianoteq

# Cleanup
rm /tmp/pi-pianoteq*

EOF

echo "Deployment complete!"
