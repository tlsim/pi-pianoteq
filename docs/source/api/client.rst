======================
Client API Reference
======================

This page documents the client API interfaces that you'll use when creating a custom client.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
========

The client API consists of two main abstract classes:

- **Client**: Base class for implementing user interfaces
- **ClientApi**: Interface for controlling instruments and presets

Client Base Class
=================

.. autoclass:: pi_pianoteq.client.client.Client
   :members:
   :undoc-members:
   :show-inheritance:

Abstract Methods
----------------

Your client implementation must override these methods:

__init__(api)
~~~~~~~~~~~~~

.. code-block:: python

   def __init__(self, api: Optional[ClientApi]):
       """
       Initialize the client.

       Args:
           api: The ClientApi instance, or None during loading phase.
                During startup, this will be None until instruments are
                discovered.
       """

**Purpose**: Initialize your client's state and resources.

**When called**: At the very beginning, before Pianoteq has started.

**API availability**: The ``api`` parameter will be ``None``. Store it, but don't use it yet.

**Example**:

.. code-block:: python

   def __init__(self, api: Optional[ClientApi]):
       self.api = api
       self.running = False
       # Initialize display hardware, create UI components, etc.

set_api(api)
~~~~~~~~~~~~

.. code-block:: python

   def set_api(self, api: ClientApi):
       """
       Provide the ClientApi after initialization.

       Args:
           api: The ClientApi instance, now fully initialized with instruments.
       """

**Purpose**: Receive the API once Pianoteq has started and instruments are loaded.

**When called**: After Pianoteq startup (~6-8 seconds), once instruments are discovered.

**API availability**: The API is now fully functional. You can query instruments and presets.

**What to do**:

- Store the API reference
- Pre-fetch instrument/preset lists if needed for menus
- Prepare UI components that depend on instrument data
- **Don't** start event loops or threads yet

**Example**:

.. code-block:: python

   def set_api(self, api: ClientApi):
       self.api = api
       # Cache instruments for menu
       self.instruments = api.get_instruments()
       # Prepare UI components
       self.build_menu()

show_loading_message(message)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def show_loading_message(self, message: str):
       """
       Display a loading message during startup.

       Args:
           message: The message to display (e.g., "Starting Pianoteq...")
       """

**Purpose**: Provide user feedback during startup while waiting for Pianoteq.

**When called**: During startup, before API is available. May be called multiple times with different messages.

**API availability**: API is not available (``self.api`` is ``None``).

**What to do**:

- Display the message on your UI
- Keep it simple and fast
- Don't try to use the API

**Typical messages**:

- "Starting Pianoteq..." - Pianoteq process is launching
- "Loading..." - Waiting for API and instruments

**Example**:

.. code-block:: python

   def show_loading_message(self, message: str):
       self.display.clear()
       self.display.text(message, centered=True)
       self.display.show()

start()
~~~~~~~

.. code-block:: python

   def start(self):
       """
       Start normal client operation.

       This is called after set_api(), when the system is fully ready.
       """

**Purpose**: Begin normal operation of your client.

**When called**: After ``set_api()``, when everything is ready.

**API availability**: API is fully available and functional.

**What to do**:

- Start event loops
- Start background threads
- Accept user input
- Display initial state
- This method typically blocks until the client exits

**Example**:

.. code-block:: python

   def start(self):
       self.running = True
       self.display_current_state()
       # Start event loop (blocks)
       self.run_event_loop()

Initialization Flow
-------------------

The complete initialization sequence:

.. code-block:: python

   # 1. Construction (before Pianoteq starts)
   client = YourClient(api=None)

   # 2. Loading messages (during Pianoteq startup)
   client.show_loading_message("Starting Pianoteq...")
   # ... Pianoteq starts ...
   client.show_loading_message("Loading...")
   # ... Instruments discovered ...

   # 3. API injection (once ready)
   client.set_api(client_lib)

   # 4. Normal operation (blocks until exit)
   client.start()

ClientApi Interface
===================

.. autoclass:: pi_pianoteq.client.client_api.ClientApi
   :members:
   :undoc-members:
   :show-inheritance:

