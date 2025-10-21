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
sed "s/{{USER}}/$USER/g" pi_pianoteq.service.template > pi_pianoteq.service

echo "Deploying to $REMOTE..."

scp dist/pi_pianoteq-1.0.0-py3-none-any.whl $REMOTE:/tmp/pi_pianoteq-1.0.0-py3-none-any.whl
scp pi_pianoteq.service $REMOTE:/tmp/pi_pianoteq.service

ssh $REMOTE <<EOF
sudo mv /tmp/pi_pianoteq.service /etc/systemd/system/pi_pianoteq.service
sudo chmod 644 /etc/systemd/system/pi_pianoteq.service

pip3 install --break-system-packages --upgrade --force-reinstall --no-deps /tmp/pi_pianoteq-1.0.0-py3-none-any.whl

sudo systemctl daemon-reload
sudo systemctl enable pi_pianoteq
sudo systemctl restart pi_pianoteq

rm /tmp/pi_pianoteq*

EOF

echo "Deployment complete!"
