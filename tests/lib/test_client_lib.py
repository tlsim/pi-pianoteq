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
    """Test randomization functionality in ClientLib."""

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

        self.client_lib = ClientLib(self.library, self.selector, self.jsonrpc)

    def test_randomize_current_preset_calls_jsonrpc(self):
        """Test that randomize_current_preset calls randomize_parameters."""
        self.client_lib.randomize_current_preset()

        self.jsonrpc.randomize_parameters.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.random.choice')
    def test_randomize_instrument_and_preset_selects_random_instrument(self, mock_choice):
        """Test that randomize_instrument_and_preset randomly selects an instrument."""
        mock_choice.return_value = self.inst2

        self.client_lib.randomize_instrument_and_preset()

        mock_choice.assert_called_once()
        instruments = mock_choice.call_args[0][0]
        self.assertEqual([self.inst1, self.inst2], instruments)

    @patch('pi_pianoteq.lib.client_lib.random.choice')
    def test_randomize_instrument_and_preset_loads_preset(self, mock_choice):
        """Test that randomize_instrument_and_preset loads preset for selected instrument."""
        mock_choice.return_value = self.inst2
        self.jsonrpc.reset_mock()

        self.client_lib.randomize_instrument_and_preset()

        self.jsonrpc.load_preset.assert_called_once_with(self.preset2a.name)

    @patch('pi_pianoteq.lib.client_lib.random.choice')
    def test_randomize_instrument_and_preset_randomizes_parameters(self, mock_choice):
        """Test that randomize_instrument_and_preset randomizes parameters."""
        mock_choice.return_value = self.inst2

        self.client_lib.randomize_instrument_and_preset()

        self.jsonrpc.randomize_parameters.assert_called_once()

    def test_randomize_instrument_and_preset_with_empty_library(self):
        """Test that randomize_instrument_and_preset handles empty library gracefully."""
        # Manually set empty library to avoid sync_preset() initialization issues
        self.client_lib.instrument_library = Library([])

        self.client_lib.randomize_instrument_and_preset()

        # Should not attempt to randomize with no instruments available
        self.assertEqual(self.jsonrpc.randomize_parameters.call_count, 0)


if __name__ == '__main__':
    unittest.main()