API Methods
-----------

Instrument Methods
~~~~~~~~~~~~~~~~~~

get_instruments()
^^^^^^^^^^^^^^^^^

.. code-block:: python

   def get_instruments(self) -> list[Instrument]:
       """Get list of all available instruments."""

**Returns**: List of :class:`~pi_pianoteq.instrument.instrument.Instrument` objects.

**Example**:

.. code-block:: python

   instruments = self.api.get_instruments()
   for inst in instruments:
       print(f"{inst.name}: {len(inst.presets)} presets")

get_current_instrument()
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def get_current_instrument(self) -> Instrument:
       """Get the currently selected instrument."""

**Returns**: The current :class:`~pi_pianoteq.instrument.instrument.Instrument`.

**Example**:

.. code-block:: python

   current = self.api.get_current_instrument()
   print(f"Now playing: {current.name}")

set_instrument(name)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_instrument(self, name: str):
       """
       Switch to a specific instrument.

       Args:
           name: The full instrument name (e.g., "D4 Grand Piano")
       """

**Example**:

.. code-block:: python

   self.api.set_instrument("D4 Grand Piano")

set_instrument_next()
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_instrument_next(self):
       """Switch to the next instrument (wraps around at end)."""

**Example**:

.. code-block:: python

   self.api.set_instrument_next()
   new_instrument = self.api.get_current_instrument()

set_instrument_prev()
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_instrument_prev(self):
       """Switch to the previous instrument (wraps around at start)."""

**Example**:

.. code-block:: python

   self.api.set_instrument_prev()

Preset Methods
~~~~~~~~~~~~~~

get_presets(instrument_name)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def get_presets(self, instrument_name: str) -> list[Preset]:
       """
       Get list of presets for a specific instrument.

       Args:
           instrument_name: The full instrument name

       Returns:
           List of Preset objects, or empty list if instrument not found
       """

**Example**:

.. code-block:: python

   presets = self.api.get_presets("D4 Grand Piano")
   for preset in presets:
       print(f"  - {preset.display_name}")

get_current_preset()
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def get_current_preset(self) -> Preset:
       """Get the currently loaded preset."""

**Returns**: The current :class:`~pi_pianoteq.instrument.preset.Preset`.

**Example**:

.. code-block:: python

   current = self.api.get_current_preset()
   print(f"Current preset: {current.display_name}")

set_preset(instrument_name, preset_name)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_preset(self, instrument_name: str, preset_name: str):
       """
       Load a specific preset.

       Switches to the instrument if not current, then loads the preset.
       Sends MIDI Program Change to Pianoteq.

       Args:
           instrument_name: The full instrument name
           preset_name: The full preset name (not display_name)
       """

**Example**:

.. code-block:: python

   self.api.set_preset("D4 Grand Piano", "D4 Grand Piano Close Mic")

set_preset_next()
^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_preset_next(self):
       """
       Switch to the next preset in current instrument.

       Wraps around to first preset when reaching the end.
       """

**Example**:

.. code-block:: python

   self.api.set_preset_next()
   new_preset = self.api.get_current_preset()

set_preset_prev()
^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_preset_prev(self):
       """
       Switch to the previous preset in current instrument.

       Wraps around to last preset when reaching the start.
       """

**Example**:

.. code-block:: python

   self.api.set_preset_prev()

Utility Methods
~~~~~~~~~~~~~~~

version()
^^^^^^^^^

.. code-block:: python

   @classmethod
   def version(cls) -> str:
       """Get the ClientApi version."""

**Returns**: API version string (currently "1.0.0").

**Example**:

.. code-block:: python

   version = ClientApi.version()
   print(f"Using ClientApi version {version}")

set_on_exit(callback)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_on_exit(self, on_exit: Callable[[], None]) -> None:
       """
       Register a callback to run on exit.

       Args:
           on_exit: Function to call during shutdown, before system shutdown
       """

**Purpose**: Register cleanup code to run when shutting down.

**Example**:

