# Pianoteq JSON-RPC API Reference

Comprehensive documentation of the Pianoteq JSON-RPC API, based on testing with Pianoteq 9.0.2 (trial) and Pianoteq 8.4.3 STAGE (licensed).

> **For pi-pianoteq implementation notes**, see [pianoteq-api-implementation.md](pianoteq-api-implementation.md)

## Overview

**Endpoint:** `http://localhost:8081/jsonrpc`
**Protocol:** JSON-RPC 2.0
**Availability:** Pianoteq 7.0+
**Requirement:** Pianoteq must be running with `--serve` flag

### Tested Versions
- **Pianoteq 9.0.2 Trial** (x86_64, Linux) - 37 methods
- **Pianoteq 8.4.3 STAGE** (arm64, Raspberry Pi 4B) - 38 methods (includes `activate`)

### Request Format
```json
{
  "jsonrpc": "2.0",
  "method": "methodName",
  "params": [] | {},
  "id": 1
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "result": <result_value>,
  "id": 1
}
```

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": <error_code>,
    "message": "<error_message>"
  },
  "id": 1
}
```

## Quick Reference

| Method | Category | Parameters | Returns | Description |
|--------|----------|------------|---------|-------------|
| `list` | System | None | Array of methods | Get list of available methods |
| `getInfo` | Info | None | Object | Get Pianoteq state and version info |
| `getPerfInfo` | Info | None | Object | Get CPU performance info |
| `getActivationInfo` | Info | None | Object | Get license/activation info |
| `getListOfPresets` | Presets | `preset_type="full"` | Array | List all presets |
| `loadPreset` | Presets | `name, bank="", preset_type="full"` | null | Load a preset |
| `savePreset` | Presets | `name, bank, preset_type="full"` | null | Save current preset |
| `deletePreset` | Presets | `name, bank, preset_type="full"` | null | Delete a preset file |
| `resetPreset` | Presets | None | null | Reset to saved preset |
| `nextPreset` | Navigation | None | null | Load next preset |
| `prevPreset` | Navigation | None | null | Load previous preset |
| `nextInstrument` | Navigation | None | null | Load next instrument |
| `prevInstrument` | Navigation | None | null | Load previous instrument |
| `abSwitch` | A/B | None | null | Switch between A and B presets |
| `abCopy` | A/B | None | null | Copy current preset to other slot |
| `getParameters` | Parameters | None | Array | Get all parameters with values |
| `setParameters` | Parameters | `list=[]` | null | Change parameter values |
| `randomizeParameters` | Parameters | `amount=1.0` | null | Randomize parameter values |
| `undo` | Edit | None | null | Undo last edit |
| `redo` | Edit | None | null | Redo last edit |
| `getMetronome` | Metronome | None | Object | Get metronome state |
| `setMetronome` | Metronome | `enabled, bpm, volume_db, timesig, accentuate` | null | Change metronome settings |
| `getSequencerInfo` | MIDI Sequencer | None | Object | Get sequencer state |
| `loadMidiFile` | MIDI Sequencer | `path` | null | Load MIDI file or playlist |
| `saveMidiFile` | MIDI Sequencer | `path` | null | Save current MIDI file |
| `midiPlay` | MIDI Sequencer | None | null | Play MIDI sequence |
| `midiStop` | MIDI Sequencer | None | null | Stop MIDI sequence |
| `midiPause` | MIDI Sequencer | None | null | Pause MIDI sequence |
| `midiRewind` | MIDI Sequencer | None | null | Rewind to start |
| `midiRecord` | MIDI Sequencer | None | null | Start recording |
| `midiSeek` | MIDI Sequencer | `seconds` | null | Seek to position |
| `midiSend` | MIDI | `bytes=[]` | null | Send raw MIDI bytes |
| `panic` | MIDI | None | null | Reset all MIDI state |
| `loadFile` | Files | `path` | null | Load any supported file |
| `getAudioDeviceInfo` | Audio | None | Object | Get current audio device info |
| `getListOfAudioDevices` | Audio | None | Array | List available audio devices |
| `activate` | System | `serial, device_name` | ? | Activate license (v8 only) |
| `quit` | System | None | null | Quit Pianoteq |

---

## Method Documentation

### System Methods

#### `list()`
Get the list of all available JSON-RPC methods.

**Parameters:** None

**Returns:** `Array<MethodInfo>`

**TypeScript Interface:**
```typescript
interface MethodInfo {
  name: string;        // Method name
  spec: string;        // Method signature
  doc: string;         // Documentation string
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "name": "getInfo",
      "spec": "getInfo()",
      "doc": "Return various informations about the current state of Pianoteq."
    },
    ...
  ],
  "id": 1
}
```

**Usage Notes:**
- Use this to discover available methods
- Documentation strings may be empty for some methods
- Method availability may vary by version

---

#### `quit()`
Immediately quit Pianoteq.

**Parameters:** None

**Returns:** `null`

**Warning:** This terminates the Pianoteq process immediately.

---

#### `activate(serial, device_name)` ⚠️ **Licensed Binaries Only**
Activate Pianoteq license.

**Parameters:**
- `serial` (string): License serial number
- `device_name` (string): Device name for activation

**Returns:** Unknown (not tested with valid credentials)

**Availability:**
- **Present in licensed binaries:** Pianoteq 8.4.3 STAGE (tested)
- **Not in trial binaries:** Pianoteq 9.0.2 Trial (returns "function not found: activate")
- **Likely present in v9 licensed binaries** (not tested)

**Error Response (Trial Binary):**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 1,
    "message": "function not found: activate"
  },
  "id": 1
}
```

