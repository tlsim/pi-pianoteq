import unittest

from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset


class SelectorSetPositionFromObjectsTestCase(unittest.TestCase):
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

    def test_set_position_from_objects_first_instrument_first_preset(self):
        result = self.selector.set_position_from_objects(self.inst1, self.preset1a)
        self.assertTrue(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_first_instrument_second_preset(self):
        result = self.selector.set_position_from_objects(self.inst1, self.preset1b)
        self.assertTrue(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_second_instrument_first_preset(self):
        result = self.selector.set_position_from_objects(self.inst2, self.preset2a)
        self.assertTrue(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_second_instrument_second_preset(self):
        result = self.selector.set_position_from_objects(self.inst2, self.preset2b)
        self.assertTrue(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_instrument_not_in_library(self):
        inst3 = Instrument('Unknown', 'Unknown', '#000000', '#FFFFFF')
        inst3.presets = [Preset('Unknown Preset', 'Preset')]
        result = self.selector.set_position_from_objects(inst3, inst3.presets[0])
        self.assertFalse(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_preset_not_in_instrument(self):
        wrong_preset = Preset('Wrong Preset', 'Wrong')
        result = self.selector.set_position_from_objects(self.inst1, wrong_preset)
        self.assertFalse(result)
        self.assertEqual(0, self.selector.current_instrument_idx)
        self.assertEqual(0, self.selector.current_instrument_preset_idx)

    def test_set_position_from_objects_preserves_current_on_failure(self):
        self.selector.current_instrument_idx = 1
        self.selector.current_instrument_preset_idx = 1

        inst3 = Instrument('Unknown', 'Unknown', '#000000', '#FFFFFF')
        inst3.presets = [Preset('Unknown Preset', 'Preset')]
        result = self.selector.set_position_from_objects(inst3, inst3.presets[0])

        self.assertFalse(result)
        self.assertEqual(1, self.selector.current_instrument_idx)
        self.assertEqual(1, self.selector.current_instrument_preset_idx)


if __name__ == '__main__':
    unittest.main()
