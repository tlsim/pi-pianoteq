====================
Testing Guide
====================

This guide covers testing strategies for pi-pianoteq, including testing custom clients and the core system.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
========

Testing Levels
--------------

1. **Unit tests**: Test individual components in isolation
2. **Integration tests**: Test components working together
3. **System tests**: Test the full system with real Pianoteq
4. **Hardware tests**: Test on actual Raspberry Pi hardware

Testing Your Custom Client
===========================

Unit Testing with Mock API
---------------------------

The cleanest way to test your client is to mock the ``ClientApi`` interface:

.. code-block:: python

   import unittest
   from unittest.mock import Mock, MagicMock
   from pi_pianoteq.client import ClientApi
   from pi_pianoteq.instrument import Instrument, Preset
   from your_client import YourClient

   class TestYourClient(unittest.TestCase):
       def setUp(self):
           """Set up test fixtures."""
           # Create mock API
           self.api = Mock(spec=ClientApi)

           # Create mock data
           self.mock_preset = Mock(spec=Preset)
           self.mock_preset.name = "Test Preset"
           self.mock_preset.display_name = "Test Preset"

           self.mock_instrument = Mock(spec=Instrument)
           self.mock_instrument.name = "Test Piano"
           self.mock_instrument.presets = [self.mock_preset]
           self.mock_instrument.background_primary = "#1e3a5f"
           self.mock_instrument.background_secondary = "#0f1d2f"

           # Configure mock API returns
           self.api.get_current_instrument.return_value = self.mock_instrument
           self.api.get_current_preset.return_value = self.mock_preset
           self.api.get_instruments.return_value = [self.mock_instrument]

           # Create client
           self.client = YourClient(api=None)
           self.client.set_api(self.api)

       def test_next_preset_calls_api(self):
           """Test that next preset button calls API correctly."""
           self.client.handle_next_preset_button()

           self.api.set_preset_next.assert_called_once()

       def test_displays_current_instrument(self):
           """Test that display shows current instrument name."""
           display_text = self.client.get_display_text()

           self.assertIn("Test Piano", display_text)

       def test_loading_mode_without_api(self):
           """Test that client handles loading mode correctly."""
           client = YourClient(api=None)
           client.show_loading_message("Test")

           # Should not crash when api is None
           # Add assertions about loading display state

Testing Two-Phase Initialization
---------------------------------

.. code-block:: python

   def test_two_phase_initialization(self):
       """Test complete initialization sequence."""
       # Phase 1: Loading mode
       client = YourClient(api=None)
       self.assertIsNone(client.api)

       client.show_loading_message("Starting...")
       # Assert loading display is shown

       # Phase 2: API injection
       client.set_api(self.api)
       self.assertIsNotNone(client.api)

       # Phase 3: Normal operation
       client.start()
       # Assert normal display is shown

Testing Display Updates
-----------------------

.. code-block:: python

   def test_display_updates_on_preset_change(self):
       """Test that display updates after preset change."""
       # Record initial display
       initial_display = self.client.get_display_state()

       # Change preset
       self.client.handle_next_preset_button()

       # Verify display updated
       new_display = self.client.get_display_state()
       self.assertNotEqual(initial_display, new_display)

Testing Error Handling
-----------------------

.. code-block:: python

   def test_handles_api_errors_gracefully(self):
       """Test that client handles API errors without crashing."""
       # Make API raise an error
       self.api.set_preset_next.side_effect = Exception("API Error")

       # Should not crash
       try:
           self.client.handle_next_preset_button()
       except Exception:
           self.fail("Client should handle API errors gracefully")

Testing Threading (if applicable)
----------------------------------

.. code-block:: python

   import threading
   import time

   def test_thread_safety(self):
       """Test that client is thread-safe."""
       errors = []

       def call_api():
           try:
               for _ in range(100):
                   self.client.handle_next_preset_button()
           except Exception as e:
               errors.append(e)

       # Start multiple threads
       threads = [threading.Thread(target=call_api) for _ in range(5)]
       for t in threads:
           t.start()
       for t in threads:
           t.join()

       # Should not have any errors
       self.assertEqual(len(errors), 0)

Integration Testing
===================

Testing with Real ClientLib
----------------------------

For integration tests, use real components but mock external dependencies:

.. code-block:: python

   from pi_pianoteq.lib.client_lib import ClientLib
   from pi_pianoteq.instrument import Library, Instrument, Preset
   from pi_pianoteq.instrument.selector import Selector
   from unittest.mock import Mock

   class TestClientIntegration(unittest.TestCase):
       def setUp(self):
           """Set up real ClientLib with mock MIDI."""
           # Create real instruments and library
           preset1 = Preset("D4 Grand Piano Classic")
           preset2 = Preset("D4 Grand Piano Bright")

           instrument = Instrument("D4 Grand Piano", "D4", "#1e3a5f", "#0f1d2f")
           instrument.add_preset(preset1)
           instrument.add_preset(preset2)

           library = Library([instrument])
           selector = Selector(library)

           # Mock ProgramChange (don't send real MIDI)
           mock_program_change = Mock()

           # Create real ClientLib
           self.client_lib = ClientLib(library, selector, mock_program_change)

           # Create client with real ClientLib
           self.client = YourClient(api=None)
           self.client.set_api(self.client_lib)

       def test_preset_navigation(self):
           """Test navigating through presets."""
           # Get first preset
           first = self.client_lib.get_current_preset()

           # Go to next
           self.client_lib.set_preset_next()
           second = self.client_lib.get_current_preset()

           self.assertNotEqual(first.name, second.name)

           # Go to next (should wrap around)
           self.client_lib.set_preset_next()
           third = self.client_lib.get_current_preset()

           self.assertEqual(first.name, third.name)

System Testing
==============

Testing with Real Pianoteq
---------------------------

For system tests, use the CLI client with real Pianoteq:

**Prerequisites**:

1. Pianoteq installed and configured
2. JSON-RPC API enabled (default port 8081)
3. MIDI loopback configured

**Running system tests**:

.. code-block:: bash

   # Start system in CLI mode
   pipenv run pi-pianoteq --cli

   # Manually test:
   # - Navigate instruments (arrow keys)
   # - Navigate presets (arrow keys)
   # - Verify Pianoteq loads correct presets
   # - Check loading screen appears during startup

Automated System Tests
----------------------

You can automate system tests using the JSON-RPC API to verify behavior:

.. code-block:: python

   import unittest
   import subprocess
   import time
   import requests

   class TestSystemWithPianoteq(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           """Start Pianoteq."""
           cls.pianoteq_process = subprocess.Popen([
               "/path/to/pianoteq",
               "--headless",
               "--rpc"
           ])
           time.sleep(8)  # Wait for startup

       @classmethod
       def tearDownClass(cls):
           """Stop Pianoteq."""
           cls.pianoteq_process.terminate()
           cls.pianoteq_process.wait()

       def test_preset_change_via_api(self):
           """Test that pi-pianoteq changes presets in Pianoteq."""
           # Start pi-pianoteq in background
           # Send button press
           # Query Pianoteq API to verify preset changed
           pass

Running Tests
=============

Local Development
-----------------

**Run all tests**:

.. code-block:: bash

   pipenv run pytest tests/ -v

**Run specific test file**:

.. code-block:: bash

   pipenv run pytest tests/test_your_client.py -v

**Run with coverage**:

.. code-block:: bash

   pipenv run pytest tests/ --cov=pi_pianoteq --cov-report=html
   # Open htmlcov/index.html

**Run specific test**:

.. code-block:: bash

   pipenv run pytest tests/test_your_client.py::TestYourClient::test_next_preset -v

Continuous Integration
----------------------

For CI environments (GitHub Actions, etc.), use:

.. code-block:: bash

   # Install system dependencies
   apt-get install -y libasound2-dev

   # Install Python dependencies
   pip3 install pipenv
   pipenv install --dev

   # Run tests
   pipenv run pytest tests/ -v

See ``.github/workflows/test.yml`` for the full CI configuration.

Hardware Testing
================

Testing on Raspberry Pi
-----------------------

**Deploy to Pi**:

.. code-block:: bash

   python3 -m build
   ./deploy.sh

**Check service logs**:

.. code-block:: bash

   ssh tom@192.168.0.169 "sudo journalctl -u pi-pianoteq.service -n 50"

**Test client manually**:

1. Physical buttons for GfxhatClient
2. Check LCD display
3. Verify backlight colors change
4. Test all navigation paths

**Common issues**:

- **Display not updating**: Check systemd logs for errors
- **Buttons not responding**: Check GFX HAT connection
- **Wrong colors**: Check instrument color configuration
- **Crashes on startup**: Check Pianoteq is running and API is available

Testing Checklist for Custom Clients
=====================================

Before deploying your client, verify:

Functionality
-------------

- [ ] Loading screen shows during startup
- [ ] Display updates after ``set_api()``
- [ ] Current instrument name displays correctly
- [ ] Current preset name displays correctly
- [ ] Next preset button works
- [ ] Previous preset button works
- [ ] Next instrument button works (if implemented)
- [ ] Previous instrument button works (if implemented)
- [ ] Instrument menu shows all instruments (if implemented)
- [ ] Preset menu shows all presets (if implemented)
- [ ] Selection wraps around at boundaries
- [ ] Display updates immediately after preset change
- [ ] Instrument colors apply correctly (if supported)
- [ ] Shutdown button works (if implemented)

Error Handling
--------------

- [ ] Client doesn't crash if API call fails
- [ ] Client handles None API during loading mode
- [ ] Client handles empty instrument list
- [ ] Client handles empty preset list
- [ ] Client handles long instrument/preset names
- [ ] Client handles special characters in names

Performance
-----------

- [ ] Display updates smoothly (no lag)
- [ ] Button presses respond immediately
- [ ] No memory leaks (check with long-running tests)
- [ ] CPU usage is reasonable
- [ ] No thread deadlocks (if multi-threaded)

Cleanup
-------

- [ ] Client releases resources on exit
- [ ] Background threads stop properly
- [ ] Display clears on exit
- [ ] No zombie processes

Debugging Techniques
====================

Adding Debug Logging
--------------------

.. code-block:: python

   import logging

   logger = logging.getLogger(__name__)
   logger.setLevel(logging.DEBUG)

   class YourClient(Client):
       def set_api(self, api):
           logger.debug("set_api called")
           logger.debug(f"Available instruments: {len(api.get_instruments())}")
           self.api = api

       def handle_button(self):
           logger.debug("Button pressed")
           self.api.set_preset_next()
           preset = self.api.get_current_preset()
           logger.debug(f"New preset: {preset.name}")

Using Print Statements (Carefully)
-----------------------------------

**For CLI client**: Print statements work fine

**For GfxhatClient**: Avoid print, use logging instead (print breaks systemd logs)

Using a Debugger
----------------

**In development**:

.. code-block:: bash

   pipenv run python -m pdb -m pi_pianoteq --cli

**Remote debugging on Pi** (using debugpy):

.. code-block:: python

   import debugpy
   debugpy.listen(5678)
   debugpy.wait_for_client()

Then connect from VS Code or another debugger.

Mock Testing Tips
=================

Creating Realistic Mock Data
-----------------------------

.. code-block:: python

   def create_mock_instrument(name, num_presets=5):
       """Create a realistic mock instrument."""
       instrument = Mock(spec=Instrument)
       instrument.name = name
       instrument.preset_prefix = name.split()[0]
       instrument.background_primary = "#1e3a5f"
       instrument.background_secondary = "#0f1d2f"
       instrument.presets = [
           create_mock_preset(f"{name} Preset {i}")
           for i in range(num_presets)
       ]
       return instrument

   def create_mock_preset(name):
       """Create a realistic mock preset."""
       preset = Mock(spec=Preset)
       preset.name = name
       preset.display_name = name.split()[-1]  # Last word
       preset.midi_program_number = 0
       preset.midi_channel = 0
       return preset

Verifying Mock Interactions
----------------------------

.. code-block:: python

   def test_preset_change_sequence(self):
       """Test that preset changes happen in correct order."""
       self.client.handle_next_preset_button()

       # Verify call order
       self.api.set_preset_next.assert_called()
       self.api.get_current_preset.assert_called()

       # Verify call count
       self.assertEqual(self.api.set_preset_next.call_count, 1)

Best Practices
==============

Test Organization
-----------------

.. code-block:: text

   tests/
   ├── test_client_api.py          # ClientApi interface tests
   ├── test_client_lib.py          # ClientLib implementation tests
   ├── test_gfxhat_client.py       # GfxhatClient tests
   ├── test_cli_client.py          # CliClient tests
   ├── test_your_client.py         # Your custom client tests
   ├── test_library.py             # Library tests
   ├── test_selector.py            # Selector tests
   ├── test_program_change.py      # ProgramChange tests
   └── integration/
       ├── test_full_system.py     # System tests
       └── test_with_pianoteq.py   # Tests requiring real Pianoteq

Test Naming
-----------

Use descriptive test names:

.. code-block:: python

   # Good
   def test_next_preset_button_calls_set_preset_next():
       pass

   def test_display_shows_instrument_name_after_change():
       pass

   # Bad
   def test_button():
       pass

   def test_1():
       pass

Test Independence
-----------------

Each test should be independent:

.. code-block:: python

   # Good - setUp creates fresh state
   def setUp(self):
       self.api = Mock(spec=ClientApi)
       self.client = YourClient(api=None)
       self.client.set_api(self.api)

   # Bad - tests depend on execution order
   def test_a(self):
       self.client.some_state = True

   def test_b(self):
       self.assertTrue(self.client.some_state)  # Depends on test_a

Resources
=========

- pytest documentation: https://docs.pytest.org/
- unittest.mock documentation: https://docs.python.org/3/library/unittest.mock.html
- See ``tests/`` directory for examples
- See :doc:`client-development` for implementation patterns
- See :doc:`architecture` for system design