---

### Information Methods

#### `getInfo()`
Get comprehensive information about the current state of Pianoteq.

**Parameters:** None

**Returns:** `Array<PianoteqInfo>` (single-element array)

**TypeScript Interface:**
```typescript
interface PianoteqInfo {
  version: string;                    // e.g., "9.0.2"
  product_name: string;               // e.g., "Pianoteq Trial", "Pianoteq STAGE"
  vendor_name: string;                // "Modartt"
  plugin_type: string;                // "sta" for standalone
  arch: string;                       // "x86", "arm"
  arch_bits: number;                  // 64
  build_date: string;                 // "20251020"
  modified: boolean;                  // Has current preset been modified?
  computing_parameter_update: boolean;// Is parameter update in progress?
  current_preset: CurrentPreset;
}

interface CurrentPreset {
  name: string;                       // Preset name
  instrument: string;                 // Instrument name
  author: string;                     // Preset author
  bank: string;                       // Bank name (empty for factory)
  comment: string;                    // Preset description
  mini_presets: {                     // Active mini-presets
    [type: string]: string;           // e.g., {"reverb": "Concert Hall"}
  };
}
```

**Example Response (Local - Trial):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "arch": "x86",
      "arch_bits": 64,
      "build_date": "20251020",
      "computing_parameter_update": false,
      "current_preset": {
        "author": "Modartt",
        "bank": "",
        "comment": "The default preset for the Kalimba, close to the original instrument.",
        "instrument": "Kalimba",
        "mini_presets": {},
        "name": "Kalimba Original"
      },
      "modified": false,
      "plugin_type": "sta",
      "product_name": "Pianoteq Trial",
      "vendor_name": "Modartt",
      "version": "9.0.2"
    }
  ],
  "id": 2
}
```

**Example Response (Pi - Licensed STAGE):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "arch": "arm",
      "arch_bits": 64,
      "build_date": "20250613",
      "computing_parameter_update": false,
      "current_preset": {
        "author": "Modartt",
        "bank": "",
        "comment": "This preset offers a combined micing perspective with a classical sound.",
        "instrument": "Grand Steinway D (New York)",
        "mini_presets": {
          "reverb": "Concert Hall"
        },
        "name": "NY Steinway D Classical"
      },
      "modified": false,
      "plugin_type": "sta",
      "product_name": "Pianoteq STAGE",
      "vendor_name": "Modartt",
      "version": "8.4.3"
    }
  ],
  "id": 2
}
```

---

#### `getPerfInfo()`
Get CPU performance and audio processing information.

**Parameters:** None

**Returns:** `Array<PerfInfo>` (single-element array)

**TypeScript Interface:**
```typescript
interface PerfInfo {
  counter: number;                    // Sample counter
  polyphony: number;                  // Current polyphony (active voices)
  cpu_overload: boolean;              // Is CPU overloaded?
  audio_buffer: number[];             // Buffer sizes (3 values)
  audio_load: number[];               // Audio load per buffer (32 values, 0.0-1.0)
  perf_index: number[];               // Performance index (32 values)
}
```

