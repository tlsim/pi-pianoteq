====================
Data Models Reference
====================

This page documents the data models used in the pi-pianoteq client API.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
========

Pi-pianoteq uses two main data models:

- **Instrument**: Represents a Pianoteq instrument with its presets
- **Preset**: Represents an individual instrument preset

These are simple data classes that you receive from ClientApi methods.

Instrument
==========

.. autoclass:: pi_pianoteq.instrument.instrument.Instrument
   :members:
   :undoc-members:
   :show-inheritance:

Attributes
----------

name
~~~~

.. code-block:: python

   name: str

The full display name of the instrument.

**Examples**:

- ``"D4 Grand Piano"``
- ``"U4 Upright Piano"``
- ``"K2 Grand Piano"``
- ``"Steingraeber E-272"``

**Usage**:

.. code-block:: python

   instrument = api.get_current_instrument()
   print(f"Playing: {instrument.name}")

preset_prefix
~~~~~~~~~~~~~

.. code-block:: python

   preset_prefix: str

The short prefix used to identify this instrument's presets.

**Examples**:

- ``"D4"`` for "D4 Grand Piano"
- ``"U4"`` for "U4 Upright Piano"
- ``"K2"`` for "K2 Grand Piano"

**Purpose**: Used internally to group presets by instrument during discovery.

**Usage**:

.. code-block:: python

   instrument = api.get_current_instrument()
   print(f"Prefix: {instrument.preset_prefix}")

background_primary
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   background_primary: str

Hex color code for primary background/UI element.

**Format**: Hex color string (e.g., ``"#1e3a5f"``)

**Purpose**: Provides color theming for UIs. Different instruments have different colors.

**Usage**:

.. code-block:: python

   instrument = api.get_current_instrument()
   color = instrument.background_primary  # "#1e3a5f"

   # Convert to RGB for LED control
   hex_color = color.lstrip('#')
   r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
   set_led_color(r, g, b)

background_secondary
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   background_secondary: str

Hex color code for secondary background/UI element.

**Format**: Hex color string (e.g., ``"#0f1d2f"``)

**Purpose**: Provides secondary color for gradients or alternate UI elements.

**Usage**:

.. code-block:: python

   instrument = api.get_current_instrument()
   primary = instrument.background_primary
   secondary = instrument.background_secondary

   # Use for gradient background
   set_gradient(primary, secondary)

presets
~~~~~~~

.. code-block:: python

   presets: list[Preset]

List of all presets available for this instrument.

**Type**: List of :class:`Preset` objects

**Order**: Ordered as received from Pianoteq

**Usage**:

.. code-block:: python

   instrument = api.get_current_instrument()

   print(f"{instrument.name} has {len(instrument.presets)} presets:")
   for preset in instrument.presets:
       print(f"  - {preset.display_name}")

Methods
-------

add_preset(preset)
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_preset(self, preset: Preset):
       """Add a preset to this instrument."""

**Purpose**: Internal method used during instrument discovery.

**Note**: Client developers typically don't need to call this. Presets are added during system initialization.

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   instrument = api.get_current_instrument()

   print(f"Name: {instrument.name}")
   print(f"Prefix: {instrument.preset_prefix}")
   print(f"Presets: {len(instrument.presets)}")
   print(f"Colors: {instrument.background_primary}, {instrument.background_secondary}")

Iterating Presets
~~~~~~~~~~~~~~~~~

.. code-block:: python

   instrument = api.get_current_instrument()
   current_preset = api.get_current_preset()

   for preset in instrument.presets:
       marker = "→" if preset == current_preset else " "
       print(f"{marker} {preset.display_name}")

Using Colors for UI Theming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def update_display_colors(self):
       """Update display colors based on current instrument."""
       instrument = api.get_current_instrument()

       # Set RGB LED backlight
       primary_rgb = self.hex_to_rgb(instrument.background_primary)
       self.set_backlight_color(*primary_rgb)

       # Use for UI elements
       self.set_text_color(instrument.background_primary)
       self.set_background_color(instrument.background_secondary)

   def hex_to_rgb(self, hex_color):
       """Convert hex color to RGB tuple."""
       hex_color = hex_color.lstrip('#')
       return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

