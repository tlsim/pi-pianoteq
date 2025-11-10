# Pi-Pianoteq Tests

## Running Tests

### Setup

Install the package in development mode with dependencies:

```bash
pipenv install -e .
```

### Run All Tests

```bash
# From project root
pipenv run pytest
```

### Run Specific Test File

```bash
pipenv run pytest tests/client/gfxhat/test_preset_menu_display.py
pipenv run pytest tests/client/gfxhat/test_gfxhat_state_machine.py
pipenv run pytest tests/util/test_button_suppression.py
```

### Run Tests in Specific Directory

```bash
pipenv run pytest tests/client/gfxhat/  # All GFX HAT client tests
pipenv run pytest tests/config/         # Configuration tests
```

### Run Single Test

```bash
pipenv run pytest tests/client/gfxhat/test_preset_menu_display.py::test_current_preset_highlighted_for_current_instrument
```

### Run Tests with Coverage

```bash
# Run with terminal coverage report
pipenv run pytest --cov --cov-report=term-missing

# Generate HTML coverage report (opens in browser)
pipenv run pytest --cov --cov-report=html
# Then open htmlcov/index.html in browser

# Run with both terminal and HTML reports
pipenv run pytest --cov --cov-report=term-missing --cov-report=html
```

Coverage reports show:
- Overall coverage percentage
- Line-by-line coverage for each file
- Missing lines (not covered by tests)
- HTML report provides visual highlighting

## Test Directory Structure

Tests are organized to mirror the source code structure:

```
tests/
├── conftest.py              # Shared fixtures and hardware mocking
├── client/
│   └── gfxhat/
│       ├── test_gfxhat_state_machine.py
│       └── test_preset_menu_display.py
├── config/
│   └── test_config.py
├── instrument/
│   └── test_presets.py
├── logging/
│   └── test_logging_config.py
├── rpc/
│   └── test_jsonrpc_client.py
└── util/
    └── test_button_suppression.py
```

## Test Coverage

### Client Tests (client/gfxhat/)

- **test_preset_menu_display.py** - Preset menu functionality
  - Menu option generation
  - Preset selection
  - Current preset highlighting (context-aware)
  - Edge cases (empty list, preset not found)

- **test_gfxhat_state_machine.py** - GFX HAT client state management
  - Loading mode initialization
  - Display priority (preset menu > instrument menu > main)
  - Menu transitions (enter/exit)
  - Preset menu transitions (from main/instrument menu)
  - Cleanup (stop all scrolling)

### Core Component Tests

- **util/test_button_suppression.py** - ButtonSuppression timing logic
- **instrument/test_presets.py** - Preset display name stripping, instrument grouping
- **config/test_config.py** - Configuration loading
- **logging/test_logging_config.py** - Logging setup
- **rpc/test_jsonrpc_client.py** - JSON-RPC client

## Hardware Mocking

Hardware dependencies are automatically mocked by `conftest.py`:

- `gfxhat.lcd` - LCD display
- `gfxhat.touch` - Touch buttons
- `gfxhat.backlight` - RGB backlight
- `PIL.Image` / `PIL.ImageDraw` - Image rendering

The mocking is configured once in `conftest.py` and applies to all tests automatically. This allows tests to run on any system without requiring physical hardware.

## Adding New Tests

See `docs/testing-strategy.md` for comprehensive guidance on:
- What to test for each component
- Mocking strategies
- Edge cases to consider
- Test priorities

### Example Test Structure

```python
from unittest.mock import Mock
import pytest

def test_specific_behavior():
    """Test description explaining what and why."""
    # Arrange
    mock_api = Mock()
    component = MyComponent(mock_api)

    # Act
    result = component.do_something()

    # Assert
    assert result == expected_value
    mock_api.some_method.assert_called_once()
```

## Test Philosophy

Focus tests on:
1. **State transitions** - Verify state changes correctly
2. **API interactions** - Verify correct methods called with right args
3. **Edge cases** - Empty lists, None values, boundary conditions
4. **Integration points** - Callbacks, threading, cleanup

Avoid testing:
1. Implementation details (exact pixel positions)
2. Third-party library behavior
3. Hardware behavior (use mocks)

## CI/CD Integration

Tests can be run in CI/CD pipelines without hardware:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e .
    pytest
```

The hardware mocking (configured in `conftest.py`) allows tests to run on any system, including:
- Development machines (without GFX HAT)
- CI servers
- Docker containers
