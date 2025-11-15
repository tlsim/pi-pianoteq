import unittest

from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset


class SelectorSetPresetByNameTestCase(unittest.TestCase):
    def setUp(self):
        self.inst1 = Instrument('Steinway D', 'Steinway D', '#000000', '#FFFFFF')
        self.preset1a = Preset('Steinway D Prelude', 'Prelude')
        self.preset1b = Preset('Steinway D Jazz', 'Jazz')
        self.inst1.presets = [self.preset1a, self.preset1b]

        self.inst2 = Instrument('Ant. Petrof', 'Ant. Petrof', '#000000', '#FFFFFF')
        self.preset2a = Preset('Ant. Petrof Recording 1', 'Recording 1')
        self.preset2b = Preset('Ant. Petrof Recording 2', 'Recording 2')
        self.inst2.presets = [self.preset2a, self.preset2b]

        self.selector = Selector([self.inst1, self.inst2])

    def test_set_preset_by_name_first_instrument_first_preset(self):
        result = self.selector.set_preset_by_name('Steinway D', 'Steinway D Prelude')
        self.assertTrue(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_first_instrument_second_preset(self):
        result = self.selector.set_preset_by_name('Steinway D', 'Steinway D Jazz')
        self.assertTrue(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_second_instrument_first_preset(self):
        result = self.selector.set_preset_by_name('Ant. Petrof', 'Ant. Petrof Recording 1')
        self.assertTrue(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_second_instrument_second_preset(self):
        result = self.selector.set_preset_by_name('Ant. Petrof', 'Ant. Petrof Recording 2')
        self.assertTrue(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_instrument_not_found(self):
        result = self.selector.set_preset_by_name('Unknown', 'Unknown Preset')
        self.assertFalse(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_preset_not_found(self):
        result = self.selector.set_preset_by_name('Steinway D', 'Nonexistent Preset')
        self.assertFalse(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_preset_by_name_preserves_current_on_failure(self):
        self.selector.current_instrument_idx = 1
        self.selector.current_instrument_preset_idx = 1

        result = self.selector.set_preset_by_name('Unknown', 'Unknown Preset')

        self.assertFalse(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)


if __name__ == '__main__':
    unittest.main()