Building Instrument Menu
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def build_instrument_menu(self):
       """Build menu of all instruments."""
       instruments = api.get_instruments()
       current = api.get_current_instrument()

       menu = []
       for inst in instruments:
           menu.append({
               'name': inst.name,
               'preset_count': len(inst.presets),
               'color': inst.background_primary,
               'is_current': inst == current
           })

       return menu

Preset
======

.. autoclass:: pi_pianoteq.instrument.preset.Preset
   :members:
   :undoc-members:
   :show-inheritance:

Attributes
----------

name
~~~~

.. code-block:: python

   name: str

The full preset name as returned by Pianoteq.

**Examples**:

- ``"D4 Grand Piano Close Mic"``
- ``"D4 Grand Piano Classical Recording"``
- ``"U4 Upright Piano Soft"``

**Purpose**: The canonical identifier for the preset. Use this when calling :meth:`ClientApi.set_preset()`.

**Usage**:

.. code-block:: python

   preset = api.get_current_preset()
   print(f"Full name: {preset.name}")

   # Load this preset explicitly
   api.set_preset(instrument.name, preset.name)

display_name
~~~~~~~~~~~~

.. code-block:: python

   display_name: str

Formatted name for display, with common prefix removed.

**Examples**:

- ``"Close Mic"`` (from "D4 Grand Piano Close Mic")
- ``"Classical Recording"`` (from "D4 Grand Piano Classical Recording")
- ``"Soft"`` (from "U4 Upright Piano Soft")

**Purpose**: Shorter name suitable for small displays. Common prefixes are removed based on longest common word prefix algorithm.

**Usage**:

.. code-block:: python

   preset = api.get_current_preset()
   # Use display_name for UI
   self.display.text(preset.display_name)

**Note**: If display_name is not set during initialization, it defaults to the full ``name``.

midi_program_number
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   midi_program_number: Optional[int]

The MIDI program number for this preset.

**Type**: ``int`` or ``None``

**Range**: 0-127

**Purpose**: Used internally for MIDI Program Change messages. Set during preset discovery.

**Usage**:

.. code-block:: python

   preset = api.get_current_preset()
   if preset.has_midi_params():
       print(f"MIDI Program: {preset.midi_program_number}")

**Note**: Client developers rarely need to access this directly. The ClientApi handles MIDI communication.

midi_channel
~~~~~~~~~~~~

.. code-block:: python

   midi_channel: Optional[int]

The MIDI channel for this preset.

**Type**: ``int`` or ``None``

**Range**: 0-15 (MIDI channels 1-16)

**Purpose**: Used internally for MIDI Program Change messages. Set during preset discovery.

**Usage**:

.. code-block:: python

   preset = api.get_current_preset()
   if preset.has_midi_params():
       print(f"MIDI Channel: {preset.midi_channel + 1}")  # Display as 1-16

**Note**: Client developers rarely need to access this directly. The ClientApi handles MIDI communication.

Methods
-------

__init__(name, display_name)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def __init__(self, name: str, display_name: Optional[str] = None):
       """
       Create a Preset instance.

       Args:
           name: The full preset name from Pianoteq API
           display_name: The formatted name for display (computed during library construction)
       """

**Purpose**: Create a new Preset object.

**Note**: Client developers typically don't create Preset objects manually. They are created during system initialization.

has_midi_params()
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def has_midi_params(self) -> bool:
       """Check if MIDI parameters are set."""

**Returns**: ``True`` if both ``midi_program_number`` and ``midi_channel`` are set, ``False`` otherwise.

**Purpose**: Check if the preset has valid MIDI configuration.

**Usage**:

.. code-block:: python

   preset = api.get_current_preset()
   if preset.has_midi_params():
       print("Preset has MIDI configuration")
   else:
       print("Warning: Preset missing MIDI parameters")

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   preset = api.get_current_preset()

   print(f"Full name: {preset.name}")
   print(f"Display name: {preset.display_name}")
   print(f"MIDI: Program {preset.midi_program_number}, Channel {preset.midi_channel}")