**Example Response (Local):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "audio_buffer": [512, 512, 512],
      "audio_load": [0.0021730447188019753, 0.000928856257814914, ...],
      "counter": 128,
      "cpu_overload": false,
      "perf_index": [0.0, 0.0, ...],
      "polyphony": 0
    }
  ],
  "id": 3
}
```

**Example Response (Pi):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "audio_buffer": [256, 256, 256],
      "audio_load": [0.0057581509463489056, 0.01014455035328865, ...],
      "counter": 1422,
      "cpu_overload": false,
      "perf_index": [0.0, 0.0, ...],
      "polyphony": 0
    }
  ],
  "id": 3
}
```

**Usage Notes:**
- `polyphony: 0` when no notes playing
- `audio_load` values are normalized (0.0 = 0%, 1.0 = 100%)
- Buffer size differs by platform (512 on desktop, 256 on Pi)

---

#### `getActivationInfo()`
Get license and activation information.

**Parameters:** None

**Returns:** `Array<ActivationInfo>` (single-element array)

**TypeScript Interface:**
```typescript
interface ActivationInfo {
  error_msg: string;                  // "Demo" for trial, "" for licensed
  addons: string[];                   // List of licensed addons
  // Licensed-only fields:
  name?: string;                      // License holder name
  email?: string;                     // License holder email
  hwname?: string;                    // Hardware name
  status?: number;                    // Status code (1 = active)
}
```

**Example Response (Local - Trial):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "addons": [],
      "error_msg": "Demo"
    }
  ],
  "id": 4
}
```

**Example Response (Pi - Licensed STAGE):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "addons": ["BechsteinDG", "Electric", "Hohner", "Steinway D", "K2", ""],
      "email": "user@example.com",
      "error_msg": "",
      "hwname": "raspberrypi",
      "name": "License Holder",
      "status": 1
    }
  ],
  "id": 4
}
```

**License Detection:**
- **Trial/Demo:** `error_msg == "Demo"`, `addons` is empty
- **Licensed:** `error_msg == ""`, `addons` contains instrument packs

---

### Preset Methods

#### `getListOfPresets(preset_type="full")`
Get list of all available presets.

**Parameters:**
- `preset_type` (string, optional): Type of presets to list
  - `"full"` (default): Full instrument presets
  - `"vel"`: Velocity mini-presets
  - `"mic"`: Microphone mini-presets
  - `"equ"`: Equalizer mini-presets
  - `"reverb"`: Reverb mini-presets
  - `"tuning"`: Tuning mini-presets
  - `"effect_rack"`: Effect rack mini-presets
  - `"effect1"`, `"effect2"`, `"effect3"`: Individual effect mini-presets

**Returns:** `Array<PresetInfo>`

**TypeScript Interface:**
```typescript
// Full presets (preset_type="full")
interface PresetInfo {
  name: string;                       // Preset name
  instr: string;                      // Instrument name (authoritative)
  class: string;                      // Instrument class
  collection: string;                 // Collection name
  license: string;                    // License name
  license_status: "ok" | "demo";      // License status
  author: string;                     // Preset author
  bank: string;                       // Bank name (empty for factory)
  comment: string;                    // Preset description
  file: string;                       // File path or "(builtin)"
}

// Mini-presets (other preset_type values)
interface MiniPresetInfo {
  name: string;                       // Mini-preset name
  author: string;                     // Author
  bank: string;                       // Bank name
  comment: string;                    // Description
  file: string;                       // File path or "(builtin)"
}
```

**Example Response (Full Presets - Local):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "author": "Modartt",
      "bank": "",
      "class": "Acoustic Piano",
      "collection": "Acoustic Piano",
      "comment": "This preset offers a combined micing perspective with a classical sound.",
      "file": "(builtin)",
      "instr": "Grand Steinway D (New York)",
      "license": "Steinway D",
      "license_status": "demo",
      "name": "NY Steinway D Classical"
    },
    ...
  ]
}
```

**Example Response (Velocity Mini-Presets):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "author": "Copyright (c) 2025 Modartt",
      "bank": "",
      "comment": "",
      "file": "(builtin)",
      "name": "Slow keyboard"
    },
    ...
  ]
}
```

**Usage Notes:**
- Local (trial): 719 full presets
- Pi (licensed STAGE): 667 full presets
- Use `instr` field for grouping by instrument (most reliable)
- `license_status`: `"ok"` (licensed) or `"demo"` (trial/unavailable)

---

#### `loadPreset(name, bank="", preset_type="full")`
Load the specified preset.

**Parameters:**
- `name` (string): Preset name
- `bank` (string, optional): Bank name (default: `""` for factory presets)
- `preset_type` (string, optional): Preset type (default: `"full"`)
  - Valid values: `full`, `equ`, `vel`, `mic`, `reverb`, `tuning`, `effect_rack`, `effect1`, `effect2`, `effect3`

