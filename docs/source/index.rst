.. pi-pianoteq documentation master file

Creating Custom Clients for pi-pianoteq
========================================

**Want to create your own interface for pi-pianoteq?** This guide shows you how to build custom clients for different hardware or platforms.

Pi-pianoteq provides a simple client API that lets you create interfaces for:

- **Hardware displays**: OLED screens, E-ink displays, LED matrices, touchscreens
- **Input devices**: Rotary encoders, physical buttons, MIDI controllers
- **Software interfaces**: Web apps, mobile apps, desktop GUIs, voice control

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
