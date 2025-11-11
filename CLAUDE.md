# Claude AI Assistant Context

This file contains development context and conventions for AI assistants working on this project.

## Environment

### Development Machine
- **Python**: Uses `pipenv` for dependency management
- **User**: tom
- **Project location**: `/home/tom/Develop/pi-pianoteq`

### Raspberry Pi (Deployment Target)
- **Hostname/IP**: `192.168.0.169`
- **SSH User**: `tom`
- **Python**: System Python with virtual environment
- **Hardware**: Raspberry Pi 4B with Pimoroni GFX HAT (128x64 LCD, 6 buttons, RGB backlight)
- **Pianoteq**: STAGE version 8.4.3 (licensed with 5 instruments)
- **Service**: Runs as systemd service `pi-pianoteq.service`

## Build & Deploy Workflow

### Initial Setup (Development Environment)
```bash
# Install dependencies and package in editable mode
pipenv install -e .
```

### Local Testing & Deployment

Use pipenv for Python operations; run build/deploy scripts directly (NOT with `pipenv run`):

```bash
# Local testing
pipenv run pi-pianoteq --cli

# Build and deploy to Pi
python3 -m build
./deploy.sh  # Auto-restarts pi-pianoteq.service, runs GFX HAT client
```

**Important**: Don't use `timeout` with CLI client on Pi via SSH - causes terminal issues.

### Running Tests

The project uses pytest with mocked hardware dependencies (configured in `tests/conftest.py`).

**With pipenv (preferred on development machine):**
```bash
pipenv run pytest tests/ -v
```

**Without pipenv (e.g., CI environments, sandboxed sessions):**
```bash
# Install dependencies
pip3 install pytest pillow

# Run tests with PYTHONPATH set
PYTHONPATH=src python3 -m pytest tests/ -v
```

**Test structure:**
- `tests/conftest.py` - Mocks hardware dependencies (gfxhat, PIL) before test imports
- Hardware modules (gfxhat.lcd, gfxhat.touch, etc.) are mocked automatically
- No need for actual hardware or display drivers to run tests
- All tests should pass

**When to run tests:**
- After making API changes to verify all clients still work
- Before committing significant refactoring
- When updating test mocks after changing method signatures

## Code Style & Conventions

### Comments
- Keep comments concise and factual
- No unnecessary enthusiasm ("thread-safe!" → "thread-safe")
- No implementation commentary ("Calming blue" → just the hex value)
- No "TODO", "FIXME", or interim comments like "now do this..."
- Remove WIP implementation details before committing

### Architecture Patterns
- Clients use two-phase initialization: `__init__(api=None)` → `set_api(api)` → `start()`
- Loading mode allows display before API availability
- GFX HAT and CLI clients follow parallel patterns (LoadingDisplay, get_display(), etc.)

### Error Handling
- Use logger for errors/warnings, not print() statements (except for user-facing CLI output)
- CLI mode uses buffered logging to avoid breaking the UI

## Project-Specific Knowledge

### Pianoteq Integration
- **JSON-RPC API**: `http://localhost:8081/jsonrpc` (since Pianoteq 7+)
- **License Detection**: `getActivationInfo()` returns `error_msg: "Demo"` (trial, 51+ instruments) or `""` (licensed, 11 instruments on Pi)
- **Startup Timing**: API available ~6 seconds, instruments loaded ~6-8 seconds (after license check)

### Loading Screen
- Two messages: "Starting..." and "Loading..."
- GFX HAT: Blue backlight (#1e3a5f), centered text on 128x64 display
- CLI: Full-screen prompt_toolkit Application with live log window
- Keep messages short to fit on small LCD (max ~18-20 chars)

### Version Management
- Update `pyproject.toml` version
- Update `CHANGELOG.md` with user-facing changes only
- Build and deploy
- No need to commit before testing - deploy and verify first

### CHANGELOG Guidelines
- **Added**: New user-facing features
- **Changed**: User-visible behavior changes
- **Fixed**: Bug fixes users would notice
- **Removed**: Removed features
- Do NOT include internal implementation details ("refactored X", "unified Y architecture")
- Do NOT include "Changed" entries for WIP code - only for changes between versions

## Common Tasks

### After Code Changes
```bash
python3 -m build && ./deploy.sh
# Wait ~15 seconds, then check logs
ssh tom@192.168.0.169 "sudo journalctl -u pi-pianoteq.service -n 30"
```

### Service Management
```bash
# Status
ssh tom@192.168.0.169 "sudo systemctl status pi-pianoteq.service"

# Logs (use -n 50, --since '5 minutes ago', etc.)
ssh tom@192.168.0.169 "sudo journalctl -u pi-pianoteq.service -n 50"
```

### JSON-RPC API Reference
See `docs/pianoteq-api.md` for complete API documentation with examples.

### Create a Release
```bash
# After updating version in pyproject.toml and CHANGELOG.md
gh release create v1.X.X \
  --title "Release 1.X.X" \
  --notes "Release notes here..."
```

**Note:** GitHub Actions will automatically build and attach the `.whl` file - don't attach manually.

Release notes format:
- Keep similar structure to previous releases (see `gh release view v1.6.0`)
- Include "What's New" with bullet points grouped by feature
- End with link to full CHANGELOG

## Debugging Tips

- **Startup logs**: Check for "Discovered N instruments" (11=licensed, 51+=demo) and license status ("Licensed" or "Demo/Trial")
- **API errors during startup**: Multiple ERROR logs normal during ~6 second API initialization
- **Virtual environment**: Pi uses `--system-site-packages` for python3-rtmidi

## File Structure Notes

- `src/pi_pianoteq/client/` - Client implementations (GFX HAT, CLI)
- `src/pi_pianoteq/rpc/jsonrpc_client.py` - Pianoteq JSON-RPC wrapper
- `src/pi_pianoteq/config/config.py` - Configuration and instrument discovery
- `src/pi_pianoteq/__main__.py` - Main entry point with loading sequence
- `deploy.sh` - Deployment script (reads `deploy.conf` for Pi connection details)
- `docs/` - Documentation (API reference, development guide, systemd setup)

