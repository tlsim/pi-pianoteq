.. pi-pianoteq documentation master file

Creating Custom Clients for pi-pianoteq
========================================

**Want to create your own interface for pi-pianoteq?** This guide shows you how to build custom clients for different hardware or platforms.

Pi-pianoteq provides a simple client API that lets you create interfaces for:

- **Hardware displays**: OLED screens, E-ink displays, LED matrices, touchscreens
- **Input devices**: Rotary encoders, physical buttons, MIDI controllers
- **Software interfaces**: Web apps, mobile apps, desktop GUIs, voice control

Why Use This Instead of Direct JSON-RPC?
-----------------------------------------

**You could** use Pianoteq's JSON-RPC API directly, but the client API simplifies development:

1. **Process management** - Automatically starts and stops Pianoteq
2. **State synchronization** - Handles initialization and syncs with Pianoteq's current state
3. **Demo filtering** - Automatically filters out demo instruments (only shows licensed ones)
4. **Pure Python API** - Simple method calls instead of JSON-RPC requests
5. **MIDI abstraction** - Sends MIDI Program Change messages automatically (no MIDI library needed)
6. **Typed data models** - Work with ``Instrument`` and ``Preset`` objects instead of raw JSON dictionaries
7. **Shortened preset names** - Removes instrument prefix for cleaner display on small screens (e.g., "Classical" instead of "D4 Grand Piano Classical")
8. **Preset grouping** - Presets organized by instrument, not a flat list
9. **UI theming** - Built-in instrument colors for display customization

**Example comparison:**

.. code-block:: python

   # Direct JSON-RPC (complex)
   response = requests.post('http://localhost:8081/jsonrpc', json={
       'jsonrpc': '2.0',
       'method': 'getListOfPresets',
       'id': 1
   })
   presets = response.json()['result']  # Raw list of dicts
   # Now send MIDI Program Change...
   # Now update selection state...
   # Now filter demos...

   # Client API (simple)
   api.set_preset_next()  # That's it!

Quick Start
-----------

**Three steps to create a client:**

1. Read the :doc:`guide` - Understand the client architecture
2. Study the :doc:`example` - See a complete working implementation
3. Use the :doc:`api` - Reference for all available methods

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Client Development

   guide
   example
   api
   data-models

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Reference

   reference/development
   reference/pianoteq-api
   reference/systemd

How It Works
------------

Your client implements two simple interfaces:

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi

   class MyClient(Client):
       def __init__(self, api):
           self.api = api

       def set_api(self, api):
           self.api = api  # Receive API when ready

       def show_loading_message(self, message):
           # Show "Starting..." and "Loading..." messages

       def start(self):
           # Your main loop - display info, handle input

The ``ClientApi`` gives you control:

.. code-block:: python

   # Navigate presets
   api.set_preset_next()
   api.set_preset_prev()

   # Get current state
   instrument = api.get_current_instrument()
   preset = api.get_current_preset()

   # Navigate instruments
   api.set_instrument_next()
   instruments = api.get_instruments()

That's it! See the guide for details.

Examples
--------

**Hardware Clients:**

- `GfxhatClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/gfxhat/gfxhat_client.py>`_ - Pimoroni GFX HAT (128x64 LCD, 6 buttons)
- `CliClient <https://github.com/tlsim/pi-pianoteq/blob/master/src/pi_pianoteq/client/cli/cli_client.py>`_ - Terminal interface with menus

**Your client here!** - Submit a PR to add your implementation

User Documentation
------------------

Looking for installation and usage docs? See the `main README <https://github.com/tlsim/pi-pianoteq>`_.
