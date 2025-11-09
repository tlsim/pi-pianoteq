# Preset Selection Menu Implementation Plan

## Overview

Implement preset selection using a menu interface for GFX HAT, accessed via long press on ENTER button.

**GitHub Issue:** #30 - GFX Hat Preset selection
**Related Issue:** #27 - CLI feature: typeahead preset selection

## User Experience

### From Main Display
- **Long press ENTER** → Opens preset menu for current instrument
- Navigate with LEFT/RIGHT/UP/DOWN
- Select preset → Loads it and returns to main display

### From Instrument Menu
- Navigate to any instrument (not just current)
- **Long press ENTER** → Opens preset menu for highlighted instrument
- Select preset → Switches to that instrument + preset, returns to main display

This provides full browsing capability - explore any instrument's presets before committing to the switch.

## Architecture Analysis

### Existing System Behavior

**Instrument Selection** (src/pi_pianoteq/instrument/selector.py:14-26):
- Always resets to first preset (index 0) when switching instruments
- `set_instrument_next()`, `set_instrument_prev()`, `set_instrument(name)` all set `current_instrument_preset_idx = 0`

**Preset Navigation** (src/pi_pianoteq/instrument/selector.py:31-42):
- UP/DOWN navigation wraps across instruments
- `set_preset_next()` at last preset → wraps to next instrument's first preset
- `set_preset_prev()` at first preset → wraps to prev instrument's last preset

**Preset Loading Mechanism**:
- Uses MIDI Program Change messages (not JSON-RPC `loadPreset`)
- Each preset assigned unique MIDI channel + program number (src/pi_pianoteq/instrument/library.py:31)
- Flow: Button press → Selector updates indices → ClientLib calls ProgramChange.set_preset() → MIDI sent → Pianoteq loads preset

**Hardware Support**:
- GFX HAT supports three event types: `'press'`, `'release'`, `'held'`
- Current implementation only uses `'press'` events
- Underlying cap1xxx library fully supports long press detection

## Implementation Steps

### 1. Extend ClientApi Interface

**File:** `src/pi_pianoteq/client/client_api.py`

Add abstract methods (consistent with existing naming - no "by_name" suffix):

```python
@abstractmethod
def get_preset_names(self, instrument_name: str) -> List[str]:
    raise NotImplemented

@abstractmethod
def set_preset(self, instrument_name: str, preset_name: str):
    raise NotImplemented
```

### 2. Implement API Methods in ClientLib

**File:** `src/pi_pianoteq/lib/client_lib.py`

```python
def get_preset_names(self, instrument_name: str) -> List[str]:
    """Get list of preset names for a specific instrument."""
    instrument = next((i for i in self.instrument_library.get_instruments()
                      if i.name == instrument_name), None)
    return [p.name for p in instrument.presets] if instrument else []

def set_preset(self, instrument_name: str, preset_name: str):
    """
    Set specific preset for a specific instrument.

    Switches to the instrument if not current, then loads the preset.
    Uses MIDI Program Change to trigger Pianoteq preset load.
    """
    # Find instrument
    instrument = next((i for i in self.instrument_library.get_instruments()
                      if i.name == instrument_name), None)
    if not instrument:
        return

    # Find preset within that instrument
    preset = next((p for p in instrument.presets if p.name == preset_name), None)
    if not preset:
        return

    # Update selector state
    self.selector.set_instrument(instrument_name)
    preset_idx = instrument.presets.index(preset)
    self.selector.current_instrument_preset_idx = preset_idx

    # Send MIDI
    self.program_change.set_preset(preset)
```

### 3. Create PresetMenuDisplay

**New File:** `src/pi_pianoteq/client/gfxhat/preset_menu_display.py`

