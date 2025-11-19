import unittest
from unittest.mock import Mock, MagicMock, patch

from pi_pianoteq.lib.client_lib import ClientLib
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset
from pi_pianoteq.rpc.types import PianoteqInfo, CurrentPreset


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
        client_lib.on_preset_modified = None

        client_lib.randomize_all()

        self.jsonrpc.load_preset.assert_not_called()
        self.jsonrpc.randomize_parameters.assert_not_called()

    def test_randomize_current_preset_sets_modified_flag(self):
        """Test that randomize_current_preset triggers modified callback."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        modified_callback = Mock()
        client_lib.set_on_preset_modified(modified_callback)

        client_lib.randomize_current_preset()

        modified_callback.assert_called_once_with(True)

    def test_randomize_all_sets_modified_flag(self):
        """Test that randomize_all triggers modified callback."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        modified_callback = Mock()
        client_lib.set_on_preset_modified(modified_callback)

        with patch('pi_pianoteq.lib.client_lib.random.choice') as mock_choice:
            mock_choice.side_effect = [self.inst1, self.preset1a]
            client_lib.randomize_all()

        # Should be called with True when randomizing
        self.assertTrue(any(call == ((True,),) for call in modified_callback.call_args_list))

    def test_set_preset_clears_modified_flag(self):
        """Test that loading a preset clears modified flag."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        modified_callback = Mock()
        client_lib.set_on_preset_modified(modified_callback)

        client_lib.set_preset(self.inst1.name, self.preset1a.name)

        # Should be called with False when loading preset
        modified_callback.assert_called_with(False)

    def test_set_preset_next_clears_modified_flag(self):
        """Test that navigating presets clears modified flag."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        modified_callback = Mock()
        client_lib.set_on_preset_modified(modified_callback)

        client_lib.set_preset_next()

        modified_callback.assert_called_with(False)

    def test_set_instrument_clears_modified_flag(self):
        """Test that changing instruments clears modified flag."""
        client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        modified_callback = Mock()
        client_lib.set_on_preset_modified(modified_callback)

        client_lib.set_instrument(self.inst2.name)

        modified_callback.assert_called_with(False)


if __name__ == '__main__':
    unittest.main()
