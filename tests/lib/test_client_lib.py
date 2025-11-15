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


class ClientLibRandomisePresetTestCase(unittest.TestCase):
    """Test that the special Randomised preset triggers parameter randomization."""

    def setUp(self):
        self.inst1 = Instrument('Steinway D', 'Steinway D', '#000000', '#FFFFFF')
        self.preset1a = Preset('Steinway D Prelude', 'Prelude')
        self.preset1b = Preset('Steinway D Jazz', 'Jazz')
        self.random_preset = Preset('__RANDOMISE__', 'Randomised')
        self.inst1.presets = [self.preset1a, self.preset1b, self.random_preset]

        self.library = Library([self.inst1])
        self.selector = Selector([self.inst1])
        self.jsonrpc = Mock()

        # Mock get_info for sync
        preset_info = CurrentPreset(name='Steinway D Prelude')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        self.client_lib = ClientLib(self.library, self.selector, self.jsonrpc)
        self.jsonrpc.reset_mock()

    def test_set_preset_next_to_randomise_calls_randomize_parameters(self):
        """Test that navigating to Randomised preset calls randomize_parameters."""
        # Mock get_info to show we're on Steinway D
        preset_info = CurrentPreset(name='Steinway D Jazz', instrument='Steinway D')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        # Navigate from Prelude -> Jazz -> Randomised
        self.client_lib.set_preset_next()
        self.assertEqual(self.selector.current_instrument_preset_idx, 1)
        self.jsonrpc.load_preset.assert_called_once_with('Steinway D Jazz')
        self.jsonrpc.reset_mock()

        # Navigate to Randomised preset (still on same instrument)
        self.client_lib.set_preset_next()
        self.assertEqual(self.selector.current_instrument_preset_idx, 2)
        self.jsonrpc.randomize_parameters.assert_called_once()
        self.jsonrpc.load_preset.assert_not_called()

    def test_set_preset_directly_to_randomise_calls_randomize_parameters(self):
        """Test that directly selecting Randomised preset calls randomize_parameters."""
        # Mock get_info to show we're on Steinway D
        preset_info = CurrentPreset(name='Steinway D Prelude', instrument='Steinway D')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        self.client_lib.set_preset('Steinway D', '__RANDOMISE__')

        self.jsonrpc.randomize_parameters.assert_called_once()
        self.jsonrpc.load_preset.assert_not_called()

    def test_regular_preset_still_calls_load_preset(self):
        """Test that regular presets still call load_preset."""
        self.client_lib.set_preset_next()

        self.jsonrpc.load_preset.assert_called_once_with('Steinway D Jazz')
        self.jsonrpc.randomize_parameters.assert_not_called()

    def test_randomise_when_switching_instruments_loads_preset_first(self):
        """Test that switching instruments with Randomised loads real preset first."""
        # Add another instrument with real preset + Randomised preset
        inst2 = Instrument('Ant. Petrof', 'Ant. Petrof', '#000000', '#FFFFFF')
        real_preset = Preset('Ant. Petrof Recording 1', 'Recording 1')
        random_preset2 = Preset('__RANDOMISE__', 'Randomised')
        inst2.presets = [real_preset, random_preset2]

        # Update library and selector
        self.library.instruments.append(inst2)
        self.selector.instruments.append(inst2)

        # Mock get_info to show we're currently on a different instrument
        preset_info = CurrentPreset(name='Steinway D Prelude', instrument='Steinway D')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        # Switch to the new instrument and select randomise preset (second preset, index 1)
        self.selector.set_instrument('Ant. Petrof')
        self.selector.current_instrument_preset_idx = 1  # Point to Randomised
        preset = self.selector.get_current_preset()
        self.client_lib._apply_preset(preset)

        # Should first load the real preset, then randomize
        self.jsonrpc.load_preset.assert_called_once_with('Ant. Petrof Recording 1')
        self.jsonrpc.randomize_parameters.assert_called_once()

    def test_randomise_when_already_on_instrument_skips_preset_load(self):
        """Test that randomizing current instrument doesn't load preset first."""
        # Mock get_info to show we're on the current instrument
        preset_info = CurrentPreset(name='Steinway D Jazz', instrument='Steinway D')
        info = PianoteqInfo(current_preset=preset_info)
        self.jsonrpc.get_info.return_value = info

        # Navigate to Randomised preset (third preset, index 2)
        self.selector.current_instrument_preset_idx = 2
        preset = self.selector.get_current_preset()
        self.client_lib._apply_preset(preset)

        # Should NOT load a preset, just randomize
        self.jsonrpc.load_preset.assert_not_called()
        self.jsonrpc.randomize_parameters.assert_called_once()


if __name__ == '__main__':
    unittest.main()