**Returns:** `null`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "loadPreset",
  "params": ["Kalimba Original", ""],
  "id": 1
}
```

**Example Request (Mini-Preset):**
```json
{
  "jsonrpc": "2.0",
  "method": "loadPreset",
  "params": ["Slow keyboard", "", "vel"],
  "id": 1
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": null,
  "id": 1
}
```

**Usage Notes:**
- Loading a full preset changes the entire instrument
- Loading a mini-preset only changes that aspect (e.g., velocity curve, reverb)
- Use empty string `""` for `bank` parameter for factory presets

---

#### `savePreset(name, bank, preset_type="full")`
Save the current preset.

**Parameters:**
- `name` (string): Preset name
- `bank` (string): Bank name (required, use "My Presets" for user presets)
- `preset_type` (string, optional): Preset type (default: `"full"`)

**Returns:** `null`

**Usage Notes:**
- Saves to disk in Pianoteq's preset directory
- Cannot overwrite factory presets (empty bank)
- Use "My Presets" bank for user presets

---

#### `deletePreset(name, bank, preset_type="full")`
Delete a preset (removes file from disk).

**Parameters:**
- `name` (string): Preset name
- `bank` (string): Bank name
- `preset_type` (string, optional): Preset type (default: `"full"`)

**Returns:** `null`

**Warning:** Permanently deletes the preset file. Cannot delete factory presets.

---

#### `resetPreset()`
Reset all parameters to the saved preset state.

**Parameters:** None

**Returns:** `null`

**Usage Notes:**
- Discards all unsaved parameter changes
- Reloads the preset from disk/memory

---

### Navigation Methods

#### `nextPreset()`
Load the next preset in the list.

**Parameters:** None
**Returns:** `null`

---

#### `prevPreset()`
Load the previous preset in the list.

**Parameters:** None
**Returns:** `null`

---

#### `nextInstrument()`
Load the next instrument (skips presets within same instrument).

**Parameters:** None
**Returns:** `null`

---

#### `prevInstrument()`
Load the previous instrument.

**Parameters:** None
**Returns:** `null`

---

### A/B Preset Methods

#### `abSwitch()`
Switch between A and B preset slots.

**Parameters:** None
**Returns:** `null`

**Usage Notes:**
- Pianoteq maintains two preset slots (A and B)
- Switches instantly between them
- Useful for comparing presets or live performance

---

#### `abCopy()`
Copy current preset to the other slot.

**Parameters:** None
**Returns:** `null`

**Usage Notes:**
- If on slot A, copies A → B
- If on slot B, copies B → A

---

### Edit Methods

#### `undo()`
Undo the last parameter edit.

**Parameters:** None
**Returns:** `null`

---

#### `redo()`
Redo the last undone edit.

**Parameters:** None
**Returns:** `null`

---

### Parameter Methods

#### `getParameters()`
Get all parameters with their current values.

**Parameters:** None

**Returns:** `Array<Parameter>`

**TypeScript Interface:**
```typescript
interface Parameter {
  id: string;                         // Parameter identifier
  name: string;                       // Display name
  index: number;                      // Parameter index
  normalized_value: number;           // Normalized value (0.0 - 1.0)
  text: string;                       // Formatted text value
  unit: string;                       // Unit (e.g., "dB", "")
}
```

**Example Response (Local - 211 parameters):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "id": "condition",
      "index": 0,
      "name": "Condition",
      "normalized_value": 0.0,
      "text": "0",
      "unit": ""
    },
    {
      "id": "dynamics",
      "index": 1,
      "name": "Dynamics",
      "normalized_value": 0.39393940567970276,
      "text": "40",
      "unit": "dB"
    },
    {
      "id": "volume",
      "index": 2,
      "name": "Volume",
      "normalized_value": 0.7272727489471436,
      "text": "0",
      "unit": "dB"
    },
    ...
  ]
}
```

