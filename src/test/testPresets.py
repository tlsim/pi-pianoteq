import unittest
from instrument.Library import Library

s1 = 'Steinway D Prelude'
s2 = 'Steinway D Jazz'
a1 = 'Ant. Petrof Recording 1'
a2 = 'Ant. Petrof Recording 2'
u1 = 'Unknown Instrument Preset 1'

i1 = 'Steinway D'
i2 = 'Ant. Petrof'


class InstrumentTestCase(unittest.TestCase):
    def test_preset_instrument_grouping(self):
        preset_names = [a1, s1, s2, a2]
        instrument_names = [i1, i2]
        library = Library(preset_names, instrument_names)
        grouped = library.get_instruments()
        self.assertEqual(2, len(grouped))
        self.assertEqual(2, len(grouped[0].presets))
        self.assertEqual(2, len(grouped[1].presets))

    def test_unknown_instrument_grouping(self):
        preset_names = [a1, s1, u1, s2, a2]
        instrument_names = [i1, i2]
        library = Library(preset_names, instrument_names)
        grouped = library.get_instruments()
        self.assertEqual(3, len(grouped))
        self.assertEqual(1, len(grouped[2].presets))
        self.assertEqual(u1, grouped[2].presets[0].name)


if __name__ == '__main__':
    unittest.main()
