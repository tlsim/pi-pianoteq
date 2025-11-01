# Running pi-pianoteq as a Systemd Service

This guide explains how to set up pi-pianoteq to run automatically on boot using systemd.

## Automatic Setup (via deploy.sh)

If you used the `deploy.sh` script, the systemd service is already configured. Skip to [Managing the Service](#managing-the-service).

## Manual Setup

### 1. Create the Service File

Create `/etc/systemd/system/pi-pianoteq.service`:

```ini
[Unit]
Description = Service for pi-pianoteq

[Service]
Type=simple
User=<username>
Group=<username>
ExecStartPre=cpupower frequency-set -g performance
ExecStart=/usr/bin/python3 -u -m pi_pianoteq
ExecStopPost=cpupower frequency-set -g ondemand
PermissionsStartOnly=true
LimitMEMLOCK=500000
LimitRTPRIO=90
LimitNICE=-10
Nice=-10

[Install]
WantedBy=graphical.target
```

**Important:** Replace `<username>` with your Raspberry Pi username.

If you installed pi-pianoteq in a virtual environment, update the `ExecStart` line:
```ini
ExecStart=/home/<username>/venv/bin/python -u -m pi_pianoteq
```

### 2. Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-pianoteq
sudo systemctl start pi-pianoteq
```

## Managing the Service

Check the service status:
```bash
systemctl status pi-pianoteq
```

View logs:
```bash
sudo journalctl -u pi-pianoteq -f
```

Manage the service:
```bash
sudo systemctl stop pi-pianoteq      # Stop the service
sudo systemctl start pi-pianoteq     # Start the service
sudo systemctl restart pi-pianoteq   # Restart after config changes
sudo systemctl disable pi-pianoteq   # Disable auto-start on boot
```

## Pianoteq Headless Mode

The systemd service runs Pianoteq in headless mode by default (`PIANOTEQ_HEADLESS=true`).

**What this means:**
- Pianoteq runs without its GUI window (audio engine only)
- pi-pianoteq still provides an interface via the GFX HAT (if installed)
- Ideal for headless operation without a display connected

**To enable Pianoteq's GUI:**
1. Stop the service: `sudo systemctl stop pi-pianoteq`
2. Set `PIANOTEQ_HEADLESS=false` in `~/.config/pi_pianoteq/pi_pianoteq.conf`
3. Restart: `sudo systemctl start pi-pianoteq`

**Or run manually (without the service):**
```bash
sudo systemctl stop pi-pianoteq
PIANOTEQ_HEADLESS=false python -m pi_pianoteq
```

Note: You'll need a display (VNC, HDMI, etc.) to see the Pianoteq GUI.

## Performance Settings

The service file includes performance optimizations:
- **CPU governor**: Sets to `performance` mode on start, returns to `ondemand` on stop
- **Nice level**: `-10` for higher priority
- **Real-time limits**: Memory locking and RT priority for low-latency audio

These settings help ensure stable audio performance.
