# Pi-Pianoteq Tests

## Running Tests

### Setup

Install the package in development mode with dependencies:

```bash
pipenv install -e .
```

Or install test dependencies manually:
```bash
pip install pillow python-rtmidi
```

### Run All Tests

```bash
# From project root
python -m unittest discover tests -v
```

### Run Specific Test File

```bash
python -m unittest tests.test_preset_menu_display -v
python -m unittest tests.test_gfxhat_state_machine -v
python -m unittest tests.test_button_suppression -v
```

### Run Single Test

```bash
python -m unittest tests.test_preset_menu_display.PresetMenuDisplayTestCase.test_current_preset_highlighted_for_current_instrument
```

## Test Coverage

### Existing Tests

- **test_button_suppression.py** - ButtonSuppression timing logic
- **test_presets.py** - Preset display name stripping, instrument grouping
- **test_config.py** - Configuration loading
- **test_logging_config.py** - Logging setup
- **test_jsonrpc_client.py** - JSON-RPC client

### New Tests (GFX HAT Client)

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

## Hardware Mocking

The GFX HAT tests use `unittest.mock` to mock hardware dependencies:

- `gfxhat.lcd` - LCD display
- `gfxhat.touch` - Touch buttons
- `gfxhat.backlight` - RGB backlight
- `PIL.Image` / `PIL.ImageDraw` - Image rendering

Example:
```python
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.lcd')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.touch')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.backlight')
def test_something(self, mock_backlight, mock_touch, mock_lcd):
    # Hardware is mocked - test logic without physical hardware
```

## Adding New Tests

See `docs/testing-strategy.md` for comprehensive guidance on:
- What to test for each component
- Mocking strategies
- Edge cases to consider
- Test priorities

### Example Test Structure

```python
import unittest
from unittest.mock import Mock, patch

class MyComponentTestCase(unittest.TestCase):
    def setUp(self):
        """Set up common fixtures used across tests."""
        self.mock_api = Mock()
        # Set up return values...

    def test_specific_behavior(self):
        """Test description explaining what and why."""
        # Arrange
        component = MyComponent(self.mock_api)

        # Act
        result = component.do_something()

        # Assert
        self.assertEqual(expected, result)
        self.mock_api.some_method.assert_called_once()
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
    python -m unittest discover tests -v
```

The hardware mocking allows tests to run on any system, including:
- Development machines (without GFX HAT)
- CI servers
- Docker containers