Displaying Current Preset
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def update_display(self):
       """Update display with current preset."""
       preset = api.get_current_preset()

       # Use display_name for limited display space
       self.display.text(preset.display_name, y=20)
       self.display.show()

Building Preset Menu
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def build_preset_menu(self):
       """Build menu of presets for current instrument."""
       instrument = api.get_current_instrument()
       current_preset = api.get_current_preset()

       menu = []
       for i, preset in enumerate(instrument.presets):
           menu.append({
               'index': i,
               'name': preset.display_name,  # Short name for menu
               'full_name': preset.name,     # Full name for selection
               'is_current': preset == current_preset
           })

       return menu

Selecting Preset from Menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def select_preset(self, menu_index):
       """Select preset by menu index."""
       instrument = api.get_current_instrument()

       if 0 <= menu_index < len(instrument.presets):
           preset = instrument.presets[menu_index]
           # Use full name for API call
           api.set_preset(instrument.name, preset.name)

Comparing Presets
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def is_current_preset(self, preset):
       """Check if a preset is the current one."""
       current = api.get_current_preset()
       return preset == current

   # Usage in menu
   for preset in instrument.presets:
       if is_current_preset(preset):
           print(f"→ {preset.display_name}")
       else:
           print(f"  {preset.display_name}")

Working with Instrument and Preset Together
============================================

Finding a Preset
----------------

.. code-block:: python

   def find_preset(instrument_name, preset_name):
       """Find a preset by name."""
       presets = api.get_presets(instrument_name)
       for preset in presets:
           if preset.name == preset_name:
               return preset
       return None

Searching by Display Name
--------------------------

.. code-block:: python

   def search_presets(query):
       """Search presets by display name."""
       results = []
       for instrument in api.get_instruments():
           for preset in instrument.presets:
               if query.lower() in preset.display_name.lower():
                   results.append({
                       'instrument': instrument.name,
                       'preset': preset.display_name,
                       'full_preset_name': preset.name
                   })
       return results

Complete Navigation Example
----------------------------

.. code-block:: python

   class PresetBrowser:
       def __init__(self, api):
           self.api = api

       def show_current(self):
           """Display current instrument and preset."""
           instrument = self.api.get_current_instrument()
           preset = self.api.get_current_preset()

           print(f"\n{instrument.name}")
           print(f"  {preset.display_name}")
           print(f"  (Preset {instrument.presets.index(preset) + 1} of {len(instrument.presets)})")

       def list_all(self):
           """List all instruments and presets."""
           for instrument in self.api.get_instruments():
               print(f"\n{instrument.name} [{instrument.preset_prefix}]")
               print(f"  Color: {instrument.background_primary}")
               print(f"  Presets:")
               for preset in instrument.presets:
                   print(f"    - {preset.display_name}")

Data Model Notes
================

Immutability
------------

Both ``Instrument`` and ``Preset`` objects should be treated as **read-only** after initialization:

- Don't modify attributes directly
- Don't add/remove presets from instruments
- To change state, use ClientApi methods (``set_instrument()``, ``set_preset()``, etc.)

Identity
--------

Objects are compared by identity (reference equality):

.. code-block:: python

   current = api.get_current_instrument()
   all_instruments = api.get_instruments()

   # This checks if it's the same object
   if current in all_instruments:
       print("Found!")

Persistence
-----------

Instrument and Preset objects exist for the entire lifetime of the application. They are created during startup and don't change.

**Caching is safe**:

.. code-block:: python

   class MyClient(Client):
       def set_api(self, api):
           self.api = api
           # Safe to cache - won't change
           self.instruments = api.get_instruments()

See Also
========

- :doc:`client` - ClientApi methods that return these models
- :doc:`../guides/client-development` - Complete development guide
- :doc:`../examples/minimal-client` - Working example using these models
