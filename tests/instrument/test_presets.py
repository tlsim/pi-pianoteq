import unittest

from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset

s1 = 'Steinway D Prelude'
s2 = 'Steinway D Jazz'
a1 = 'Ant. Petrof Recording 1'
a2 = 'Ant. Petrof Recording 2'

i1 = 'Steinway D'
i2 = 'Ant. Petrof'


class InstrumentTestCase(unittest.TestCase):
    def test_preset_instrument_grouping(self):
        # Create instruments with presets already added
        inst1 = Instrument(i1, i1, '#000000', '#FFFFFF')
        inst1.presets = [Preset(s1, 'Prelude'), Preset(s2, 'Jazz')]
        inst2 = Instrument(i2, i2, '#000000', '#FFFFFF')
        inst2.presets = [Preset(a1, 'Recording 1'), Preset(a2, 'Recording 2')]

        library = Library([inst1, inst2])
        grouped = library.get_instruments()
        self.assertEqual(2, len(grouped))
        self.assertEqual(2, len(grouped[0].presets))
        self.assertEqual(2, len(grouped[1].presets))


class PresetDisplayNameFieldTestCase(unittest.TestCase):
    def test_preset_has_display_name_field(self):
        preset = Preset('Steel Drum natural', display_name='Natural')
        self.assertEqual('Steel Drum natural', preset.name)
        self.assertEqual('Natural', preset.display_name)

    def test_preset_defaults_display_name_to_name(self):
        preset = Preset('Steel Drum natural')
        self.assertEqual('Steel Drum natural', preset.name)
        self.assertEqual('Steel Drum natural', preset.display_name)


if __name__ == '__main__':
    unittest.main()
