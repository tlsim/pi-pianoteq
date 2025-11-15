=============
API Reference
=============

This page documents the Client and ClientApi interfaces you'll use when creating a custom client.

Client Interface
================

Implement these four methods in your client:

__init__(api)
-------------

.. code-block:: python

   def __init__(self, api: Optional[ClientApi]):
       """Initialize your client. API will be None during startup."""

**When called**: At application start, before Pianoteq launches

**Parameters**: ``api`` - Will be ``None`` initially

**What to do**: Initialize your display hardware or UI components

set_api(api)
------------

.. code-block:: python

   def set_api(self, api: ClientApi):
       """Receive the API once Pianoteq is ready."""

**When called**: After the JSON-RPC API initializes and instruments are loaded

**Parameters**: ``api`` - The ClientApi instance to use

**What to do**: Store the API reference, optionally cache instrument data

**Note**: Initialization typically takes 6-8 seconds on a Raspberry Pi, but may be faster on other hardware

show_loading_message(message)
------------------------------

.. code-block:: python

   def show_loading_message(self, message: str):
       """Display a loading message during startup."""

**When called**: During startup, may be called multiple times

**Parameters**: ``message`` - Usually "Starting..." or "Loading..."

**What to do**: Display the message on your UI

start()
-------

.. code-block:: python

   def start(self):
       """Begin normal operation."""

**When called**: After ``set_api()``, when system is ready

**What to do**: Start your main event loop. This method typically blocks until exit.

ClientApi Interface
===================

These methods are available on the API object you receive in ``set_api()``.

Preset Navigation
-----------------

set_preset_next()
~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_preset_next()

Navigate to the next preset in the current instrument. Wraps around to the first preset.

set_preset_prev()
~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_preset_prev()

Navigate to the previous preset in the current instrument. Wraps around to the last preset.

get_current_preset()
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   preset = api.get_current_preset()

**Returns**: The current :class:`Preset` object

**Example**:

.. code-block:: python

   preset = api.get_current_preset()
   print(preset.display_name)  # "Classical"

set_preset(instrument_name, preset_name)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_preset(instrument_name, preset_name)

Load a specific preset. Switches to the instrument if needed.

**Parameters**:
- ``instrument_name`` - Full instrument name (e.g., "D4 Grand Piano")
- ``preset_name`` - Full preset name (use ``preset.name``, not ``preset.display_name``)

**Example**:

.. code-block:: python

   api.set_preset("D4 Grand Piano", "D4 Grand Piano Classical")

Instrument Navigation
---------------------

set_instrument_next()
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_instrument_next()

Navigate to the next instrument. Wraps around to the first instrument. Also loads the first preset of that instrument.

set_instrument_prev()
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_instrument_prev()

Navigate to the previous instrument. Wraps around to the last instrument. Also loads the first preset of that instrument.

get_current_instrument()
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   instrument = api.get_current_instrument()

**Returns**: The current :class:`Instrument` object

**Example**:

.. code-block:: python

   instrument = api.get_current_instrument()
   print(instrument.name)  # "D4 Grand Piano"

set_instrument(name)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_instrument(name)

Switch to a specific instrument by name. Also loads the first preset.

**Parameters**: ``name`` - Full instrument name

**Example**:

.. code-block:: python

   api.set_instrument("D4 Grand Piano")

get_instruments()
~~~~~~~~~~~~~~~~~

.. code-block:: python

   instruments = api.get_instruments()

**Returns**: List of all available :class:`Instrument` objects

**Example**:

.. code-block:: python

   instruments = api.get_instruments()
   for inst in instruments:
       print(f"{inst.name} - {len(inst.presets)} presets")

get_presets(instrument_name)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   presets = api.get_presets(instrument_name)

Get all presets for a specific instrument.

**Parameters**: ``instrument_name`` - Full instrument name

**Returns**: List of :class:`Preset` objects, or empty list if instrument not found

**Example**:

.. code-block:: python

   presets = api.get_presets("D4 Grand Piano")
   for preset in presets:
       print(preset.display_name)

Utility Methods
---------------

shutdown_device()
~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.shutdown_device()

Shut down the system (Raspberry Pi). Use for hardware shutdown buttons.

⚠️ **Warning**: This will power off the system!

set_on_exit(callback)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   api.set_on_exit(callback)

Register a cleanup function to run before shutdown.

**Parameters**: ``callback`` - Function to call (takes no arguments)

**Example**:

.. code-block:: python

   def cleanup():
       self.display.clear()
       self.stop_threads()

   api.set_on_exit(cleanup)

version()
~~~~~~~~~

.. code-block:: python

   version = ClientApi.version()

**Returns**: API version string (currently "1.0.0")

Complete Example
================

.. code-block:: python

   from pi_pianoteq.client import Client, ClientApi
   from typing import Optional

   class MyClient(Client):
       def __init__(self, api: Optional[ClientApi]):
           self.api = api

       def set_api(self, api: ClientApi):
           self.api = api
           # Cache data if needed
           self.instruments = api.get_instruments()

       def show_loading_message(self, message: str):
           print(f"Loading: {message}")

       def start(self):
           while True:
               # Display current state
               inst = self.api.get_current_instrument()
               preset = self.api.get_current_preset()
               print(f"{inst.name} - {preset.display_name}")

               # Handle input
               cmd = input("Command (n/p): ")
               if cmd == 'n':
                   self.api.set_preset_next()
               elif cmd == 'p':
                   self.api.set_preset_prev()

See Also
========

- :doc:`guide` - Complete development guide
- :doc:`data-models` - Instrument and Preset details
- :doc:`example` - Full minimal client example
