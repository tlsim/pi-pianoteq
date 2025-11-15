import unittest
from unittest.mock import Mock, MagicMock, patch

from pi_pianoteq.lib.client_lib import ClientLib
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset
from pi_pianoteq.midi.program_change import ProgramChange


class ClientLibSyncTestCase(unittest.TestCase):
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
        self.program_change = Mock(spec=ProgramChange)
        self.jsonrpc = Mock()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_matching_preset_syncs_position(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {
            'current_preset': {
                'name': 'Ant. Petrof Recording 2'
            }
        }

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)
        self.program_change.set_preset.assert_not_called()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_non_matching_preset_resets_to_first(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {
            'current_preset': {
                'name': 'Unknown Preset Not In Library'
            }
        }

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.program_change.set_preset.assert_called_once()
        called_preset = self.program_change.set_preset.call_args[0][0]
        self.assertEqual(self.preset1a.name, called_preset.name)

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_empty_preset_name_resets_to_first(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {
            'current_preset': {
                'name': ''
            }
        }

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.program_change.set_preset.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_missing_current_preset_resets_to_first(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {}

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.program_change.set_preset.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_jsonrpc_exception_resets_to_first(self, mock_sleep):
        self.jsonrpc.get_info.side_effect = Exception('Connection failed')

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.program_change.set_preset.assert_called_once()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_with_first_preset_syncs_correctly(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {
            'current_preset': {
                'name': 'Steinway D Prelude'
            }
        }

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)
        self.program_change.set_preset.assert_not_called()

    @patch('pi_pianoteq.lib.client_lib.sleep')
    def test_sync_respects_startup_delay(self, mock_sleep):
        self.jsonrpc.get_info.return_value = {
            'current_preset': {
                'name': 'Steinway D Jazz'
            }
        }

        client_lib = ClientLib(self.library, self.selector, self.program_change, self.jsonrpc)

        mock_sleep.assert_called_once()


if __name__ == '__main__':
    unittest.main()
