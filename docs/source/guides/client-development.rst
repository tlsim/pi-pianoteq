==========================
Client Development Guide
==========================

This guide walks you through creating a custom client for pi-pianoteq. Whether you're building support for new hardware (OLED displays, rotary encoders, touchscreens) or software interfaces (web, mobile, desktop GUI), this guide covers everything you need to know.

.. contents:: Table of Contents
   :local:
   :depth: 2

Introduction
============

What is a Client?
-----------------

A **client** in pi-pianoteq is any user interface that allows users to:

- View the current instrument and preset
- Navigate between instruments
- Select and load presets
- View instrument/preset menus
- Trigger system shutdown (optional)

pi-pianoteq includes two reference clients:

- **GfxhatClient**: Hardware client for Pimoroni GFX HAT (128x64 LCD, 6 buttons, RGB backlight)
- **CliClient**: Terminal-based client using prompt_toolkit (keyboard navigation, full-screen TUI)

Why Create a Custom Client?
----------------------------

You might want to create a client for:

- **Different hardware**: OLED displays (SSD1306, SH1106), E-ink displays, touchscreens, LED matrices
- **Different input methods**: Rotary encoders, physical buttons, touchscreen gestures
- **Different platforms**: Web interface, mobile app, desktop GUI, MIDI controller
- **Accessibility**: Voice control, large text displays, screen readers

Architecture Overview
=====================

Client Architecture
-------------------

pi-pianoteq separates UI clients from business logic:

.. code-block:: text

   Your Client (implements Client, uses ClientApi)
         ↓
   ClientLib (implements ClientApi)
         ↓
   ┌─────────────┬──────────────┬───────────────┐
   │   Library   │   Selector   │ ProgramChange │
   └─────────────┴──────────────┴───────────────┘
         ↓              ↓              ↓
   [Instruments]  [Selection State]  [MIDI to Pianoteq]

**Your client** interacts exclusively with the ``ClientApi`` interface. You never directly access Library, Selector, or ProgramChange.

Key Components
--------------

Client (Abstract Base Class)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your client must inherit from ``Client`` and implement:

- ``__init__(api: Optional[ClientApi])`` - Constructor accepting optional API
- ``set_api(api: ClientApi)`` - Receive API after startup
- ``show_loading_message(message: str)`` - Display loading messages
- ``start()`` - Begin normal operation

See :doc:`../api/client` for complete reference.

ClientApi (Interface)
~~~~~~~~~~~~~~~~~~~~~

The ``ClientApi`` defines all operations clients can perform:

**Instrument methods:**

- ``get_instruments() -> list[Instrument]`` - Get all instruments
- ``get_current_instrument() -> Instrument`` - Get current instrument
- ``set_instrument(name: str)`` - Switch to specific instrument
- ``set_instrument_next()`` - Next instrument
- ``set_instrument_prev()`` - Previous instrument

**Preset methods:**

- ``get_presets(instrument_name: str) -> list[Preset]`` - Get presets for instrument
- ``get_current_preset() -> Preset`` - Get current preset
- ``set_preset(instrument_name: str, preset_name: str)`` - Load specific preset
- ``set_preset_next()`` - Next preset
- ``set_preset_prev()`` - Previous preset

**Utility methods:**

- ``shutdown_device()`` - Trigger system shutdown
- ``set_on_exit(callback)`` - Register exit callback
- ``version() -> str`` - Get API version

See :doc:`../api/client` for parameter details and return types.

Two-Phase Initialization
=========================

Why Two-Phase Initialization?
------------------------------

Pianoteq takes **6-8 seconds** to start up and load instruments. During this time:

1. Pianoteq process launches
2. JSON-RPC API becomes available (~6 seconds)
3. Instruments are discovered via API
4. ``ClientLib`` is constructed

**The problem**: Users need feedback during startup, but the API isn't available yet.

**The solution**: Two-phase initialization allows your client to show loading messages before the API is ready.

The Three Phases
----------------

