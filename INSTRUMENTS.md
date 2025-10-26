# Customizing Instruments

Pi-Pianoteq uses an `instruments.json` file to define which Pianoteq instruments appear in the interface. You can customize this to match the instruments you own.

## Quick Start

### Step 1: See What You Have

```bash
python -m pi_pianoteq --show-instruments
```

This diagnostic tool shows:
- ✅ Which instruments are currently mapped to presets
- ❌ Unmapped presets you might want to add
- 💡 Suggested JSON snippets with auto-detected categories
- ⚠️ Unused instruments you can remove

**Example output:**
```
✓ MAPPED INSTRUMENTS:

  Grand K2 (prefix: "K2")
    └─ 12 preset(s) matched
       • K2 Classical
       • K2 Jazz
       ...

✗ UNMAPPED PRESETS:

  Likely "Ancient Greek Lyre" (3 preset(s)):
    • Ancient Greek Lyre - Dorian
    • Ancient Greek Lyre - Lydian
    ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUGGESTED ADDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add these to ~/.config/pi_pianoteq/instruments.json:

  {
    "name": "Ancient Greek Lyre",
    "preset_prefix": "Ancient Greek Lyre",
    "category": "historical"
  },
```

### Step 2: Initialize Template (Optional)

```bash
python -m pi_pianoteq --init-instruments
```

This creates `~/.config/pi_pianoteq/instruments.json` as a starting template containing all bundled instruments. You can then edit it to add/remove instruments based on the diagnostic report.

### Step 3: Edit and Restart

Edit `~/.config/pi_pianoteq/instruments.json` to customize, then restart pi_pianoteq for changes to take effect.

## File Location Priority

Instruments are loaded with the following priority:
1. **User config**: `~/.config/pi_pianoteq/instruments.json` (if exists)
2. **Bundled default**: Falls back to package default

User config persists across package upgrades.

## File Format

The `instruments.json` file is a JSON array of instrument objects:

```json
[
  {
    "name": "Grand C. Bechstein DG",
    "preset_prefix": "C. Bechstein DG",
    "category": "piano"
  },
  {
    "name": "Vintage Tines MKI",
    "preset_prefix": "MKI",
    "category": "electric-tines"
  }
]
```

### Required Fields

- **`name`**: Display name shown in the interface
- **`preset_prefix`**: String that must appear at the **start** of Pianoteq preset names to match this instrument

### Optional Fields

Choose **one** of these approaches for display backlight colors:

#### Easy Option - Use a Category

