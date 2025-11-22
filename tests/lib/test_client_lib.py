import unittest
from unittest.mock import Mock, MagicMock, patch

from pi_pianoteq.lib.client_lib import ClientLib
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset
from pi_pianoteq.rpc.types import PianoteqInfo, CurrentPreset
from pi_pianoteq.state.state_monitor import PianoteqState


class ClientLibPresetSyncTestCase(unittest.TestCase):
    def setUp(self):
        self.inst1 = Instrument('Steinway D', 'Steinway D', '#000000', '#FFFFFF')
        self.preset1a = Preset('Steinway D Prelude', 'Prelude')
        self.preset1b = Preset('Steinway D Jazz', 'Jazz')
        self.inst1.presets = [self.preset1a, self.preset1b]

        self.inst2 = Instrument('Ant. Petrof', 'Ant. Petrof', '#000000', '#FFFFFF')
        self.preset2a = Preset('Ant. Petrof Recording 1', 'Recording 1')
        self.preset2b = Preset('Ant. Petrof Recording 2', 'Recording 2')
        self.inst2.presets = [self.preset2a, self.preset2b]

        self.library = Library([self.inst1, self.inst2])
        self.selector = Selector([self.inst1, self.inst2])
        self.jsonrpc = Mock()

    def test_sync_with_matching_preset_syncs_position(self):
        preset_info = CurrentPreset(name='Ant. Petrof Recording 2')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)
        self.jsonrpc.load_preset.assert_not_called()

    def test_sync_with_non_matching_preset_resets_to_first(self):
        preset_info = CurrentPreset(name='Unknown Preset Not In Library')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.jsonrpc.load_preset.assert_called_once_with(self.preset1a.name)

    def test_sync_with_empty_preset_name_resets_to_first(self):
        preset_info = CurrentPreset(name='')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.jsonrpc.load_preset.assert_called_once_with(self.preset1a.name)

    def test_sync_with_missing_current_preset_resets_to_first(self):
        preset_info = CurrentPreset(name='')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.jsonrpc.load_preset.assert_called_once_with(self.preset1a.name)

    def test_sync_with_jsonrpc_exception_resets_to_first(self):
        self.jsonrpc.get_info.side_effect = Exception('Connection failed')

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.jsonrpc.load_preset.assert_called_once_with(self.preset1a.name)

    def test_sync_with_first_preset_syncs_correctly(self):
        preset_info = CurrentPreset(name='Steinway D Prelude')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)
        self.jsonrpc.load_preset.assert_not_called()


class ClientLibRandomizationTestCase(unittest.TestCase):
    def setUp(self):
        self.inst1 = Instrument('Steinway D', 'Steinway D', '#000000', '#FFFFFF')
        self.preset1a = Preset('Steinway D Prelude', 'Prelude')
        self.preset1b = Preset('Steinway D Jazz', 'Jazz')
        self.inst1.presets = [self.preset1a, self.preset1b]

        self.inst2 = Instrument('Ant. Petrof', 'Ant. Petrof', '#000000', '#FFFFFF')
        self.preset2a = Preset('Ant. Petrof Recording 1', 'Recording 1')
        self.preset2b = Preset('Ant. Petrof Recording 2', 'Recording 2')
        self.inst2.presets = [self.preset2a, self.preset2b]

        self.library = Library([self.inst1, self.inst2])
        self.selector = Selector([self.inst1, self.inst2])
        self.jsonrpc = Mock()

        preset_info = CurrentPreset(name='Steinway D Prelude')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

    def test_randomize_current_preset_calls_randomize_parameters(self):
        """Test that randomize_current_preset calls the JSON-RPC randomize method."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        self.jsonrpc.reset_mock()

        client_lib.randomize_current_preset()

        self.jsonrpc.randomize_parameters.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.random.choice')
    def test_randomize_all_selects_random_instrument_and_preset(self, mock_choice):
        """Test that randomize_all picks random instrument and preset."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        self.jsonrpc.reset_mock()

        mock_choice.side_effect = [self.inst2, self.preset2b]

        client_lib.randomize_all()

        self.assertEqual(2, mock_choice.call_count)
        self.jsonrpc.load_preset.assert_called_once_with(self.preset2b.name)
        self.jsonrpc.randomize_parameters.assert_called_once()
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)

    def test_randomize_all_handles_empty_library(self):
        """Test that randomize_all handles empty instrument library gracefully."""
        empty_library = Library([])
        empty_selector = Selector([])
        self.jsonrpc.get_info.side_effect = Exception("No instruments")

        client_lib = ClientLib.__new__(ClientLib)
        client_lib.jsonrpc = self.jsonrpc
        client_lib.instrument_library = empty_library
        client_lib.selector = empty_selector
        client_lib.on_exit = None

        client_lib.randomize_all()

        self.jsonrpc.load_preset.assert_not_called()
        self.jsonrpc.randomize_parameters.assert_not_called()