**Example Response (Pi - 93 parameters):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "id": "Condition",
      "index": 0,
      "name": "Condition",
      "normalized_value": 0.0,
      "text": "0",
      "unit": ""
    },
    ...
  ]
}
```

**Version/Product Differences:**
- **Parameter ID case differs by Pianoteq version:**
  - **Pianoteq 9:** lowercase IDs (`"volume"`, `"condition"`, `"velocity_offset"`)
  - **Pianoteq 8:** Capitalized IDs (`"Volume"`, `"Condition"`, `"Post Effect Gain"`)
- **Parameter count differs by product edition:**
  - **Pianoteq 9 Trial (full edition):** 211 parameters for Steinway D
  - **Pianoteq 8 STAGE (simplified):** 93 parameters for Steinway D
  - STAGE versions have fewer parameters (no advanced physical modeling controls)

---

#### `setParameters(list=[])`
Change values for one or more parameters.

**Parameters:**
- `list` (array): Array of parameter updates

**TypeScript Interface:**
```typescript
interface ParameterUpdate {
  id: string;                         // Parameter ID (required)
  normalized_value?: number;          // Set normalized value (0.0 - 1.0)
  text?: string;                      // Set text value (e.g., "-5")
  // Note: Provide either normalized_value OR text, not both
}
```

**Returns:** `null`

**Example Request (Normalized Value):**
```json
{
  "jsonrpc": "2.0",
  "method": "setParameters",
  "params": {
    "list": [
      {"id": "volume", "normalized_value": 0.5}
    ]
  },
  "id": 1
}
```

**Example Request (Text Value):**
```json
{
  "jsonrpc": "2.0",
  "method": "setParameters",
  "params": {
    "list": [
      {"id": "Volume", "text": "-5"}
    ]
  },
  "id": 1
}
```

**Example Request (Multiple Parameters):**
```json
{
  "jsonrpc": "2.0",
  "method": "setParameters",
  "params": {
    "list": [
      {"id": "volume", "normalized_value": 0.5},
      {"id": "dynamics", "text": "50"}
    ]
  },
  "id": 1
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": null,
  "id": 1
}
```

**Usage Notes:**
- **Parameter IDs are case-sensitive** and vary by version
- Use `normalized_value` (0.0-1.0) for precise control
- Use `text` for human-readable values (e.g., "-5 dB" → `"-5"`)
- Changes are immediate and can be undone with `undo()`
- Omit `index`, `name`, `unit` fields - only `id` and value needed

---

#### `randomizeParameters(amount=1.0)`
Randomize parameter values (like the "Random" button).

**Parameters:**
- `amount` (float, optional): Randomization amount (0.0 - 1.0, default: 1.0)
  - `0.0`: No change
  - `1.0`: Maximum randomization

**Returns:** `null`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "randomizeParameters",
  "params": [0.1],
  "id": 1
}
```

**Usage Notes:**
- Useful for exploring sound variations
- Can be undone with `undo()`
- Lower amounts produce subtler variations

---

### Metronome Methods

#### `getMetronome()`
Get the current metronome state.

**Parameters:** None

**Returns:** `Array<MetronomeState>` (single-element array)

**TypeScript Interface:**
```typescript
interface MetronomeState {
  enabled: boolean;                   // Is metronome on?
  bpm: number;                        // Beats per minute
  volume_db: number;                  // Volume in dB
  timesig: string;                    // Time signature (e.g., "4/4", "3/4")
  accentuate: boolean;                // Accentuate first beat?
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "accentuate": true,
      "bpm": 120.0,
      "enabled": false,
      "timesig": "4/4",
      "volume_db": 0.0
    }
  ],
  "id": 5
}
```

---

#### `setMetronome(enabled=null, bpm=null, volume_db=null, timesig=null, accentuate=null)`
Change metronome settings.

**Parameters:** (all optional, only provide what you want to change)
- `enabled` (boolean): Enable/disable metronome
- `bpm` (number): Beats per minute
- `volume_db` (number): Volume in dB
- `timesig` (string): Time signature (e.g., `"3/4"`, `"4/4"`)
- `accentuate` (boolean): Accentuate first beat

**Returns:** `null`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "setMetronome",
  "params": {
    "enabled": true,
    "bpm": 90,
    "timesig": "3/4"
  },
  "id": 1
}
```

**Usage Notes:**
- All parameters are optional - only specify what you want to change
- Changes are immediate

---

### MIDI Sequencer Methods

#### `getSequencerInfo()`
Get the current MIDI sequencer state.

**Parameters:** None

**Returns:** `Array<SequencerInfo>` (single-element array)

**TypeScript Interface:**
```typescript
interface SequencerInfo {
  name: string;                       // Sequence name
  description: string;                // Sequence description
  path: string;                       // File path or "(builtin)"
  duration: number;                   // Total duration in seconds
  position: number;                   // Current position in seconds
  playback_speed: number;             // Playback speed multiplier
  is_playing: boolean;                // Is currently playing?
  is_paused: boolean;                 // Is paused?
  is_recording: boolean;              // Is recording?
}
```

**Example Response (Not Playing):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "description": "kalimba-mini-demo",
      "duration": 9.26770833482345,
      "is_paused": false,
      "is_playing": false,
      "is_recording": false,
      "name": "Preset demo",
      "path": "(builtin)",
      "playback_speed": 1.0,
      "position": 0.0
    }
  ],
  "id": 6
}
```

