# Pianoteq JSON-RPC API - Implementation Notes

Implementation status for the pi-pianoteq project. For complete API documentation, see [pianoteq-api.md](pianoteq-api.md).

---

## Current API Usage

The project uses **4 out of 37+ available methods**, only for **discovery** during startup:

| Method | Usage | Location |
|--------|-------|----------|
| `getActivationInfo()` | Detect licensed vs trial | `jsonrpc_client.py:121`, `__main__.py:150` |
| `getListOfPresets()` | Discover available instruments | `jsonrpc_client.py:85`, `config.py:225` |
| `getInfo()` | Defined but unused | `jsonrpc_client.py:104` |
| `loadPreset()` | Defined but unused | `jsonrpc_client.py:154` |

**Runtime control uses MIDI:**
- Preset switching: MIDI Program Change → Pianoteq LoadPreset mapping (`.ptqmap` file)
- Parameters: MIDI CC messages (not currently used)

---

## Navigation

Prev/next buttons work via:
1. GFX HAT buttons trigger menu navigation
2. Menu sends MIDI Program Change
3. Pianoteq's mapping file translates to LoadPreset

No need for `nextPreset()` API calls - current implementation is simpler.

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
- [../src/pi_pianoteq/rpc/jsonrpc_client.py](../src/pi_pianoteq/rpc/jsonrpc_client.py) - Current implementation
- [../src/pi_pianoteq/mapping/mapping.py](../src/pi_pianoteq/mapping/mapping.py) - MIDI mapping for preset loading
- [../CLAUDE.md](../CLAUDE.md) - Project development context
