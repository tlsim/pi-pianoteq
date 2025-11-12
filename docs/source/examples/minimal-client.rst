============================
Minimal Example Client
============================

This is a complete, working minimal client implementation that demonstrates the essential concepts for creating a pi-pianoteq client.

This example implements a simple console-based client that:

- Shows loading messages during startup
- Displays the current instrument and preset
- Accepts keyboard commands to navigate
- Demonstrates two-phase initialization

Complete Source Code
=====================

.. code-block:: python

   """
   minimal_client.py - Minimal pi-pianoteq client example

   This demonstrates the essential structure of a pi-pianoteq client.
   It's a simple console-based interface with keyboard navigation.

   Usage:
       1. Copy this file to your pi-pianoteq project
       2. Register it in __main__.py (see "Registering Your Client" below)
       3. Run: pipenv run pi-pianoteq --minimal
   """

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional
   import sys
   import threading
   import logging

   logger = logging.getLogger(__name__)


   class MinimalClient(Client):
       """
       Minimal console-based client for pi-pianoteq.

       Demonstrates two-phase initialization and basic ClientApi usage.
       """

       def __init__(self, api: Optional[ClientApi]):
           """
           Initialize the client.

           Args:
               api: The ClientApi instance, or None during loading phase
           """
           self.api = api
           self.running = False

       def set_api(self, api: ClientApi):
           """
           Receive the ClientApi after initialization.

           Called once instruments are discovered and ClientLib is ready.

           Args:
               api: The ClientApi instance
           """
           logger.info("API provided, instruments loaded")
           self.api = api

           # Optionally pre-fetch data for menus
           instruments = api.get_instruments()
           logger.info(f"Available instruments: {len(instruments)}")

       def show_loading_message(self, message: str):
           """
           Display a loading message during startup.

           Args:
               message: The loading message to display
           """
           print(f"\n{'=' * 50}")
           print(f"  {message}")
           print(f"{'=' * 50}\n")

       def start(self):
           """
           Start normal client operation.

           This is called after set_api(), when the system is ready.
           """
           logger.info("Starting minimal client")
           self.running = True

           # Show welcome message
           self.clear_screen()
           print("=" * 50)
           print("  Pi-Pianoteq Minimal Client")
           print("=" * 50)
           print()
           print("Commands:")
           print("  n - Next preset")
           print("  p - Previous preset")
           print("  i - Show instrument info")
           print("  l - List all instruments")
           print("  q - Quit")
           print()

           # Show initial state
           self.display_current_state()

           # Start input loop
           self.run_input_loop()

       def run_input_loop(self):
           """
           Main input loop - accept keyboard commands.
           """
           while self.running:
               try:
                   command = input("\nCommand: ").lower().strip()

                   if command == 'q':
                       self.quit()
                   elif command == 'n':
                       self.next_preset()
                   elif command == 'p':
                       self.prev_preset()
                   elif command == 'i':
                       self.show_instrument_info()
                   elif command == 'l':
                       self.list_instruments()
                   else:
                       print(f"Unknown command: {command}")

               except (KeyboardInterrupt, EOFError):
                   print("\n")
                   self.quit()
                   break

       # Command handlers

       def next_preset(self):
           """Handle next preset command."""
           if self.api is None:
               print("API not available")
               return

           self.api.set_preset_next()
           print("\n→ Next preset")
           self.display_current_state()

       def prev_preset(self):
           """Handle previous preset command."""
           if self.api is None:
               print("API not available")
               return

           self.api.set_preset_prev()
           print("\n← Previous preset")
           self.display_current_state()

       def show_instrument_info(self):
           """Display detailed information about current instrument."""
           if self.api is None:
               print("API not available")
               return

           instrument = self.api.get_current_instrument()
           presets = instrument.presets

           print("\n" + "=" * 50)
           print(f"Instrument: {instrument.name}")
           print("=" * 50)
           print(f"Prefix: {instrument.preset_prefix}")
           print(f"Number of presets: {len(presets)}")
           print(f"Colors: {instrument.background_primary} / {instrument.background_secondary}")
           print("\nPresets:")
           for i, preset in enumerate(presets, 1):
               current = "→" if preset == self.api.get_current_preset() else " "
               print(f"  {current} {i}. {preset.display_name}")

       def list_instruments(self):
           """List all available instruments."""
           if self.api is None:
               print("API not available")
               return

           instruments = self.api.get_instruments()
           current = self.api.get_current_instrument()

           print("\n" + "=" * 50)
           print("Available Instruments")
           print("=" * 50)
           for i, inst in enumerate(instruments, 1):
               marker = "→" if inst == current else " "
               print(f"  {marker} {i}. {inst.name} ({len(inst.presets)} presets)")

       def quit(self):
           """Handle quit command."""
           print("Shutting down...")
           self.running = False

       # Display helpers

       def display_current_state(self):
           """Display current instrument and preset."""
           if self.api is None:
               print("API not available")
               return

           instrument = self.api.get_current_instrument()
           preset = self.api.get_current_preset()

           print("\n" + "-" * 50)
           print(f"Instrument: {instrument.name}")
           print(f"Preset:     {preset.display_name}")
           print("-" * 50)

       def clear_screen(self):
           """Clear the terminal screen."""
           print("\033[2J\033[H", end="")


Key Concepts Explained
======================

Two-Phase Initialization
-------------------------

The client handles three distinct phases:

**Phase 1: Construction (api=None)**

.. code-block:: python

   def __init__(self, api: Optional[ClientApi]):
       self.api = api  # Will be None initially
       self.running = False