- **`category`**: One of the predefined color categories (see [Color Categories](#color-categories) below)

#### Advanced Option - Manual Colors

- **`background_primary`**: Hex color (`#RRGGBB`) for center LED zones
- **`background_secondary`**: Hex color (`#RRGGBB`) for edge LED zones

**Note:** Manual colors override category. If neither is specified, defaults to `category: "piano"`.

## Display Backlight

The GFX HAT has **6 RGB LED zones** behind the 128×64 LCD display that provide colored backlighting:

```
┌─────────────────────────────────────────────┐
│           128×64 LCD Display                │
├─────────────────────────────────────────────┤
│ [0]  [1]  [2]  [3]  [4]  [5]                │
│ SEC  PRI  PRI  PRI  PRI  SEC                │
└─────────────────────────────────────────────┘
```

**Layout:**
- **Zone 0** (left edge): Secondary color
- **Zones 1-4** (center): Primary color
- **Zone 5** (right edge): Secondary color

This creates a **horizontal gradient effect** blending from secondary (edges) → primary (center) → secondary (edges), matching the visual style of the Pianoteq interface.

## Color Categories

Instead of picking hex colors manually, use predefined categories that match the Pianoteq interface:

| Category | Description | Primary | Secondary | Visual Effect |
|----------|-------------|---------|-----------|---------------|
| `piano` | Modern grand/upright pianos | `#040404` | `#2e3234` | Nearly black → dark gray |
| `electric-tines` | Vintage Tines/Rhodes/Reeds | `#af2523` | `#1b1b1b` | Dark red → very dark |
| `electric-keys` | Clavinet, Pianet, Electra | `#cc481c` | `#ea673b` | Orange → bright orange |
| `vibraphone` | Vibraphone | `#735534` | `#a68454` | Brown → tan |
| `percussion-mallet` | Celesta, Glockenspiel, Kalimba | `#a67247` | `#bf814e` | Tan → light tan |
| `percussion-wood` | Marimba, Xylophone | `#732e1f` | `#959998` | Dark brown → gray |
| `percussion-metal` | Steel Drum, Hand Pan, etc. | `#382d2b` | `#6c2f1a` | Dark brown → maroon |
| `harpsichord` | Harpsichord | `#251310` | `#4d281b` | Very dark brown |
| `harp` | Concert Harp | `#743620` | `#b95d36` | Brown → light brown |
| `historical` | Historical pianos | `#33150f` | `#73422e` | Dark brown → brown |

All categories are designed to provide **visible backlight** (none use pure black `#000000` which would turn LEDs off).

## Preset Matching

Presets are matched to instruments using **case-sensitive prefix matching** at position 0:

### Matching Rules

✅ **Match Examples:**
- Preset "C. Bechstein DG Prelude" **matches** prefix "C. Bechstein DG"
- Preset "MKI Classic" **matches** prefix "MKI"

❌ **Non-Match Examples:**
- Preset "My C. Bechstein DG" does **NOT** match "C. Bechstein DG" (prefix not at start)
- Preset "c. bechstein dg" does **NOT** match "C. Bechstein DG" (case-sensitive)

### ⚠️ Critical: Order Matters!

The **first** matching instrument in the array wins. If you have overlapping prefixes, list more specific ones first:

```json
✅ CORRECT ORDER:
[
  {"name": "C. Bechstein DG", "preset_prefix": "C. Bechstein DG"},
  {"name": "C. Bechstein 1899", "preset_prefix": "C. Bechstein"}
]

❌ WRONG ORDER:
[
  {"name": "C. Bechstein 1899", "preset_prefix": "C. Bechstein"},
  {"name": "C. Bechstein DG", "preset_prefix": "C. Bechstein DG"}
]
```

In the wrong order, "C. Bechstein DG" presets would incorrectly match "C. Bechstein" first.

## Unmatched Presets

Presets that don't match any `preset_prefix` are **silently excluded** from the interface. Only instruments with at least one matched preset appear in the selector.

This means you can:
- Remove instruments you don't own (they won't appear if no presets match)
- Add instruments you do own (they'll appear when presets match)
- Organize instruments in your preferred order

Use `--show-instruments` to identify unmatched presets.

## Common Customization Examples

### Only Include Instruments You Own

```json
[
  {"name": "Grand K2", "preset_prefix": "K2", "category": "piano"},
  {"name": "Vintage Tines MKI", "preset_prefix": "MKI", "category": "electric-tines"}
]
```

### Reorder by Preference

```json
[
  {"name": "Vintage Tines MKI", "preset_prefix": "MKI", "category": "electric-tines"},
  {"name": "Grand K2", "preset_prefix": "K2", "category": "piano"},
  {"name": "Celesta", "preset_prefix": "Celesta", "category": "percussion-mallet"}
]
```

The first instrument will be selected when pi_pianoteq starts.

### Mix Categories and Manual Colors

```json
[
  {
    "name": "Grand K2",
    "preset_prefix": "K2",
    "category": "piano"
  },
  {
    "name": "Custom Electric",
    "preset_prefix": "Custom",
    "background_primary": "#ff0000",
    "background_secondary": "#00ff00"
  }
]
```

Manual colors override category, allowing you to use categories for most instruments while customizing specific ones.

## Troubleshooting

### My presets aren't appearing

1. Run `python -m pi_pianoteq --show-instruments` to see unmapped presets
2. Check that `preset_prefix` **exactly** matches the start of preset names (case-sensitive)
3. Check for overlapping prefixes - more specific ones must come first
4. Verify there are no typos in the JSON syntax

### Colors aren't working

1. Ensure colors are in `#RRGGBB` format (e.g., `#af2523`, not `af2523` or `#af25`)
2. For categories, use exact names: `"piano"` not `"Piano"` or `"PIANO"`
3. If colors are invalid, defaults will be used and a warning logged
4. Check that you're not using pure black `#000000` which turns LEDs off

### My custom file isn't loading

1. Verify it exists at `~/.config/pi_pianoteq/instruments.json`
2. Check JSON syntax with a validator (e.g., `python -m json.tool < instruments.json`)
3. Check pi_pianoteq logs for error messages
4. If the file has errors, pi_pianoteq will fall back to the bundled default and log warnings

### How do I find the right prefix?

1. Run `python -m pi_pianoteq --show-instruments`
2. Look at the "UNMAPPED PRESETS" section
3. The tool groups presets by likely prefix and suggests JSON to copy-paste
4. You can also check your Pianoteq preset names manually

## Advanced Topics

### Validation and Fallbacks

Pi-Pianoteq validates instruments.json with these rules:

- **Required fields missing**: Entry is skipped with a warning
- **Invalid category**: Falls back to default "piano" category
- **Invalid hex colors**: Replaced with defaults (`#040404`/`#2e3234`)
- **Malformed JSON**: Falls back to bundled default with error logging

This ensures the interface remains functional even with configuration errors.

### Priority Order for Colors

Colors are determined with this priority:

1. **Manual `background_primary`/`background_secondary`** (highest priority)
2. **Category colors** (if category specified)
3. **Default piano colors** `#040404`/`#2e3234` (if nothing specified)

### Logging

Pi-Pianoteq logs useful information about instruments loading:

```bash
# See which file is being used
INFO: Loading instruments from user config: /home/user/.config/pi_pianoteq/instruments.json

# Warnings for invalid entries
WARNING: Instrument 'Test' has invalid category 'invalid-category', using default
WARNING: Instrument at index 5 missing required field 'preset_prefix', skipping
```

Check logs if things aren't working as expected.

## See Also

- [README.md](README.md) - Main documentation
- [SYSTEMD.md](SYSTEMD.md) - Running as a service
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow
