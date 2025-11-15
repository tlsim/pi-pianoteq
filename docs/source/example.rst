===============
Minimal Example
===============

This is a complete, working console client that demonstrates the essentials of creating a pi-pianoteq client.

Complete Source
===============

.. code-block:: python

   """
   minimal_client.py - Simple console client for pi-pianoteq

   Demonstrates:
   - Two-phase initialization
   - Using the ClientApi
   - Navigation and display
   """

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class MinimalClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           self.api = api
           self.running = False

       def set_api(self, api: ClientApi):
           """Store the API when it becomes available."""
           self.api = api

       def show_loading_message(self, message: str):
           """Display loading messages during startup."""
           print(f"\n{'='*50}")
           print(f"  {message}")
           print(f"{'='*50}\n")

       def start(self):
           """Main client loop."""
           self.running = True
           self.show_help()

           while self.running:
               self.display_current_state()
               self.handle_input()

       def display_current_state(self):
           """Show current instrument and preset."""
           if self.api is None:
               return

           instrument = self.api.get_current_instrument()
           preset = self.api.get_current_preset()

           print(f"\n{'-'*50}")
           print(f"Instrument: {instrument.name}")
           print(f"Preset:     {preset.display_name}")
           print(f"{'-'*50}")

       def handle_input(self):
           """Process user commands."""
           try:
               cmd = input("\nCommand: ").lower().strip()

               if cmd == 'n':
                   self.api.set_preset_next()
               elif cmd == 'p':
                   self.api.set_preset_prev()
               elif cmd == 'i':
                   self.show_instruments()
               elif cmd == 'q':
                   self.running = False
               else:
                   print(f"Unknown command: {cmd}")
                   self.show_help()

           except (KeyboardInterrupt, EOFError):
               print("\nExiting...")
               self.running = False

       def show_instruments(self):
           """Display all available instruments."""
           instruments = self.api.get_instruments()
           current = self.api.get_current_instrument()

           print(f"\n{'='*50}")
           print("Available Instruments")
           print(f"{'='*50}")

           for inst in instruments:
               marker = "→" if inst == current else " "
               print(f"{marker} {inst.name} ({len(inst.presets)} presets)")

       def show_help(self):
           """Show available commands."""
           print("\nCommands:")
           print("  n - Next preset")
           print("  p - Previous preset")
           print("  i - Show instruments")
           print("  q - Quit")

How It Works
============

Phase 1: Loading Mode
----------------------

.. code-block:: python

   client = MinimalClient(api=None)
   client.show_loading_message("Starting Pianoteq...")

The client is created without an API. Only ``show_loading_message()`` can be called.

Phase 2: API Ready
------------------

.. code-block:: python

   client.set_api(client_lib)

Once Pianoteq is ready, the API is provided via ``set_api()``.

Phase 3: Normal Operation
--------------------------

.. code-block:: python

   client.start()

The ``start()`` method begins the main loop, using the API to display state and handle input.

Key Points
==========

1. **Always check for None**: During loading, ``api`` is ``None``
2. **Use display_name**: For presets, use ``preset.display_name`` (not ``preset.name``)
3. **Handle errors gracefully**: Catch ``KeyboardInterrupt`` and ``EOFError``
4. **Keep it simple**: The core loop is just display + input + update

Extending This Example
======================

Add Preset Selection
--------------------

.. code-block:: python

   def select_preset(self):
       instrument = self.api.get_current_instrument()
       print(f"\nPresets for {instrument.name}:")

       for i, preset in enumerate(instrument.presets, 1):
           print(f"  {i}. {preset.display_name}")

       choice = int(input("\nSelect preset number: "))
       if 1 <= choice <= len(instrument.presets):
           preset = instrument.presets[choice - 1]
           self.api.set_preset(instrument.name, preset.name)

Add Instrument Colors
---------------------

.. code-block:: python

   def display_with_color(self):
       instrument = self.api.get_current_instrument()
       color = instrument.background_primary

       # For terminals that support ANSI colors
       hex_color = color.lstrip('#')
       r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

       print(f"\033[38;2;{r};{g};{b}m{instrument.name}\033[0m")

Next Steps
==========

- Read the :doc:`guide` for more patterns and best practices
- Check the :doc:`api` for all available methods
- Look at the real clients:

  - `GfxhatClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/gfxhat/gfxhat_client.py>`_ - Hardware display with buttons
  - `CliClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/cli/cli_client.py>`_ - Full-featured terminal interface
