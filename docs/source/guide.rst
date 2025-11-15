==================
Client Development
==================

This guide shows you how to create custom clients for pi-pianoteq.

Creating a Client
=================

Implement the ``Client`` Interface
-----------------------------------

Your client must implement four methods:

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class MyClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           """Initialize your client. API will be None during startup."""
           self.api = api

       def set_api(self, api: ClientApi):
           """Called when the API is ready. Store it for later use."""
           self.api = api

       def show_loading_message(self, message: str):
           """Display loading messages like 'Starting...' and 'Loading...'"""
           print(f"Loading: {message}")

       def start(self):
           """Main entry point. Start your event loop here."""
           while True:
               self.update_display()
               self.handle_input()

Two-Phase Initialization
=========================

Why Two Phases?
---------------

Pianoteq's JSON-RPC API takes time to initialize and load instruments (typically 6-8 seconds on a Raspberry Pi, faster on other hardware). During this startup:

1. Client created with ``api=None``
2. Loading messages shown via ``show_loading_message()``
3. Once the API is ready and instruments are loaded, ``set_api()`` called with the real API
4. Finally, ``start()`` called to begin normal operation

**Phase 1 - Loading Mode** (api=None):

.. code-block:: python

   client = MyClient(api=None)
   client.show_loading_message("Starting Pianoteq...")
   # Can't use API yet - just show loading screen

**Phase 2 - API Ready**:

.. code-block:: python

   client.set_api(client_lib)
   # API available - cache data if needed

**Phase 3 - Normal Operation**:

.. code-block:: python

   client.start()
   # Main loop - use API freely

Using the ClientApi
===================

The ``ClientApi`` provides all control methods you need.

Get Current State
-----------------

.. code-block:: python

   # Get current instrument
   instrument = self.api.get_current_instrument()
   print(instrument.name)  # e.g., "D4 Grand Piano"

   # Get current preset
   preset = self.api.get_current_preset()
   print(preset.display_name)  # e.g., "Classical"

Navigate Presets
----------------

.. code-block:: python

   # Next/previous preset
   self.api.set_preset_next()
   self.api.set_preset_prev()

   # Load specific preset
   self.api.set_preset("D4 Grand Piano", "D4 Grand Piano Classical")

Navigate Instruments
--------------------

.. code-block:: python

   # Next/previous instrument
   self.api.set_instrument_next()
   self.api.set_instrument_prev()

   # Switch to specific instrument
   self.api.set_instrument("D4 Grand Piano")

   # Get all instruments
   instruments = self.api.get_instruments()
   for inst in instruments:
       print(f"{inst.name} has {len(inst.presets)} presets")

Get Presets for an Instrument
------------------------------

.. code-block:: python

   # Get presets for current instrument
   instrument = self.api.get_current_instrument()
   presets = instrument.presets

   # Get presets for any instrument
   presets = self.api.get_presets("D4 Grand Piano")

Data Models
===========

Instrument
----------

.. code-block:: python

   instrument.name                  # "D4 Grand Piano"
   instrument.preset_prefix         # "D4"
   instrument.background_primary    # "#1e3a5f" (for UI theming)
   instrument.background_secondary  # "#0f1d2f"
   instrument.presets              # List of Preset objects

Preset
------

.. code-block:: python

   preset.name           # "D4 Grand Piano Classical" (full name)
   preset.display_name   # "Classical" (short name for display)

See :doc:`data-models` for complete details.

Complete Example
================

Here's a simple console client:

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class ConsoleClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           self.api = api
           self.running = False

       def set_api(self, api: ClientApi):
           self.api = api

       def show_loading_message(self, message: str):
           print(f"\n{'='*40}")
           print(f"  {message}")
           print(f"{'='*40}\n")

       def start(self):
           self.running = True
           self.show_help()

           while self.running:
               self.display_current()
               command = input("\nCommand (n/p/q): ").lower()

               if command == 'n':
                   self.api.set_preset_next()
               elif command == 'p':
                   self.api.set_preset_prev()
               elif command == 'q':
                   self.running = False

       def display_current(self):
           if self.api is None:
               return

           instrument = self.api.get_current_instrument()
           preset = self.api.get_current_preset()

           print(f"\nInstrument: {instrument.name}")
           print(f"Preset:     {preset.display_name}")

       def show_help(self):
           print("\nCommands:")
           print("  n - Next preset")
           print("  p - Previous preset")
           print("  q - Quit")

For a more complete example, see :doc:`example`.

Common Patterns
===============

Building a Menu
---------------

.. code-block:: python

   def show_instrument_menu(self):
       instruments = self.api.get_instruments()
       current = self.api.get_current_instrument()

       for i, inst in enumerate(instruments):
           marker = "→" if inst == current else " "
           print(f"{marker} {inst.name}")

Handling User Input
-------------------

.. code-block:: python

   def handle_button_press(self, button):
       if button == 'next':
           self.api.set_preset_next()
           self.update_display()
       elif button == 'prev':
           self.api.set_preset_prev()
           self.update_display()

Using Instrument Colors
-----------------------

For hardware with RGB LEDs:

.. code-block:: python

   instrument = self.api.get_current_instrument()
   color = instrument.background_primary  # e.g., "#1e3a5f"

   # Convert hex to RGB
   hex_color = color.lstrip('#')
   r = int(hex_color[0:2], 16)
   g = int(hex_color[2:4], 16)
   b = int(hex_color[4:6], 16)

   set_led_color(r, g, b)

Thread Safety
=============

The ClientApi is **not thread-safe**. If you use multiple threads:

**Option 1 (Recommended)**: Only call the API from one thread

.. code-block:: python

   def start(self):
       # All API calls from main thread
       while self.running:
           self.handle_input()  # Calls API
           self.update_display()  # Calls API

**Option 2**: Use locks

.. code-block:: python

   import threading

   def __init__(self, api):
       self.api = api
       self.api_lock = threading.Lock()

   def safe_next_preset(self):
       with self.api_lock:
           self.api.set_preset_next()

Next Steps
==========

- Study the :doc:`example` - Complete minimal client implementation
- Check the :doc:`api` - Full API reference
- Read the :doc:`data-models` - Instrument and Preset details
- Look at the source:

  - `GfxhatClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/gfxhat/gfxhat_client.py>`_ - Hardware client
  - `CliClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/cli/cli_client.py>`_ - Terminal client
