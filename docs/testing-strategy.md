# GFX HAT Client Testing Strategy

## Overview

The GFX HAT client has grown in complexity with the addition of the preset menu feature. This document outlines a comprehensive testing strategy for unit testing the client components.

## Testing Priorities

### High Priority (Core Functionality)
1. **State transitions** in GfxhatClient (menu navigation)
2. **Button handler logic** (correct API calls, event routing)
3. **ScrollingText thread management** (prevent memory leaks)
4. **Menu wrapping** at boundaries (first/last item navigation)
5. **Button suppression** integration (prevent double-triggers)

### Medium Priority (Correctness)
1. Display selection logic (loading/preset menu/instrument menu/main)
2. Scrolling text offset calculations
3. Backlight color application
4. Handler updates during state transitions
5. Cleanup completeness (all threads stopped)

### Low Priority (Nice to Have)
1. Exact pixel positions in drawing
2. Text wrapping visual details
3. Edge cases in color conversion
4. Multiple cleanup call handling

## Component Testing Guide

### 1. ScrollingText

**Key Behaviors to Test:**
- Text width detection (needs_scrolling flag)
- Scroll offset increments and wrapping
- Initial delay before scrolling starts
- Thread lifecycle (start/stop/restart)
- Thread safety (get_offset from multiple threads)
- Text updates with dynamic restart

**Mocking Strategy:**
```python
@patch('threading.Thread')
@patch('time.sleep')
def test_scrolling_behavior(self, mock_sleep, mock_thread):
    mock_font = Mock()
    mock_font.getbbox.return_value = (0, 0, 150, 10)  # Width > max_width

    scroller = ScrollingText("Long text", mock_font, max_width=100)
    assert scroller.needs_scrolling == True
```

**Critical Edge Cases:**
- Empty text
- Text exactly equal to max_width
- Calling stop() when not started
- Rapid start/stop cycles

### 2. GfxhatClient State Machine

**Key Behaviors to Test:**
- Loading mode → Normal mode transition
- Main display ↔ Instrument menu transitions
- Main display → Preset menu (current instrument)
- Instrument menu → Preset menu (any instrument)
- Preset menu → return to source display
- Handler updates match current display

**Mocking Strategy:**
```python
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.lcd')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.touch')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.backlight')
def test_preset_menu_from_main(self, mock_backlight, mock_touch, mock_lcd):
    mock_api = Mock(spec=ClientApi)
    mock_api.get_current_instrument.return_value = "Piano"

    client = GfxhatClient(mock_api)
    client.on_enter_preset_menu_from_main()

    assert client.preset_menu_open == True
    assert client.preset_menu_source == 'main'
```

**Critical Edge Cases:**
- State transitions while scrolling active
- Cleanup with partially initialized displays
- Menu flags inconsistent (shouldn't happen but test robustness)

### 3. Menu Navigation

**Key Behaviors to Test:**
- UP/DOWN/LEFT/RIGHT navigation
- Wrapping at first/last items
- ENTER triggers selected action (when not suppressed)
- BACK exits menu
- Current option scrolling text updates
- Button suppression prevents rapid triggers

**Mocking Strategy:**
```python
def test_menu_wrapping(self):
    mock_api = Mock(spec=ClientApi)
    mock_api.get_preset_names.return_value = ["A", "B", "C"]

    menu = PresetMenuDisplay(mock_api, 128, 64, mock_font,
                             on_exit=Mock(), instrument_name="Piano")

    # At first item, UP wraps to last
    menu.current_menu_option = 0
    handler = menu.get_handler()
    handler(touch.UP, 'press')

    assert menu.current_menu_option == 2  # Wrapped to "C"
```

**Critical Edge Cases:**
- Empty menu options list
- Single item menu
- Very long option names (scrolling)

### 4. Button Event Handling

**Key Behaviors to Test:**
- Press events trigger correct API calls
- Held events trigger preset menu
- Suppression blocks rapid ENTER presses
- Navigation buttons record suppression
- Events update display

**Mocking Strategy:**
```python
def test_held_enter_opens_preset_menu(self):
    mock_api = Mock(spec=ClientApi)
    callback = Mock()

    display = InstrumentDisplay(mock_api, 128, 64, mock_font,
                                on_enter=Mock(),
                                on_enter_preset_menu=callback)

    handler = display.get_handler()
    handler(touch.ENTER, 'held')

    callback.assert_called_once()
```

**Critical Edge Cases:**
- Unknown event types (should ignore)
- Rapid press/held events
- Suppression timing edge cases

### 5. Preset Menu Highlighting

**Key Behaviors to Test:**
- Current preset highlighted when viewing current instrument
- No highlighting when viewing different instrument
- Scrolling starts at highlighted position
- Preset not in list handled gracefully

**Mocking Strategy:**
```python
def test_preset_highlighting(self):
    mock_api = Mock(spec=ClientApi)
    mock_api.get_current_instrument.return_value = "Piano"
    mock_api.get_current_preset.return_value = "Bright"
    mock_api.get_preset_names.return_value = ["Dark", "Bright", "Medium"]

    menu = PresetMenuDisplay(mock_api, 128, 64, mock_font,
                             on_exit=Mock(), instrument_name="Piano")

    # Should position on "Bright" (index 1)
    assert menu.current_menu_option == 1
```

**Critical Edge Cases:**
- Empty preset list
- Current preset not in list
- Multiple presets with same name (shouldn't happen)

## Mocking Hardware Dependencies

### LCD, Touch, Backlight
```python
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.lcd')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.touch')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.backlight')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.fonts')
class GfxhatClientTestCase(unittest.TestCase):
    # Tests here have hardware mocked automatically
```

### ClientApi
```python
def create_mock_api():
    mock_api = Mock(spec=ClientApi)
    mock_api.get_current_instrument.return_value = "Piano"
    mock_api.get_current_preset.return_value = "Bright"
    mock_api.get_preset_names.return_value = ["Dark", "Bright"]
    mock_api.get_instrument_names.return_value = ["Piano", "Strings"]
    return mock_api
```

### PIL Image/Draw
```python
@patch('PIL.ImageDraw.Draw')
@patch('PIL.Image.new')
def test_drawing(self, mock_image, mock_draw):
    mock_image.return_value = Mock()
    mock_draw.return_value = Mock()
    # Test drawing logic without actual image operations
```

## Test File Organization

```
tests/
├── test_gfxhat_client.py          # Main state machine
├── test_scrolling_text.py         # Threading and scrolling
├── test_instrument_display.py     # Main display handlers
├── test_menu_display.py           # Base menu logic
├── test_preset_menu_display.py    # Preset menu
├── test_instrument_menu_display.py # Instrument menu
└── test_backlight.py              # Color management
```

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_gfxhat_client

# Run with verbose output
python -m unittest discover tests -v
```

## Example: Minimal Test Suite to Start

Start with these high-value tests:

1. **test_gfxhat_client.py**
   - Loading mode initialization
   - set_api() transition
   - get_display() returns correct display for each state
   - Menu state transitions (enter/exit)
   - Preset menu transitions with correct source tracking
   - Cleanup stops all scrolling

2. **test_scrolling_text.py**
   - needs_scrolling detection
   - Thread starts/stops correctly
   - offset wraps at wrap_point
   - update_text() restarts if running

3. **test_preset_menu_display.py**
   - Preset highlighting for current instrument
   - No highlighting for different instrument
   - set_preset() calls API and exits

These core tests provide coverage of the most critical functionality and state management.