```python
from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


class PresetMenuDisplay(MenuDisplay):
    """
    Menu display for selecting presets within a specific instrument.

    Shows list of presets for the given instrument, with scrolling support
    for long preset names. Extends MenuDisplay base class pattern.
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, instrument_name: str):
        """
        Initialize preset menu for a specific instrument.

        Args:
            api: Client API instance
            width: Display width in pixels
            height: Display height in pixels
            font: Font for rendering text
            on_exit: Callback when exiting menu
            instrument_name: Name of instrument whose presets to display
        """
        self.instrument_name = instrument_name
        super().__init__(api, width, height, font, on_exit)

    def get_menu_options(self):
        """Build menu options from preset names for this instrument."""
        preset_names = self.api.get_preset_names(self.instrument_name)
        return [MenuOption(name, self.set_preset, self.font, (name,))
                for name in preset_names]

    def set_preset(self, preset_name):
        """Load selected preset and exit menu."""
        self.api.set_preset(self.instrument_name, preset_name)
        self.on_exit()
```

### 4. Add Long Press Support to InstrumentDisplay

**File:** `src/pi_pianoteq/client/gfxhat/instrument_display.py`

**Constructor changes** (line 22):
```python
def __init__(self, api: ClientApi, width, height, font, on_enter, on_enter_preset_menu):
    # ... existing code ...
    self.on_enter = on_enter
    self.on_enter_preset_menu = on_enter_preset_menu  # NEW
```

**Handler changes** (line 88):
```python
def get_handler(self):
    def handler(ch, event):
        if event == 'press':
            # ... existing press handling ...
            if ch == touch.ENTER:
                if self.suppression.allow_action():
                    self.on_enter()

        elif event == 'held':  # NEW
            if ch == touch.ENTER:
                # Open preset menu for current instrument
                self.on_enter_preset_menu()

        # Only update display on press events
        if event == 'press':
            self.update_display()

    return handler
```

### 5. Add Long Press Support to InstrumentMenuDisplay

**File:** `src/pi_pianoteq/client/gfxhat/instrument_menu_display.py`

**Constructor changes** (line 12):
```python
def __init__(self, api: ClientApi, width, height, font, on_exit, on_enter_preset_menu):
    super().__init__(api, width, height, font, on_exit)
    self.on_enter_preset_menu = on_enter_preset_menu  # NEW
    # ... existing code ...
```

**Handler changes** (line 102 in parent MenuDisplay - override get_handler):
```python
def get_handler(self):
    # Get base handler
    base_handler = super().get_handler()

    def handler(ch, event):
        if event == 'held':  # NEW
            if ch == touch.ENTER:
                # Open preset menu for highlighted instrument (not necessarily current)
                highlighted_instrument = self.menu_options[self.current_menu_option].name
                if highlighted_instrument != "Shut down":  # Skip shutdown option
                    self.on_enter_preset_menu(highlighted_instrument)
                return

        # Delegate to base handler for press events
        base_handler(ch, event)

    return handler
```

### 6. Wire Up State Management in GfxhatClient

**File:** `src/pi_pianoteq/client/gfxhat/gfxhat_client.py`

**Add imports** (top of file):
```python
from pi_pianoteq.client.gfxhat.preset_menu_display import PresetMenuDisplay
```

**Add state tracking** (line 26):
```python
def __init__(self, api: Optional[ClientApi]):
    super().__init__(api)
    self.interrupt = False
    self.menu_open = False
    self.preset_menu_open = False  # NEW
    self.preset_menu_source = None  # NEW: 'main' or 'instrument_menu'
    # ... existing code ...
```

**Update display initialization** (line 43):
```python
def _init_normal_displays(self):
    self.api.set_on_exit(self.cleanup)
    self.instrument_display = InstrumentDisplay(
        self.api, self.width, self.height, self.font,
        self.on_enter_menu,
        self.on_enter_preset_menu_from_main  # NEW
    )
    self.menu_display = InstrumentMenuDisplay(
        self.api, self.width, self.height, self.font,
        self.on_exit_menu,
        self.on_enter_preset_menu_from_instrument_menu  # NEW
    )
    self.preset_menu_display = None  # NEW: Created dynamically
    self.loading_mode = False
```