**Example Response (Playing):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "description": "kalimba-mini-demo",
      "duration": 9.26770833482345,
      "is_paused": false,
      "is_playing": true,
      "is_recording": false,
      "name": "Preset demo",
      "path": "(builtin)",
      "playback_speed": 1.0,
      "position": 1.195827642455697
    }
  ],
  "id": 26
}
```

**Usage Notes:**
- Each preset has a built-in demo MIDI file
- `position` updates in real-time during playback

---

#### `loadMidiFile(path)`
Load a MIDI file or playlist.

**Parameters:**
- `path` (string): File path to MIDI file
  - Can be a file path (loads single file)
  - Can be a folder path (loads as playlist)
  - Can be array of strings (loads multiple files as playlist)

**Returns:** `null`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "loadMidiFile",
  "params": ["/path/to/song.mid"],
  "id": 1
}
```

---

#### `saveMidiFile(path)`
Save the currently loaded MIDI file.

**Parameters:**
- `path` (string): Destination file path

**Returns:** `null`

---

#### `midiPlay()`
Start playing the loaded MIDI sequence.

**Parameters:** None
**Returns:** `null`

---

#### `midiStop()`
Stop MIDI playback.

**Parameters:** None
**Returns:** `null`

**Usage Notes:**
- Stops playback and resets position to 0

---

#### `midiPause()`
Pause MIDI playback.

**Parameters:** None
**Returns:** `null`

**Usage Notes:**
- Pauses at current position (use `midiPlay()` to resume)

---

#### `midiRewind()`
Rewind to the start of the sequence.

**Parameters:** None
**Returns:** `null`

---

#### `midiRecord()`
Start recording MIDI input.

**Parameters:** None
**Returns:** `null`

---

#### `midiSeek(seconds)`
Seek to a specific position in the sequence.

**Parameters:**
- `seconds` (number): Position in seconds

**Returns:** `null`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "midiSeek",
  "params": [5.0],
  "id": 1
}
```

---

### MIDI Control Methods

#### `midiSend(bytes=[])`
Send raw MIDI bytes to the Pianoteq engine.

**Parameters:**
- `bytes` (array of numbers): MIDI message bytes

**Returns:** `null`

**TypeScript Interface:**
```typescript
// Example: Note On for C4 (middle C), velocity 100
{
  "bytes": [144, 60, 100]  // [status_byte, note, velocity]
}

// Example: Note Off for C4
{
  "bytes": [128, 60, 0]    // [status_byte, note, velocity]
}
```

**Example Request (Note On):**
```json
{
  "jsonrpc": "2.0",
  "method": "midiSend",
  "params": {
    "bytes": [144, 60, 100]
  },
  "id": 1
}
```

**Example Request (Note Off):**
```json
{
  "jsonrpc": "2.0",
  "method": "midiSend",
  "params": {
    "bytes": [128, 60, 0]
  },
  "id": 1
}
```

**MIDI Status Bytes:**
- `144` (0x90): Note On (channel 1)
- `128` (0x80): Note Off (channel 1)
- `192` (0xC0): Program Change (channel 1)
- `176` (0xB0): Control Change (channel 1)

**Usage Notes:**
- Send raw MIDI messages directly to engine
- Useful for note triggering, program changes, CC messages
- Parameter format: flat array of bytes `[144, 60, 100]`
- No response indicates success

---

#### `panic()`
Reset all MIDI state (stop all notes).

**Parameters:** None
**Returns:** `null`

**Usage Notes:**
- Immediately stops all playing notes
- Resets all MIDI controllers
- Useful for recovering from stuck notes

---

### File Methods

#### `loadFile(path)`
Load any supported file type.

**Parameters:**
- `path` (string): File path

**Returns:** `null`

**Supported File Types** (per API documentation, not exhaustively tested):
- `.fxp` - VST preset
- `.mfxp` - Pianoteq preset
- `.scl` - Scala tuning file
- `.kbm` - Keyboard mapping
- `.ptq` - Pianoteq file
- `.wav` - Audio file
- `.mid` - MIDI file (see also `loadMidiFile()`)

**Usage Notes:**
- File types listed are from Pianoteq's `list()` API response
- For MIDI files specifically, `loadMidiFile()` may be more appropriate

---

### Audio Device Methods

#### `getAudioDeviceInfo()`
Get information about the current audio device.

**Parameters:** None

**Returns:** `Object<AudioDeviceInfo>`

**TypeScript Interface:**
```typescript
interface AudioDeviceInfo {
  device_type: string;                // "ALSA", "JACK", etc.
  audio_output_device_name: string;   // Device name
  status: string;                     // "running", etc.
  sample_rate: string;                // Sample rate (e.g., "44100.0")
  buffer_size: string;                // Buffer size (e.g., "512")
  channels: string;                   // Channel configuration
  force_stereo: string;               // "0" or "1"
}
```

**Example Response (Local):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "audio_output_device_name": "Default ALSA Output (currently PipeWire Media Server)",
    "buffer_size": "512",
    "channels": "",
    "device_type": "ALSA",
    "force_stereo": "0",
    "sample_rate": "44100.0",
    "status": "running"
  },
  "id": 7
}
```

