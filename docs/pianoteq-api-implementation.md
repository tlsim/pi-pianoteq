# Pianoteq JSON-RPC API - Implementation Notes

Implementation status for the pi-pianoteq project. For complete API documentation, see [pianoteq-api.md](pianoteq-api.md).

---

## Current API Usage (v2.2.0+)

The project uses **4 out of 37+ available methods**:

| Method | Usage | Location |
|--------|-------|----------|
| `getActivationInfo()` | Detect licensed vs trial | `jsonrpc_client.py:116`, `__main__.py` |
| `getListOfPresets()` | Discover available instruments | `jsonrpc_client.py:87`, `config.py` |
| `getInfo()` | Sync with current preset at startup | `jsonrpc_client.py:99`, `client_lib.py:31` |
| `loadPreset()` | Load presets during navigation | `jsonrpc_client.py:147`, `client_lib.py` |

**Runtime control uses JSON-RPC:**
- Preset switching: Direct `loadPreset(name, bank)` calls
- No MIDI output required for preset selection (MIDI input preserved for future features)

---

## Navigation

Prev/next buttons work via:
1. GFX HAT buttons trigger menu navigation
2. Menu calls `client_lib.set_preset_next()` / `set_preset_prev()`
3. ClientLib calls `jsonrpc.load_preset(preset.name)`
4. Pianoteq loads the preset directly

---

## Unused API Features

### Could Add New Features
- `getParameters()` / `setParameters()` - Runtime parameter control from buttons
- `abSwitch()` / `abCopy()` - Quick preset comparison
- `getMetronome()` / `setMetronome()` - Metronome toggle
- MIDI sequencer methods - Demo playback control
- `getPerfInfo()` - CPU usage display

---

## Parameter Control Considerations

If adding parameter manipulation, note version/edition differences:

**Version (ID case):**
- Pianoteq 9: `"volume"`, `"dynamics"` (lowercase)
- Pianoteq 8: `"Volume"`, `"Dynamics"` (Capitalized)

**Edition (count):**
- Full/PRO: ~211 parameters (Steinway D)
- STAGE: ~93 parameters (Steinway D)

**Always call `getParameters()` first** - never hard-code parameter IDs.

---

## See Also

- [pianoteq-api.md](pianoteq-api.md) - Complete API reference
- [../src/pi_pianoteq/rpc/jsonrpc_client.py](../src/pi_pianoteq/rpc/jsonrpc_client.py) - JSON-RPC client implementation
- [../src/pi_pianoteq/lib/client_lib.py](../src/pi_pianoteq/lib/client_lib.py) - Client library using JSON-RPC
- [../CLAUDE.md](../CLAUDE.md) - Project development context
