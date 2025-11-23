===========
Data Models
===========

This page documents the ``Instrument`` and ``Preset`` objects you'll work with when creating a client.

Instrument
==========

Represents a Pianoteq instrument with its presets and UI colors.

Attributes
----------

name
~~~~

.. code-block:: python

   instrument.name  # "D4 Grand Piano"

The full display name of the instrument.

preset_prefix
~~~~~~~~~~~~~

.. code-block:: python

   instrument.preset_prefix  # "D4"

Short prefix used to group presets (usually the first part of the name).

background_primary
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   instrument.background_primary  # "#1e3a5f"

Hex color for primary UI elements (e.g., LED backlights, backgrounds).

background_secondary
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   instrument.background_secondary  # "#0f1d2f"

Hex color for secondary UI elements (e.g., gradients).

presets
~~~~~~~

.. code-block:: python

   instrument.presets  # List of Preset objects

List of all presets available for this instrument.

Example Usage
-------------

.. code-block:: python

   instrument = api.get_current_instrument()

   print(f"Name: {instrument.name}")
   print(f"Presets: {len(instrument.presets)}")

   # Use colors for RGB LED
   color = instrument.background_primary  # "#1e3a5f"
   hex_color = color.lstrip('#')
   r = int(hex_color[0:2], 16)
   g = int(hex_color[2:4], 16)
   b = int(hex_color[4:6], 16)
   set_led_rgb(r, g, b)

   # List all presets
   for preset in instrument.presets:
       print(f"  - {preset.display_name}")

Preset
======

Represents an instrument preset.

Attributes
----------

name
~~~~

.. code-block:: python

   preset.name  # "D4 Grand Piano Classical"

The full preset name as Pianoteq knows it. Use this when calling ``api.set_preset()``.

display_name
~~~~~~~~~~~~

.. code-block:: python

   preset.display_name  # "Classical"

Shortened name for display purposes (common prefix removed). Use this in your UI.

Example Usage
-------------

.. code-block:: python

   preset = api.get_current_preset()

   # Display the short name
   print(f"Playing: {preset.display_name}")

   # Load this preset explicitly
   api.set_preset(instrument.name, preset.name)

Working with Both
=================

Getting All Presets
-------------------

.. code-block:: python

   # Get presets for current instrument
   instrument = api.get_current_instrument()
   presets = instrument.presets

   # Get presets for specific instrument
   presets = api.get_presets("D4 Grand Piano")

Building a Menu
---------------

.. code-block:: python

   def show_preset_menu():
       instrument = api.get_current_instrument()
       current_preset = api.get_current_preset()

       print(f"Presets for {instrument.name}:")
       for i, preset in enumerate(instrument.presets, 1):
           marker = "→" if preset == current_preset else " "
           print(f"{marker} {i}. {preset.display_name}")

Comparing Objects
-----------------

You can use ``==`` to compare instruments and presets:

.. code-block:: python

   current_instrument = api.get_current_instrument()
   all_instruments = api.get_instruments()

   for inst in all_instruments:
       if inst == current_instrument:
           print(f"→ {inst.name} (current)")
       else:
           print(f"  {inst.name}")

Important Notes
===============

**Use display_name for UI**: Always show ``preset.display_name`` to users, not ``preset.name``.

**Use name for API calls**: When calling ``api.set_preset()``, use the full ``preset.name``.

**Objects are read-only**: Don't modify instrument or preset attributes directly. Use the API methods to change state.

**Objects are cached**: Instruments and presets are created at startup and don't change during runtime.

See Also
========

- :doc:`api` - API methods that return these objects
- :doc:`guide` - Using these models in your client
- :doc:`example` - Complete working example
