====================
Architecture Overview
====================

This document provides a detailed overview of the pi-pianoteq architecture for developers who want to understand how the system works internally.

.. contents:: Table of Contents
   :local:
   :depth: 2

System Architecture
===================

High-Level Overview
-------------------

pi-pianoteq is structured in layers:

.. code-block:: text

   ┌─────────────────────────────────────────────┐
   │          Client Layer (UI)                  │
   │  GfxhatClient, CliClient, YourClient        │
   └──────────────────┬──────────────────────────┘
                      │ ClientApi interface
   ┌──────────────────┴──────────────────────────┐
   │          ClientLib (API Bridge)             │
   │  Implements ClientApi, coordinates backend  │
   └──────────────────┬──────────────────────────┘
                      │
           ┌──────────┼──────────┐
           │          │          │
   ┌───────┴───┐ ┌────┴────┐ ┌──┴────────┐
   │  Library  │ │Selector │ │Program    │
   │           │ │         │ │Change     │
   └───────────┘ └─────────┘ └───────────┘
        │            │            │
   [Instruments] [State]      [MIDI]
        │                         │
        └─────────────┬───────────┘
                      │
   ┌──────────────────┴──────────────────────────┐
   │         JsonRpcClient (API Wrapper)         │
   └──────────────────┬──────────────────────────┘
                      │ HTTP JSON-RPC
   ┌──────────────────┴──────────────────────────┐
   │         Pianoteq (External Process)         │
   └─────────────────────────────────────────────┘

Component Responsibilities
==========================

Client Layer
------------

**Purpose**: Implement user interfaces

**Responsibilities**:

- Display current instrument and preset
- Accept user input (buttons, keyboard, touch, etc.)
- Show loading messages during startup
- Provide navigation (menus, scrolling, etc.)

**Key classes**: ``Client`` (abstract), ``GfxhatClient``, ``CliClient``

**Dependencies**: Uses ``ClientApi`` only

ClientLib (API Bridge)
----------------------

**Purpose**: Coordinate backend components and provide a clean API

**Responsibilities**:

- Implement ``ClientApi`` interface
- Coordinate Library, Selector, and ProgramChange
- Handle MIDI timing delays during startup
- Manage lifecycle (exit callbacks)

**Key class**: ``ClientLib``

**Dependencies**: Library, Selector, ProgramChange

Library
-------

**Purpose**: Manage instrument and preset data

**Responsibilities**:

- Store all discovered instruments
- Store all presets for each instrument
- Provide read-only access to instrument data

**Key classes**: ``Library``, ``Instrument``, ``Preset``

**Dependencies**: Config (for instrument discovery)

Selector
--------

**Purpose**: Track current selection state

**Responsibilities**:

- Track current instrument
- Track current preset
- Navigate between instruments (next/prev)
- Navigate between presets (next/prev)
- Circular navigation (wrap around at boundaries)

**Key class**: ``Selector``

**Dependencies**: Library

ProgramChange
-------------

**Purpose**: Send MIDI Program Change messages to Pianoteq

**Responsibilities**:

- Send MIDI Program Change when preset changes
- Set proper MIDI channel based on preset configuration
- Handle MIDI communication with Pianoteq

**Key class**: ``ProgramChange``

**Dependencies**: JsonRpcClient

JsonRpcClient
-------------

**Purpose**: Low-level Pianoteq API wrapper

**Responsibilities**:

- HTTP JSON-RPC communication with Pianoteq
- Method call abstraction
- Error handling and retries

**Key class**: ``JsonRpcClient``

**Dependencies**: Pianoteq process (external)

Data Flow
=========

Instrument Discovery (Startup)
-------------------------------

.. code-block:: text

   1. Main process launches Pianoteq
   2. Wait for JSON-RPC API availability (~6 seconds)
   3. JsonRpcClient → getListOfPresets()
   4. Config → parse presets, group by instrument
   5. Library ← store Instruments and Presets
   6. Selector → initialize with first instrument/preset
   7. ClientLib ← constructed with Library, Selector, ProgramChange
   8. Client.set_api(ClientLib)
   9. Client.start()

Changing Presets (User Action)
-------------------------------

.. code-block:: text

   1. User presses "next preset" button
   2. Client → ClientApi.set_preset_next()
   3. ClientLib → Selector.set_preset_next()
   4. Selector → updates current_preset
   5. ClientLib → ProgramChange.set_preset(new_preset)
   6. ProgramChange → JsonRpcClient.sendProgramChange()
   7. JsonRpcClient → HTTP request to Pianoteq
   8. Pianoteq loads the new preset
   9. Client → updates display

Changing Instruments (User Action)
-----------------------------------

.. code-block:: text

   1. User selects instrument from menu
   2. Client → ClientApi.set_instrument("Piano Name")
   3. ClientLib → Selector.set_instrument("Piano Name")
   4. Selector → updates current_instrument and current_preset
   5. ClientLib → ProgramChange.set_preset(new_preset)
   6. ProgramChange → JsonRpcClient.sendProgramChange()
   7. JsonRpcClient → HTTP request to Pianoteq
   8. Pianoteq loads the new preset
   9. Client → updates display

Initialization Sequence
=======================

Detailed Startup Flow
---------------------

The startup sequence is carefully orchestrated to provide user feedback during Pianoteq's 6-8 second startup time:

**Phase 1: Pre-API (0-6 seconds)**

.. code-block:: python

   # __main__.py
   client = GfxhatClient(api=None)  # Loading mode
   client.show_loading_message("Starting Pianoteq...")

   # Launch Pianoteq process
   start_pianoteq()

   client.show_loading_message("Loading...")

   # Wait for API availability
   wait_for_api()

**Phase 2: Instrument Discovery (6-8 seconds)**

.. code-block:: python

   # Discover instruments via API
   config = Config(jsonrpc_client)
   instruments = config.discover_instruments()

   # Build library
   library = Library(instruments)

   # Initialize selector
   selector = Selector(library)

   # Initialize MIDI
   program_change = ProgramChange(jsonrpc_client)

   # Build ClientLib
   client_lib = ClientLib(library, selector, program_change)

**Phase 3: API Injection & Startup**

.. code-block:: python

   # Provide API to client
   client.set_api(client_lib)

   # Start normal operation
   client.start()  # Blocks until exit

Why This Design?
----------------

1. **Loading screen support**: Users see feedback during long startup
2. **Separation of concerns**: UI separate from business logic
3. **Testability**: Easy to mock ClientApi for testing
4. **Flexibility**: Easy to add new clients without changing backend

Configuration and Discovery
============================

Instrument Discovery
--------------------

Instruments are discovered dynamically from Pianoteq:

1. Call ``getListOfPresets()`` via JSON-RPC
2. Parse preset names to identify instruments (by prefix)
3. Group presets by instrument
4. Compute display names (remove common prefixes)
5. Assign colors from configuration

**Why dynamic?**: Different Pianoteq licenses have different instruments. Trial versions have 51+ instruments, licensed versions may have 5-20 depending on purchased instruments.

Preset Grouping
---------------

Presets are grouped by their prefix:

.. code-block:: text

   Raw preset names:
   - "D4 Grand Piano Close Mic"
   - "D4 Grand Piano Classical"
   - "U4 Upright Piano Soft"
   - "U4 Upright Piano Bright"

   Grouped by prefix:
   D4:
     - "Close Mic" (display_name)
     - "Classical" (display_name)
   U4:
     - "Soft" (display_name)
     - "Bright" (display_name)

Display names are computed by finding the longest common word prefix and removing it. See ``src/pi_pianoteq/instrument/display_name.py`` for implementation.

Thread Safety
=============

Current State
-------------

The current implementation is **not explicitly thread-safe**:

- ``Library``: Read-only after initialization (safe)
- ``Selector``: Mutable state (not thread-safe)
- ``ProgramChange``: Sends MIDI (not thread-safe)
- ``ClientLib``: Coordinates above (not thread-safe)

Recommendations for Client Developers
--------------------------------------

**If your client is single-threaded**: No concerns

**If your client uses multiple threads**:

1. **Recommended**: Only call ClientApi from one thread (UI thread)
2. **Alternative**: Use locks around API calls:

   .. code-block:: python

      import threading

      class MyClient(Client):
          def __init__(self, api):
              self.api = api
              self.api_lock = threading.Lock()

          def safe_api_call(self):
              with self.api_lock:
                  self.api.set_preset_next()

**Background threads for display**: OK, just don't call API from them:

.. code-block:: python

   def display_thread(self):
       while self.running:
           # Reading data is OK (no API calls)
           instrument = self.cached_instrument
           self.render(instrument)
           time.sleep(0.1)

   def button_handler(self):
       # API calls from main thread only
       self.api.set_preset_next()
       self.cached_instrument = self.api.get_current_instrument()

Testing Architecture
====================

Unit Testing
------------

Each component can be tested in isolation:

**Testing a client**:

.. code-block:: python

   api = Mock(spec=ClientApi)
   client = MyClient(api=api)
   client.set_api(api)

   # Test behavior
   client.handle_button_press()
   api.set_preset_next.assert_called_once()

**Testing ClientLib**:

.. code-block:: python

   library = Mock(spec=Library)
   selector = Mock(spec=Selector)
   program_change = Mock(spec=ProgramChange)

   client_lib = ClientLib(library, selector, program_change)
   client_lib.set_preset_next()

   selector.set_preset_next.assert_called_once()

See ``tests/`` directory for examples.

Integration Testing
-------------------

For testing with real Pianoteq, use CLI mode:

.. code-block:: bash

   pipenv run pi-pianoteq --cli

This allows testing the full stack without requiring GFX HAT hardware.

Future Architecture Considerations
===================================

Potential Enhancements
----------------------

1. **Thread safety**: Add locks to Selector and ClientLib
2. **Async API**: Support async/await for non-blocking clients
3. **Event system**: Notify clients of external preset changes
4. **State persistence**: Remember last preset across restarts
5. **Preset favorites**: Tag and quick-access favorite presets
6. **Search/filter**: Search presets by name or tags
7. **Multiple clients**: Support multiple simultaneous clients (hardware + web)

Extending the System
--------------------

**Adding new client types**: Implement ``Client`` interface

**Adding new backend features**: Extend ``ClientApi`` and ``ClientLib``

**Supporting multiple Pianoteq instances**: Abstract JsonRpcClient connection

**Remote control**: Implement network protocol over ClientApi

See :doc:`client-development` for client implementation guide.