At this point, Pianoteq may not be running yet, so the API is not available.

**Phase 2: API Injection**

.. code-block:: python

   def set_api(self, api: ClientApi):
       self.api = api
       # Now you can query instruments/presets
       instruments = api.get_instruments()

Once Pianoteq has started and instruments are discovered, the API is provided.

**Phase 3: Normal Operation**

.. code-block:: python

   def start(self):
       self.running = True
       # Begin normal operation
       self.run_input_loop()

Now the client accepts user input and uses the API normally.

Using the ClientApi
-------------------

The client interacts exclusively through the ClientApi interface:

**Getting current state:**

.. code-block:: python

   instrument = self.api.get_current_instrument()
   preset = self.api.get_current_preset()

**Navigating presets:**

.. code-block:: python

   self.api.set_preset_next()
   self.api.set_preset_prev()

**Navigating instruments:**

.. code-block:: python

   self.api.set_instrument_next()
   self.api.set_instrument_prev()
   self.api.set_instrument("D4 Grand Piano")

**Getting instrument data:**

.. code-block:: python

   instruments = self.api.get_instruments()
   presets = self.api.get_presets("D4 Grand Piano")

Null Safety
-----------

Always check if API is available:

.. code-block:: python

   def next_preset(self):
       if self.api is None:
           print("API not available")
           return

       self.api.set_preset_next()

This prevents crashes during the loading phase.

Registering Your Client
=======================

To use your client with pi-pianoteq, register it in ``__main__.py``:

.. code-block:: python

   # In src/pi_pianoteq/__main__.py

   from pi_pianoteq.client.minimal_client import MinimalClient

   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--minimal', action='store_true',
                          help='Use minimal example client')
       # ... other arguments ...

       args = parser.parse_args()

       # Create appropriate client
       if args.minimal:
           client = MinimalClient(api=None)
       elif args.cli:
           client = CliClient(api=None)
       else:
           client = GfxhatClient(api=None)

       # ... rest of initialization ...

Then run with:

.. code-block:: bash

   pipenv run pi-pianoteq --minimal

Extending the Example
=====================

Adding Instrument Selection
---------------------------

.. code-block:: python

   def select_instrument(self):
       """Interactively select an instrument."""
       instruments = self.api.get_instruments()

       print("\nSelect instrument:")
       for i, inst in enumerate(instruments, 1):
           print(f"  {i}. {inst.name}")

       try:
           choice = int(input("\nInstrument number: "))
           if 1 <= choice <= len(instruments):
               inst = instruments[choice - 1]
               self.api.set_instrument(inst.name)
               print(f"\nSwitched to: {inst.name}")
               self.display_current_state()
           else:
               print("Invalid selection")
       except ValueError:
           print("Invalid input")

Add to command loop:

.. code-block:: python

   elif command == 's':
       self.select_instrument()

Adding Preset Selection
-----------------------

.. code-block:: python

   def select_preset(self):
       """Interactively select a preset."""
       instrument = self.api.get_current_instrument()
       presets = instrument.presets

       print(f"\nSelect preset for {instrument.name}:")
       for i, preset in enumerate(presets, 1):
           print(f"  {i}. {preset.display_name}")

       try:
           choice = int(input("\nPreset number: "))
           if 1 <= choice <= len(presets):
               preset = presets[choice - 1]
               self.api.set_preset(instrument.name, preset.name)
               print(f"\nLoaded: {preset.display_name}")
               self.display_current_state()
           else:
               print("Invalid selection")
       except ValueError:
           print("Invalid input")

Adding Color Display
--------------------

For terminals that support ANSI colors:

.. code-block:: python

   def display_current_state(self):
       """Display current state with colors."""
       instrument = self.api.get_current_instrument()
       preset = self.api.get_current_preset()

       # Convert hex color to ANSI
       color = self.hex_to_ansi(instrument.background_primary)

       print("\n" + "-" * 50)
       print(f"{color}Instrument: {instrument.name}\033[0m")
       print(f"Preset:     {preset.display_name}")
       print("-" * 50)

   def hex_to_ansi(self, hex_color):
       """Convert hex color to ANSI escape code."""
       hex_color = hex_color.lstrip('#')
       r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
       return f"\033[38;2;{r};{g};{b}m"

Adding Background Thread
------------------------

For clients that need continuous updates:

.. code-block:: python

   def start(self):
       self.running = True

       # Start background display update thread
       self.display_thread = threading.Thread(target=self.display_loop)
       self.display_thread.daemon = True
       self.display_thread.start()

       # Start input loop
       self.run_input_loop()

   def display_loop(self):
       """Background thread that updates display."""
       while self.running:
           # Update display
           self.update_display()
           time.sleep(0.5)  # Update every 500ms

   def update_display(self):
       """Refresh the display."""
       # Only read data, don't call API mutators from background thread
       pass

Next Steps
==========

Now that you understand the basics:

1. **Modify this example** to suit your needs
2. **Read the full guide**: :doc:`../guides/client-development`
3. **Study reference clients**: Look at ``GfxhatClient`` and ``CliClient`` source code
4. **Learn the API**: :doc:`../api/client`
5. **Add tests**: :doc:`../guides/testing`

Additional Resources
====================

- :doc:`../guides/client-development` - Complete development guide
- :doc:`../guides/architecture` - System architecture
- :doc:`../api/client` - Full API reference
- ``src/pi_pianoteq/client/gfxhat/gfxhat_client.py`` - Hardware client example
- ``src/pi_pianoteq/client/cli/cli_client.py`` - TUI client example