**Add preset menu callbacks** (after line 151):
```python
def on_enter_preset_menu_from_main(self):
    """Long press ENTER on main display - show presets for current instrument."""
    instrument_name = self.api.get_current_instrument()
    self._open_preset_menu(instrument_name, source='main')

def on_enter_preset_menu_from_instrument_menu(self, instrument_name):
    """Long press ENTER on instrument menu item - show presets for highlighted instrument."""
    self._open_preset_menu(instrument_name, source='instrument_menu')

def _open_preset_menu(self, instrument_name, source):
    """Common preset menu opening logic."""
    # Stop current scrolling
    if source == 'main':
        self.instrument_display.stop_scrolling()
    else:  # from instrument menu
        self.menu_display.stop_scrolling()

    # Create preset menu for specific instrument
    from pi_pianoteq.client.gfxhat.preset_menu_display import PresetMenuDisplay
    self.preset_menu_display = PresetMenuDisplay(
        self.api, self.width, self.height, self.font,
        self.on_exit_preset_menu, instrument_name
    )

    self.preset_menu_open = True
    self.preset_menu_source = source
    self.preset_menu_display.start_scrolling()
    self.update_handler()

def on_exit_preset_menu(self):
    """Exit preset menu and return to previous display."""
    self.preset_menu_display.stop_scrolling()
    self.preset_menu_open = False

    # Return to where we came from
    if self.preset_menu_source == 'main':
        self.instrument_display.update_display()
        self.instrument_display.start_scrolling()
    else:  # from instrument menu
        self.menu_display.start_scrolling()

    self.update_handler()
```

**Update display getter** (line 111):
```python
def get_display(self):
    """Get current active display (loading, preset menu, menu, or instrument)."""
    if self.loading_mode:
        return self.loading_display
    elif self.preset_menu_open:  # NEW: Check preset menu first
        return self.preset_menu_display
    elif self.menu_open:
        return self.menu_display
    else:
        return self.instrument_display
```

**Update cleanup** (line 126):
```python
def cleanup(self):
    self.interrupt = True
    # Stop all scrolling threads (if displays are initialized)
    if self.instrument_display:
        self.instrument_display.stop_scrolling()
    if self.menu_display:
        self.menu_display.stop_scrolling()
    if self.preset_menu_display:  # NEW
        self.preset_menu_display.stop_scrolling()
    # ... existing cleanup code ...
```

## Testing Plan

### Manual Testing on Pi

1. **Basic preset menu from main display:**
   - Long press ENTER on main display
   - Verify preset menu opens for current instrument
   - Navigate with LEFT/RIGHT/UP/DOWN
   - Select preset, verify it loads and returns to main display

2. **Preset menu from instrument menu:**
   - Press ENTER to open instrument menu
   - Navigate to different instrument
   - Long press ENTER on highlighted instrument
   - Verify preset menu shows that instrument's presets
   - Select preset, verify both instrument and preset switch

3. **Edge cases:**
   - Long press on "Shut down" menu item (should do nothing)
   - Press BACK to exit preset menu without selecting
   - Verify scrolling works for long preset names
   - Test with instrument that has many presets

4. **Scrolling cleanup:**
   - Verify no thread leaks when opening/closing menus
   - Check logs for any threading errors

### CLI Testing

Test with `pipenv run pi-pianoteq --cli` to verify API changes don't break CLI client.

## Files Modified

1. `src/pi_pianoteq/client/client_api.py` - Add abstract methods
2. `src/pi_pianoteq/lib/client_lib.py` - Implement preset selection methods
3. `src/pi_pianoteq/client/gfxhat/preset_menu_display.py` - NEW FILE
4. `src/pi_pianoteq/client/gfxhat/instrument_display.py` - Add long press handler
5. `src/pi_pianoteq/client/gfxhat/instrument_menu_display.py` - Add long press handler
6. `src/pi_pianoteq/client/gfxhat/gfxhat_client.py` - Wire up preset menu state

