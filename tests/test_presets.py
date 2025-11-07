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
        inst1.presets = [Preset(s1), Preset(s2)]
        inst2 = Instrument(i2, i2, '#000000', '#FFFFFF')
        inst2.presets = [Preset(a1), Preset(a2)]

        library = Library([inst1, inst2])
        grouped = library.get_instruments()
        self.assertEqual(2, len(grouped))
        self.assertEqual(2, len(grouped[0].presets))
        self.assertEqual(2, len(grouped[1].presets))


class PresetDisplayNameTestCase(unittest.TestCase):
    def test_strip_prefix_with_space_separator(self):
        preset = Preset('Steel Drum natural')
        self.assertEqual('Natural', preset.get_display_name('Steel Drum'))

    def test_strip_prefix_with_hyphen_separator(self):
        preset = Preset('Hand Pan - natural, foo')
        self.assertEqual('Natural, foo', preset.get_display_name('Hand Pan'))

    def test_strip_prefix_case_insensitive(self):
        preset = Preset('steel drum natural')
        self.assertEqual('Natural', preset.get_display_name('Steel Drum'))

    def test_strip_prefix_with_em_dash(self):
        preset = Preset('Hand Pan — natural')
        self.assertEqual('Natural', preset.get_display_name('Hand Pan'))

    def test_strip_prefix_with_colon(self):
        preset = Preset('Grotrian: Concert')
        self.assertEqual('Concert', preset.get_display_name('Grotrian'))

    def test_exact_match_returns_original(self):
        preset = Preset('Steel Drum')
        self.assertEqual('Steel Drum', preset.get_display_name('Steel Drum'))

    def test_no_match_returns_original(self):
        preset = Preset('Different Name')
        self.assertEqual('Different Name', preset.get_display_name('Steel Drum'))

    def test_multiple_word_result(self):
        preset = Preset('Ant. Petrof Recording 1')
        self.assertEqual('Recording 1', preset.get_display_name('Ant. Petrof'))

    def test_single_letter_capitalization(self):
        preset = Preset('Grotrian a')
        self.assertEqual('A', preset.get_display_name('Grotrian'))


if __name__ == '__main__':
    unittest.main()
