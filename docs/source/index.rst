.. pi-pianoteq documentation master file

pi-pianoteq Documentation
=========================

**pi-pianoteq** is a Python application for controlling Pianoteq on a Raspberry Pi with hardware interfaces like the Pimoroni GFX HAT or a terminal-based CLI.

This documentation is for developers who want to create custom clients or understand the internal architecture. For user-facing documentation, see the `README <https://github.com/tlsim/pi-pianoteq>`_.

.. toctree::
   :maxdepth: 2
   :caption: Developer Guides

   guides/client-development
   guides/architecture
   guides/testing

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/data-models
   api/reference

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/minimal-client

.. toctree::
   :maxdepth: 1
   :caption: Existing Documentation

   existing/development
   existing/pianoteq-api
   existing/systemd

Quick Links
-----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Overview
--------

pi-pianoteq uses a modular client architecture that separates UI implementation from business logic:

* **Client**: Abstract base class for implementing UIs (hardware displays, CLI, web, etc.)
* **ClientApi**: Abstract API interface that clients use to control instruments and presets
* **ClientLib**: Concrete implementation that bridges between clients and the backend
* **Two-phase initialization**: Supports loading screens during Pianoteq's 6-8 second startup

Getting Started
---------------

If you want to create a custom client (e.g., for an OLED display, rotary encoder, web interface, or mobile app), start with:

1. :doc:`guides/client-development` - Complete guide to implementing a client
2. :doc:`examples/minimal-client` - Simple reference implementation
3. :doc:`api/client` - Full API reference

Architecture
------------

The system architecture separates concerns:

.. code-block:: text

   ┌──────────────┐
   │ Custom Client│  ← Your implementation (GfxhatClient, CliClient, etc.)
   └──────┬───────┘
          │ implements Client, uses ClientApi
          ↓
   ┌──────────────┐
   │  ClientLib   │  ← Bridges to backend, implements ClientApi
   └──────┬───────┘
          │
          ├─→ Library (Instrument/Preset management)
          ├─→ Selector (Current selection state)
          └─→ ProgramChange (MIDI communication with Pianoteq)

See :doc:`guides/architecture` for detailed information.

Contributing
------------

Contributions are welcome! Please see the `GitHub repository <https://github.com/tlsim/pi-pianoteq>`_ for contribution guidelines.

License
-------

This project is open source. See the repository for license information.