.. code-block:: python

   def cleanup(self):
       # Stop threads, release resources, etc.
       self.running = False
       self.display.clear()

   self.api.set_on_exit(cleanup)

shutdown_device()
^^^^^^^^^^^^^^^^^

.. code-block:: python

   def shutdown_device(self):
       """
       Trigger system shutdown.

       Calls registered exit callbacks, then executes system shutdown command.
       """

**Purpose**: Shutdown the entire system (Raspberry Pi).

**Warning**: This will shut down the system! Use only for hardware shutdown buttons.

**Example**:

.. code-block:: python

   def handle_shutdown_button(self):
       if self.confirm_shutdown():
           self.api.shutdown_device()

Usage Examples
==============

Complete Navigation Example
----------------------------

.. code-block:: python

   class NavigationExample(Client):
       def __init__(self, api):
           self.api = api

       def handle_input(self, button):
           """Handle button press from hardware."""
           if button == 'next_preset':
               self.api.set_preset_next()
               self.update_display()

           elif button == 'prev_preset':
               self.api.set_preset_prev()
               self.update_display()

           elif button == 'next_instrument':
               self.api.set_instrument_next()
               self.update_display()

       def update_display(self):
           """Update display with current state."""
           instrument = self.api.get_current_instrument()
           preset = self.api.get_current_preset()

           self.display.clear()
           self.display.text(instrument.name, y=0)
           self.display.text(preset.display_name, y=20)
           self.display.show()

Menu Building Example
----------------------

.. code-block:: python

   class MenuExample(Client):
       def build_instrument_menu(self):
           """Build scrollable instrument menu."""
           instruments = self.api.get_instruments()
           current = self.api.get_current_instrument()

           menu_items = []
           for inst in instruments:
               is_current = (inst == current)
               menu_items.append({
                   'name': inst.name,
                   'preset_count': len(inst.presets),
                   'selected': is_current
               })

           return menu_items

       def select_instrument(self, index):
           """Select instrument by menu index."""
           instruments = self.api.get_instruments()
           if 0 <= index < len(instruments):
               inst = instruments[index]
               self.api.set_instrument(inst.name)

Preset Selection Example
-------------------------

.. code-block:: python

   class PresetSelectionExample(Client):
       def show_preset_menu(self):
           """Show menu of presets for current instrument."""
           instrument = self.api.get_current_instrument()
           current_preset = self.api.get_current_preset()

           print(f"\nPresets for {instrument.name}:")
           for i, preset in enumerate(instrument.presets):
               marker = "→" if preset == current_preset else " "
               print(f"{marker} {i+1}. {preset.display_name}")

       def select_preset_by_index(self, index):
           """Load preset by index in current instrument."""
           instrument = self.api.get_current_instrument()
           if 0 <= index < len(instrument.presets):
               preset = instrument.presets[index]
               self.api.set_preset(instrument.name, preset.name)

Thread Safety Notes
===================

The ClientApi implementation (ClientLib) is **not explicitly thread-safe**.

Safe Patterns
-------------

**Single-threaded access** (recommended):

.. code-block:: python

   class SingleThreadClient(Client):
       def start(self):
           # All API calls from main thread
           while self.running:
               self.handle_input()  # Calls API
               self.update_display()  # Calls API

**Background display with locking**:

.. code-block:: python

   import threading

   class LockedClient(Client):
       def __init__(self, api):
           self.api = api
           self.api_lock = threading.Lock()

       def background_updater(self):
           while self.running:
               with self.api_lock:
                   preset = self.api.get_current_preset()
               self.update_display(preset)

       def button_handler(self):
           with self.api_lock:
               self.api.set_preset_next()

Unsafe Patterns
---------------

**Multiple threads without locking** (don't do this):

.. code-block:: python

   # WRONG - Race condition!
   def thread_a(self):
       self.api.set_preset_next()  # No lock

   def thread_b(self):
       self.api.set_instrument_next()  # No lock

See Also
========

- :doc:`../guides/client-development` - Complete development guide
- :doc:`../examples/minimal-client` - Working example
- :doc:`data-models` - Instrument and Preset classes
- :doc:`../guides/architecture` - System architecture
