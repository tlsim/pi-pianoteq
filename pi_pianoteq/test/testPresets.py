import unittest

from pi_pianoteq.instrument.Library import Library
from pi_pianoteq.instrument.Instrument import Instrument

s1 = 'Steinway D Prelude'
s2 = 'Steinway D Jazz'
a1 = 'Ant. Petrof Recording 1'
a2 = 'Ant. Petrof Recording 2'

i1 = 'Steinway D'
i2 = 'Ant. Petrof'


class InstrumentTestCase(unittest.TestCase):
    def test_preset_instrument_grouping(self):
        preset_names = [a1, s1, s2, a2]
        instruments = [Instrument(i1, i1, '#000000', '#FFFFFF'), Instrument(i2, i2, '#000000', '#FFFFFF')]
        library = Library(preset_names, instruments)
        grouped = library.get_instruments()
        self.assertEqual(2, len(grouped))
        self.assertEqual(2, len(grouped[0].presets))
        self.assertEqual(2, len(grouped[1].presets))


if __name__ == '__main__':
    unittest.main()