Phase 1: Loading Mode (api=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your client is instantiated with ``api=None``:

.. code-block:: python

   client = YourClient(api=None)
   client.show_loading_message("Starting Pianoteq...")
   # API not available - display loading screen only

During this phase:

- ✓ Show loading messages
- ✓ Initialize display hardware
- ✗ Cannot access instruments/presets (no API yet)

Phase 2: API Injection
~~~~~~~~~~~~~~~~~~~~~~~

Once instruments are discovered, ``set_api()`` is called:

.. code-block:: python

   client.set_api(client_lib)
   # API now available - prepare for normal operation

During this phase:

- ✓ Store API reference
- ✓ Prepare UI components
- ✓ Query instruments/presets to build menus
- ✗ Don't start event loops or background threads yet

Phase 3: Normal Operation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, ``start()`` is called to begin normal operation:

.. code-block:: python

   client.start()
   # Begin normal operation - event loops, user input, etc.

During this phase:

- ✓ Start event loops
- ✓ Accept user input
- ✓ Update displays
- ✓ Use all ClientApi methods

Implementation Example
----------------------

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class MyClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           self.api = api
           self.running = False
           # Initialize display hardware here

       def set_api(self, api: ClientApi):
           """API is now available - prepare for normal operation."""
           self.api = api
           # Cache instruments for menu building
           self.instruments = api.get_instruments()

       def show_loading_message(self, message: str):
           """Show loading message during startup."""
           # Display message on your hardware/UI
           print(f"Loading: {message}")

       def start(self):
           """Begin normal operation."""
           self.running = True
           # Start event loop, accept input, etc.
           self.run()

Creating Your First Client
===========================

Step 1: Inherit from Client
----------------------------

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class MyClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           self.api = api

Step 2: Implement Required Methods
-----------------------------------

**set_api()**

Store the API and prepare your UI:

.. code-block:: python

   def set_api(self, api: ClientApi):
       self.api = api
       # Pre-fetch data for menus if needed
       self.instruments = api.get_instruments()

**show_loading_message()**

Display loading feedback:

.. code-block:: python

   def show_loading_message(self, message: str):
       # Update your display
       self.display.clear()
       self.display.text(message, x=0, y=0)
       self.display.show()

**start()**

Begin normal operation:

.. code-block:: python

   def start(self):
       self.running = True
       # Start your main loop
       while self.running:
           self.update_display()
           self.handle_input()

Step 3: Use the ClientApi
--------------------------

Display current state:

.. code-block:: python

   def update_display(self):
       if self.api is None:
           return  # Still in loading mode

       instrument = self.api.get_current_instrument()
       preset = self.api.get_current_preset()

       self.display.clear()
       self.display.text(instrument.name, x=0, y=0)
       self.display.text(preset.display_name, x=0, y=20)
       self.display.show()

Handle user input:

.. code-block:: python

   def handle_input(self):
       if button_next_preset.is_pressed():
           self.api.set_preset_next()
       elif button_prev_preset.is_pressed():
           self.api.set_preset_prev()
       elif button_next_instrument.is_pressed():
           self.api.set_instrument_next()

Step 4: Implement Cleanup
--------------------------

If your client uses background threads or needs cleanup:

.. code-block:: python

   def stop(self):
       self.running = False
       # Stop threads, release resources, etc.

   def __del__(self):
       self.stop()

Complete Minimal Example
=========================

See :doc:`../examples/minimal-client` for a complete, working minimal client implementation.

Data Models
===========

Instrument
----------

The ``Instrument`` class represents a Pianoteq instrument:

.. code-block:: python

   class Instrument:
       name: str                    # e.g., "D4 Grand Piano"
       preset_prefix: str           # e.g., "D4"
       background_primary: str      # Hex color for UI
       background_secondary: str    # Hex color for UI gradient
       presets: list[Preset]        # List of available presets

**Usage:**

.. code-block:: python

   instruments = self.api.get_instruments()
   for inst in instruments:
       print(f"{inst.name} has {len(inst.presets)} presets")

Preset
------

The ``Preset`` class represents an instrument preset:

.. code-block:: python

   class Preset:
       name: str                         # Full preset name from Pianoteq
       display_name: str                 # Formatted for display (common prefix removed)
       midi_program_number: int | None   # MIDI program number
       midi_channel: int | None          # MIDI channel

**Usage:**

.. code-block:: python

   current_preset = self.api.get_current_preset()
   print(f"Now playing: {current_preset.display_name}")

   # Get presets for specific instrument
   presets = self.api.get_presets("D4 Grand Piano")
   for preset in presets:
       print(f"  - {preset.display_name}")

Common Patterns
===============

Pattern 1: Simple Display Client (GfxhatClient-style)
------------------------------------------------------

Use a state machine with different display modes:

.. code-block:: python

   class MyClient(Client):
       def __init__(self, api):
           self.api = api
           self.mode = "loading"
           self.displays = {
               "loading": LoadingDisplay(),
               "instrument": InstrumentDisplay(),
               "menu": MenuDisplay(),
           }

       def update(self):
           current_display = self.displays[self.mode]
           current_display.render(self.api)

       def switch_mode(self, new_mode):
           self.mode = new_mode

Pattern 2: Full-Screen TUI (CliClient-style)
---------------------------------------------

Use layout swapping:

.. code-block:: python

   class MyClient(Client):
       def __init__(self, api):
           self.api = api
           self.loading_layout = self.create_loading_layout()
           self.normal_layout = self.create_normal_layout()
           self.app = Application(layout=self.loading_layout)

       def start(self):
           # Switch to normal layout
           self.app.layout = self.normal_layout
           self.app.run()

Pattern 3: Event-Driven Client
-------------------------------

Use callbacks for hardware events:

.. code-block:: python

   class MyClient(Client):
       def start(self):
           # Register hardware callbacks
           button_a.on_press = self.on_button_a
           button_b.on_press = self.on_button_b

           # Start event loop
           self.event_loop.run()

       def on_button_a(self):
           self.api.set_preset_next()
           self.update_display()

Pattern 4: Threaded Display Updates
------------------------------------

For displays that need background updates (scrolling text, animations):

.. code-block:: python

   import threading

   class MyClient(Client):
       def start(self):
           self.running = True
           self.display_thread = threading.Thread(target=self.display_loop)
           self.display_thread.start()

       def display_loop(self):
           while self.running:
               self.update_display()
               time.sleep(0.1)  # 10 FPS

       def stop(self):
           self.running = False
           self.display_thread.join()

Thread Safety
-------------

``ClientApi`` implementations are **not guaranteed to be thread-safe**. If your client uses multiple threads:

1. **Recommended**: Only call ClientApi from one thread
2. **Alternative**: Use locks around API calls

.. code-block:: python

   import threading

   class MyClient(Client):
       def __init__(self, api):
           self.api = api
           self.api_lock = threading.Lock()

       def safe_next_preset(self):
           with self.api_lock:
               self.api.set_preset_next()

Advanced Topics
===============

Instrument and Preset Menus
----------------------------

Building scrollable menus:

.. code-block:: python

   class MenuDisplay:
       def __init__(self, api):
           self.api = api
           self.instruments = api.get_instruments()
           self.selected_index = 0

       def render(self):
           # Show 3 items at a time with selection cursor
           start = max(0, self.selected_index - 1)
           visible = self.instruments[start:start + 3]

           for i, inst in enumerate(visible):
               cursor = ">" if i == 1 else " "
               self.display.text(f"{cursor} {inst.name}", y=i * 20)

       def move_up(self):
           self.selected_index = max(0, self.selected_index - 1)

       def move_down(self):
           self.selected_index = min(
               len(self.instruments) - 1,
               self.selected_index + 1
           )

       def select(self):
           inst = self.instruments[self.selected_index]
           self.api.set_instrument(inst.name)

Scrolling Text for Long Names
------------------------------

For displays with limited width:

.. code-block:: python

   class ScrollingText:
       def __init__(self, text, width):
           self.text = text
           self.width = width
           self.offset = 0

       def update(self):
           if len(self.text) > self.width:
               self.offset = (self.offset + 1) % (len(self.text) + 4)

       def get_visible_text(self):
           padded = self.text + "    "  # Add spacing for scroll loop
           return padded[self.offset:self.offset + self.width]

See ``src/pi_pianoteq/client/gfxhat/scrolling_text.py`` for a complete implementation.

Handling Shutdown
-----------------

If your client includes a shutdown button:

.. code-block:: python

   def handle_shutdown_button(self):
       # This will call your on_exit callback then trigger system shutdown
       self.api.shutdown_device()

   def cleanup(self):
       # Register cleanup callback to run before shutdown
       self.api.set_on_exit(self.cleanup)
       # Stop threads, release hardware, etc.

Using Instrument Colors
-----------------------

The ``Instrument`` class includes color information for UI theming:

.. code-block:: python

   instrument = self.api.get_current_instrument()

   # Use for RGB LED backlight
   primary = instrument.background_primary    # e.g., "#1e3a5f"
   secondary = instrument.background_secondary # e.g., "#0f1d2f"

   # Convert hex to RGB
   def hex_to_rgb(hex_color):
       hex_color = hex_color.lstrip('#')
       return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

   r, g, b = hex_to_rgb(primary)
   set_backlight_color(r, g, b)

Testing Your Client
===================

Unit Testing with Mock API
---------------------------

.. code-block:: python

   import unittest
   from unittest.mock import Mock
   from my_client import MyClient

   class TestMyClient(unittest.TestCase):
       def setUp(self):
           self.api = Mock()
           self.api.get_current_instrument.return_value = Mock(
               name="Test Piano",
               presets=[Mock(display_name="Preset 1")]
           )
           self.client = MyClient(api=self.api)

       def test_next_preset(self):
           self.client.handle_next_button()
           self.api.set_preset_next.assert_called_once()

Integration Testing
-------------------

For testing with real Pianoteq:

.. code-block:: python

   # Use --cli mode for testing without affecting production
   # pipenv run pi-pianoteq --cli

See ``docs/development.md`` for the full testing workflow.

Troubleshooting
===============

Common Issues
-------------

**"AttributeError: 'NoneType' object has no attribute 'get_current_instrument'"**

You're trying to use the API during loading mode. Check:

.. code-block:: python

   def update_display(self):
       if self.api is None:
           self.show_loading_screen()
           return

       # Safe to use API here
       instrument = self.api.get_current_instrument()

**Display not updating after preset change**

Make sure you're calling your update/render method after API calls:

.. code-block:: python

   def on_next_button(self):
       self.api.set_preset_next()
       self.update_display()  # Don't forget this!

**Threading issues / race conditions**

Use locks if calling ClientApi from multiple threads:

.. code-block:: python

   with self.api_lock:
       self.api.set_preset_next()

**Client not receiving set_api() call**

Ensure your client is properly registered in ``__main__.py``. See the registration of ``GfxhatClient`` and ``CliClient`` for examples.

Debugging Tips
--------------

1. **Add logging**: Use Python's ``logging`` module

   .. code-block:: python

      import logging
      logger = logging.getLogger(__name__)

      def set_api(self, api):
          logger.info(f"API set with {len(api.get_instruments())} instruments")
          self.api = api

2. **Test phases independently**: Test loading mode, then API injection, then normal operation

3. **Check systemd logs** (on Raspberry Pi):

   .. code-block:: bash

      ssh tom@192.168.0.169 "sudo journalctl -u pi-pianoteq.service -n 50"

4. **Use CLI mode for debugging**: Easier than debugging on hardware

   .. code-block:: bash

      pipenv run pi-pianoteq --cli

Next Steps
==========

- See :doc:`../examples/minimal-client` for a complete working example
- See :doc:`../api/client` for the full API reference
- See :doc:`architecture` for deeper architectural details
- Read the source code of ``GfxhatClient`` and ``CliClient`` for real-world examples
- Check out ``docs/development.md`` for the development workflow