**Example Response (Pi):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "audio_output_device_name": "USB Audio CODEC, USB Audio; Direct hardware device without any conversions",
    "buffer_size": "256",
    "channels": "",
    "device_type": "ALSA",
    "force_stereo": "0",
    "sample_rate": "44100.0",
    "status": "running"
  },
  "id": 7
}
```

---

#### `getListOfAudioDevices()`
Get list of all available audio devices.

**Parameters:** None

**Returns:** `Array<AudioDeviceList>`

**TypeScript Interface:**
```typescript
interface AudioDeviceList {
  type: string;                       // "ALSA", "JACK", etc.
  devices: string[];                  // Array of device names
}
```

**Example Response (abbreviated):**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "type": "ALSA",
      "devices": [
        "Default ALSA Output (currently PipeWire Media Server)",
        "PipeWire Sound Server",
        "USB Audio CODEC, USB Audio; Front output / input",
        ...
      ]
    },
    {
      "type": "JACK",
      "devices": [
        "Auto-connect ON",
        "Auto-connect OFF"
      ]
    }
  ],
  "id": 8
}
```

---

## Version Differences

### Pianoteq 9.0.2 Trial vs 8.4.3 STAGE

| Feature | Pianoteq 9 Trial | Pianoteq 8 STAGE | Notes |
|---------|------------------|------------------|-------|
| **Total Methods** | 37 | 38 | Licensed binary has `activate()` |
| **Parameter IDs** | lowercase | Capitalized | `"volume"` vs `"Volume"` |
| **Parameter Count** | 211 (Steinway D) | 93 (Steinway D) | STAGE has fewer parameters |
| **Full Presets** | 719 (trial) | 667 (licensed) | Varies by license status |
| **preset_type values** | Includes `--invalid--` | No `--invalid--` | Documentation difference only |

### Trial vs Licensed Binary Methods
- `activate(serial, device_name)` - **Only in licensed binaries** (not trial)
  - Returns error "function not found: activate" when called on trial binary
  - Present in v8 STAGE (licensed) but not v9 Trial
  - Likely available in v9 licensed binaries (not tested)

### Product Edition Differences
- **Full/PRO editions:** ~211 parameters per instrument (includes advanced physical modeling)
- **STAGE editions:** ~93 parameters per instrument (simplified interface, essential controls only)
- Parameter count tested with Steinway D preset on both systems

---

## License Impact on API Responses

### Trial/Demo vs Licensed

#### `getActivationInfo()`
**Trial:**
```json
{
  "error_msg": "Demo",
  "addons": []
}
```

**Licensed:**
```json
{
  "error_msg": "",
  "addons": ["BechsteinDG", "Electric", ...],
  "name": "License Holder",
  "email": "user@example.com",
  "hwname": "device-name",
  "status": 1
}
```

#### `getListOfPresets()`
**Trial:**
- 719 presets (all instruments available but with demo limitations)
- `license_status: "demo"` for all presets

**Licensed STAGE:**
- 667 presets (only licensed instruments)
- `license_status: "ok"` for licensed instruments

#### `getInfo()`
**Trial:**
```json
{
  "product_name": "Pianoteq Trial"
}
```

**Licensed:**
```json
{
  "product_name": "Pianoteq STAGE"
}
```

---

## Error Handling

### Common Errors