class ClientLibStateSyncTestCase(unittest.TestCase):
    """Test state synchronization integration with StateMonitor."""

    def setUp(self):
        self.inst1 = Instrument('Steinway D', 'Steinway D', '#000000', '#FFFFFF')
        self.preset1a = Preset('Steinway D Prelude', 'Prelude')
        self.preset1b = Preset('Steinway D Jazz', 'Jazz')
        self.inst1.presets = [self.preset1a, self.preset1b]

        self.inst2 = Instrument('Ant. Petrof', 'Ant. Petrof', '#000000', '#FFFFFF')
        self.preset2a = Preset('Ant. Petrof Recording 1', 'Recording 1')
        self.inst2.presets = [self.preset2a]

        self.library = Library([self.inst1, self.inst2])
        self.selector = Selector([self.inst1, self.inst2])
        self.jsonrpc = Mock()

        # Default to first preset synced with modified=False
        preset_info = CurrentPreset(name='Steinway D Prelude')
        info = PianoteqInfo(current_preset=preset_info, modified=False)
        self.jsonrpc.get_info.return_value = info

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_state_monitor_initialized_on_startup(self, mock_state_monitor_class):
        """Test that StateMonitor is created and started on initialization."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # StateMonitor should be created with correct parameters
        mock_state_monitor_class.assert_called_once_with(self.jsonrpc, poll_interval=1.0)
        # Should subscribe to state changes
        mock_monitor.subscribe.assert_called_once()
        # Should be started
        mock_monitor.start.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_cleanup_stops_state_monitor(self, mock_state_monitor_class):
        """Test that cleanup() stops the StateMonitor."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        client_lib.cleanup()

        mock_monitor.stop.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_modified_flag_updated_on_initial_sync(self, mock_state_monitor_class):
        """Test that initial sync updates the preset modified flag."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        # Set modified=True in Pianoteq
        preset_info = CurrentPreset(name='Steinway D Prelude')
        info = PianoteqInfo(current_preset=preset_info, modified=True)
        self.jsonrpc.get_info.return_value = info

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # Preset should have modified=True
        current_preset = client_lib.get_current_preset()
        self.assertTrue(current_preset.modified)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_state_change_updates_modified_flag(self, mock_state_monitor_class):
        """Test that state change callback updates modified flag."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # Initially unmodified
        current_preset = client_lib.get_current_preset()
        self.assertFalse(current_preset.modified)

        # Simulate state change with modified=True
        new_state = PianoteqState(preset_name='Steinway D Prelude', modified=True)
        client_lib._on_state_change(new_state)

        # Modified flag should be updated
        self.assertTrue(current_preset.modified)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_state_change_with_different_preset_syncs_selection(self, mock_state_monitor_class):
        """Test that external preset change syncs selector position."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # Initially on first preset
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

        # Simulate external preset change to second instrument
        new_state = PianoteqState(preset_name='Ant. Petrof Recording 1', modified=False)
        client_lib._on_state_change(new_state)

        # Selector should update to match
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_state_change_with_unknown_preset_logs_warning(self, mock_state_monitor_class):
        """Test that unknown external preset is logged but doesn't crash."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # Simulate external preset change to unknown preset
        new_state = PianoteqState(preset_name='Unknown Preset Not In Library', modified=False)

        # Should not raise exception
        client_lib._on_state_change(new_state)

        # Selector should not change
        self.assertEqual(0, self.selector.current_instrument_idx)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_subscribe_to_state_changes_registers_callback(self, mock_state_monitor_class):
        """Test that clients can subscribe to state changes."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        callback = Mock()
        client_lib.subscribe_to_state_changes(callback)

        self.assertIn(callback, client_lib._state_callbacks)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_state_change_notifies_client_callbacks(self, mock_state_monitor_class):
        """Test that state changes trigger client callbacks."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        callback = Mock()
        client_lib.subscribe_to_state_changes(callback)

        # Simulate state change
        new_state = PianoteqState(preset_name='Steinway D Jazz', modified=True)
        client_lib._on_state_change(new_state)

        # Callback should be called with new state
        callback.assert_called_once_with(new_state)

    @patch('pi_pianoteq.lib.client_lib.StateMonitor')
    def test_client_callback_exception_does_not_crash(self, mock_state_monitor_class):
        """Test that exceptions in client callbacks are handled gracefully."""
        mock_monitor = Mock()
        mock_state_monitor_class.return_value = mock_monitor

        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

        # Register a callback that raises exception
        bad_callback = Mock(side_effect=Exception("Callback error"))
        good_callback = Mock()

        client_lib.subscribe_to_state_changes(bad_callback)
        client_lib.subscribe_to_state_changes(good_callback)

        # Simulate state change
        new_state = PianoteqState(preset_name='Steinway D Jazz', modified=True)

        # Should not raise exception
        client_lib._on_state_change(new_state)

        # Both callbacks should be called despite exception
        bad_callback.assert_called_once()
        good_callback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
