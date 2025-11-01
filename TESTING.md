# Testing Guide for Issue #17 Changes

This guide covers testing the naming consistency fixes and new application structure.

## What Changed

1. **Package name**: `pi_pianoteq` → `pi-pianoteq` (distribution name)
2. **Module structure**: Moved to `src/` layout
3. **Console script**: Can now run `pi-pianoteq` command (instead of `python -m pi_pianoteq`)
4. **Service name**: `pi_pianoteq.service` → `pi-pianoteq.service`
5. **Installation**: Simplified to `pip install --user` for normal use

## Cleanup Old Installation

If you have the old version installed, clean it up first:

### 1. Stop and Remove Old Systemd Service

```bash
# Stop the old service if running
sudo systemctl stop pi_pianoteq
sudo systemctl disable pi_pianoteq

# Remove old service file
sudo rm -f /etc/systemd/system/pi_pianoteq.service
sudo systemctl daemon-reload
```

### 2. Remove Old Package Installation

**If installed in venv (old deploy.sh):**
```bash
rm -rf ~/pi_pianoteq_venv
```

**If installed with --user:**
```bash
pip uninstall pi-pianoteq
# Note: pip should recognize both old and new names
```

**If installed system-wide:**
```bash
sudo pip uninstall pi-pianoteq
```

### 3. Verify Cleanup

```bash
# Should not find the old command
which pi-pianoteq  # Should return nothing or not found

# Check for leftover files
ls ~/.local/bin/ | grep pianoteq
ls /usr/local/bin/ | grep pianoteq
```

## Testing as Normal User

This tests the end-user installation path.

### 1. Build the Package

From your development machine:

```bash
cd pi-pianoteq
git checkout claude/fix-naming-inconsistency-011CUhvxkXBzw9DGKDvU7U6d
python3 -m build
```

Verify the wheel was created:
```bash
ls dist/pi_pianoteq-*.whl
```

### 2. Copy to Pi

```bash
scp dist/pi_pianoteq-*.whl pi@your-pi-hostname:~/
```

### 3. Install on Pi

SSH to your Pi:
```bash
ssh pi@your-pi-hostname
```

Install the package:
```bash
pip install --user ~/pi_pianoteq-*.whl
```

### 4. Verify Installation

Check that the console script was created:
```bash
ls -la ~/.local/bin/pi-pianoteq
which pi-pianoteq  # Should show ~/.local/bin/pi-pianoteq
```

### 5. Test Running

**Initialize config:**
```bash
pi-pianoteq --init-config
```

Verify config file was created at `~/.config/pi_pianoteq/pi_pianoteq.conf`

**Show config:**
```bash
pi-pianoteq --show-config
```

Should display configuration without errors.

**Test CLI mode (if Pianoteq is not running):**
```bash
pi-pianoteq --cli
```

Should start without errors. Press `q` to quit.

**Test with Pianoteq (if available):**
```bash
# Start Pianoteq first, then:
pi-pianoteq --cli
```

Verify:
- Instruments are discovered
- Can navigate presets
- Can switch instruments

### 6. Test Systemd Service (Optional)

Follow the instructions in SYSTEMD.md to set up the service.

**Create service file** (`/etc/systemd/system/pi-pianoteq.service`):
```ini
[Unit]
Description = Service for pi-pianoteq

[Service]
Type=simple
User=pi
Group=pi
ExecStartPre=cpupower frequency-set -g performance
ExecStart=/home/pi/.local/bin/pi-pianoteq
ExecStopPost=cpupower frequency-set -g ondemand
PermissionsStartOnly=true
LimitMEMLOCK=500000
LimitRTPRIO=90
LimitNICE=-10
Nice=-10

[Install]
WantedBy=graphical.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-pianoteq
sudo systemctl start pi-pianoteq
```

**Check status:**
```bash
systemctl status pi-pianoteq
sudo journalctl -u pi-pianoteq -f
```

Verify:
- Service starts without errors
- No permission issues
- Pianoteq launches correctly
- Instruments are discovered