#### Type Error (Wrong Parameter Format)
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 1,
    "message": "[json.exception.type_error.302] type must be number, but is array"
  },
  "id": 22
}
```

**Cause:** Incorrect parameter format (e.g., nested array instead of flat array for `midiSend`)

#### Connection Error
**Symptom:** Request timeout or connection refused

**Causes:**
- Pianoteq not running
- Pianoteq not started with `--serve` flag
- Firewall blocking port 8081

---

## Usage Examples

### Python

```python
import requests
import json

def rpc_call(method, params=None):
    """Make a JSON-RPC call to Pianoteq."""
    if params is None:
        params = []

    url = 'http://localhost:8081/jsonrpc'
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    response = requests.post(url, json=payload)
    return response.json()

# Get Pianoteq version
info = rpc_call('getInfo')
print(f"Version: {info['result'][0]['version']}")

# Load a preset
rpc_call('loadPreset', ['NY Steinway D Classical', ''])

# Change volume
rpc_call('setParameters', {'list': [{'id': 'volume', 'normalized_value': 0.5}]})

# Play a note
rpc_call('midiSend', {'bytes': [144, 60, 100]})  # Note on
import time
time.sleep(0.5)
rpc_call('midiSend', {'bytes': [128, 60, 0]})    # Note off
```

### cURL

```bash
# Get list of methods
curl -s http://localhost:8081/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"list","params":[],"id":1}'

# Get current state
curl -s http://localhost:8081/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getInfo","params":[],"id":1}'

# Load preset
curl -s http://localhost:8081/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"loadPreset","params":["Kalimba Original",""],"id":1}'

# Set parameter by text value
curl -s http://localhost:8081/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"setParameters","params":{"list":[{"id":"volume","text":"-5"}]},"id":1}'
```

### JavaScript/Node.js

```javascript
async function rpcCall(method, params = []) {
  const response = await fetch('http://localhost:8081/jsonrpc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: method,
      params: params,
      id: 1
    })
  });
  return await response.json();
}

// Usage
const info = await rpcCall('getInfo');
console.log(`Version: ${info.result[0].version}`);

await rpcCall('loadPreset', ['Kalimba Original', '']);
await rpcCall('setParameters', {list: [{id: 'volume', normalized_value: 0.5}]});
```

---

## Best Practices

### Parameter Manipulation
1. **Always call `getParameters()` first** to discover available parameter IDs and count
2. **Parameter IDs are version-specific:** v9 uses lowercase, v8 uses Capitalized
3. **Parameter count is edition-specific:** Full/PRO (~211), STAGE (~93)
4. **Prefer `normalized_value`** for programmatic control (0.0-1.0)
5. **Use `text`** for human-readable values

### Preset Loading
1. **Use `instr` field** from `getListOfPresets()` for grouping by instrument
2. **Check `license_status`** before loading (avoid "demo" if licensed version available)
3. **Use empty string `""`** for `bank` parameter when loading factory presets

### MIDI Control
1. **Always send note-off** messages to avoid stuck notes
2. **Use `panic()`** to recover from MIDI errors or stuck notes

### Error Recovery
1. **Check Pianoteq is running** with `--serve` flag
2. **Handle connection timeouts** gracefully
3. **Validate parameter IDs** match your Pianoteq version

---

## Testing Methodology

This documentation was created by:
1. Calling `list()` on both Pianoteq 9.0.2 (local) and 8.4.3 (Pi)
2. Systematically testing all 37 methods with various parameters
3. Comparing responses between trial and licensed versions
4. Testing same instrument (Steinway D) on both systems to isolate version/edition differences
5. Testing edge cases and error conditions
6. Documenting actual JSON responses verbatim

All examples are real responses from live Pianoteq instances.

---

## References

- **Pianoteq JSON-RPC Endpoint:** `http://localhost:8081/jsonrpc`
- **JSON-RPC 2.0 Specification:** https://www.jsonrpc.org/specification
- **Pianoteq Website:** https://www.modartt.com/pianoteq

---

## See Also

- [pianoteq-api-implementation.md](pianoteq-api-implementation.md) - Implementation notes for pi-pianoteq project
- [../src/pi_pianoteq/rpc/jsonrpc_client.py](../src/pi_pianoteq/rpc/jsonrpc_client.py) - Current client implementation
- [../CLAUDE.md](../CLAUDE.md) - Project development context

---

**Document Version:** 1.0
**Last Updated:** 2025-01-09
**Tested Versions:** Pianoteq 9.0.2 (Trial), Pianoteq 8.4.3 STAGE (Licensed)