## Future Enhancements

- Consider showing preset count in instrument menu (e.g., "Grand K2 (8)")
- Explore typeahead/search for CLI (issue #27)

---

## Appendix: Preset Highlighting Enhancement

This section details how to highlight the currently loaded preset when opening the preset menu, similar to how the instrument menu highlights the current instrument.

### Existing Pattern

The instrument menu already implements this feature (src/pi_pianoteq/client/gfxhat/instrument_menu_display.py:28-34):

```python
def update_instrument(self):
    current_instrument = self.api.get_current_instrument()
    current_option = next((o for o in self.menu_options if o.name == current_instrument), None)
    if current_option is not None:
        self.current_menu_option = self.menu_options.index(current_option)
        self._update_selected_option()
        self.draw_image()
```

When the instrument menu opens, it finds the currently playing instrument and positions the menu selection on it.

### Implementation for Presets

**Step 1:** Update `PresetMenuDisplay.__init__()` to call a new method:

```python
def __init__(self, api: ClientApi, width, height, font, on_exit, instrument_name: str):
    """
    Initialize preset menu for a specific instrument.

    Args:
        api: Client API instance
        width: Display width in pixels
        height: Display height in pixels
        font: Font for rendering text
        on_exit: Callback when exiting menu
        instrument_name: Name of instrument whose presets to display
    """
    self.instrument_name = instrument_name
    super().__init__(api, width, height, font, on_exit)
    self.update_preset()  # Position on current preset if applicable
```

**Step 2:** Add the `update_preset()` method to `PresetMenuDisplay`:

```python
def update_preset(self):
    """Highlight currently loaded preset if viewing current instrument's presets."""
    # Only highlight if we're viewing the current instrument's presets
    if self.instrument_name == self.api.get_current_instrument():
        current_preset = self.api.get_current_preset()
        current_option = next((o for o in self.menu_options if o.name == current_preset), None)
        if current_option is not None:
            self.current_menu_option = self.menu_options.index(current_option)
            self._update_selected_option()
            self.draw_image()
```

### User Experience Examples

**Scenario 1: Long press from main display**
- Currently playing "Grand K2 - Classical"
- Long press ENTER → Opens preset menu
- Menu opens with "Classical" already highlighted ✓
- User can immediately see their position in the preset list
- Navigate to "Jazz" and select it

**Scenario 2: Long press from instrument menu (different instrument)**
- Currently playing "Grand K2 - Classical"
- Navigate instrument menu to "Vibraphone V-B"
- Long press ENTER → Opens preset menu for Vibraphone
- Menu opens with first preset highlighted (not "Classical", since that's a K2 preset)
- User browses Vibraphone presets without confusion

**Scenario 3: After switching presets**
- Select "Vibraphone V-B - Soft" from preset menu
- Returns to main display
- Long press ENTER again → Opens preset menu
- Now "Soft" is highlighted (the new current preset) ✓

**Scenario 4: Browsing other instruments**
- Currently playing "Grand K2 - Classical"
- Open instrument menu, navigate to "Vibraphone V-B"
- Long press ENTER → Opens Vibraphone preset menu
- First preset highlighted (we're not on Vibraphone currently)
- This avoids confusion - only highlights when viewing current instrument's presets

### Why Context-Aware Highlighting Matters

The highlighting only activates when `self.instrument_name == self.api.get_current_instrument()` because:

1. **Clarity**: If you're browsing a different instrument's presets, highlighting would be misleading
2. **Consistency**: The first preset being highlighted when browsing other instruments matches the "switching instruments loads preset 0" behavior
3. **User Intent**: If you're exploring other instruments, you're not looking for your current position

### Benefits

- **Immediate Context**: User knows where they are in the preset list
- **Faster Navigation**: Can quickly jump to nearby presets without counting
- **Familiar Pattern**: Matches existing instrument menu behavior
- **No Confusion**: Smart enough to only highlight when contextually relevant