**Stop service when done testing:**
```bash
sudo systemctl stop pi-pianoteq
```

## Testing Development Workflow

This tests the deploy.sh workflow for developers.

### 1. Set Up deploy.conf

On your development machine, create `deploy.conf`:

```ini
[Deploy]
USER = pi
PI_HOST = your-pi-hostname
```

### 2. Clean Old Venv on Pi (if exists)

SSH to Pi and remove old venv:
```bash
rm -rf ~/pi_pianoteq_venv
```

### 3. Run deploy.sh

From your development machine:

```bash
cd pi-pianoteq
git checkout claude/fix-naming-inconsistency-011CUhvxkXBzw9DGKDvU7U6d

# Build and deploy
pipenv run build-and-deploy
# Or separately:
# pipenv run package
# pipenv run deploy
```

### 4. Verify Deployment

SSH to your Pi:

```bash
# Check venv was created with new name
ls -la ~/pi-pianoteq-venv/bin/pi-pianoteq

# Check service was installed
systemctl status pi-pianoteq
sudo journalctl -u pi-pianoteq -n 50
```

Verify:
- Venv created at `~/pi-pianoteq-venv` (new name with hyphen)
- Service is running
- Service uses correct path: `/home/pi/pi-pianoteq-venv/bin/pi-pianoteq`
- Application starts without errors

### 5. Test Dual Install Pattern (Optional)

While deploy.sh is running the venv version, you can also install a stable version:

```bash
# On Pi, install stable version
pip install --user ~/pi_pianoteq-*.whl

# Now you have both:
ls -la ~/pi-pianoteq-venv/bin/pi-pianoteq        # Dev version
ls -la ~/.local/bin/pi-pianoteq                  # Stable version

# Systemd uses dev version (venv)
systemctl status pi-pianoteq

# Can manually run stable version
sudo systemctl stop pi-pianoteq
~/.local/bin/pi-pianoteq --cli
```

## What to Test

### Core Functionality

- [ ] Package builds successfully
- [ ] Console script `pi-pianoteq` is created
- [ ] `--init-config` creates config file
- [ ] `--show-config` displays configuration
- [ ] `--cli` mode works without Pianoteq
- [ ] Application discovers instruments via JSON-RPC API
- [ ] Can navigate presets and instruments
- [ ] MIDI port communication works

### Installation Paths

- [ ] `pip install --user` installs to `~/.local/bin/pi-pianoteq`
- [ ] `deploy.sh` creates venv at `~/pi-pianoteq-venv`
- [ ] Console script is executable
- [ ] Correct Python interpreter is used

### Systemd Service

- [ ] Service file references correct path
- [ ] Service starts without errors
- [ ] Service restarts on failure
- [ ] Logs are accessible via journalctl
- [ ] CPU governor changes work (performance/ondemand)

### Naming Consistency

- [ ] Package metadata shows `Name: pi-pianoteq`
- [ ] Wheel filename is `pi_pianoteq-*.whl` (normalized)
- [ ] Service is named `pi-pianoteq.service`
- [ ] Venv directory is `pi-pianoteq-venv`
- [ ] All docs reference correct names

## Known Issues to Watch For

### Path Issues
- Ensure `~/.local/bin` is in PATH (add to `~/.bashrc` if needed)
- Check that service file uses absolute paths, not relative

### Permission Issues
- Service should run as regular user, not root
- Config files should be in user's home directory
- No sudo required for normal installation

### Migration Issues
- Old service name might conflict (clean up first)
- Old venv path needs to be removed
- Old package needs to be uninstalled

## Reporting Issues

If you encounter problems:

1. Check service logs: `sudo journalctl -u pi-pianoteq -n 100`
2. Check permissions: `ls -la ~/.local/bin/pi-pianoteq`
3. Verify PATH: `echo $PATH | grep .local/bin`
4. Test console script directly: `~/.local/bin/pi-pianoteq --show-config`

Note any errors or unexpected behavior for the pull request review.
