import unittest

from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset, find_longest_common_word_prefix, calculate_display_name

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


class CommonPrefixTestCase(unittest.TestCase):
    def test_simple_common_prefix(self):
        names = ['W1 roomy', 'W1 Logical', 'W1 - bright']
        self.assertEqual('W1', find_longest_common_word_prefix(names))

    def test_multi_word_prefix(self):
        names = ['Steel Drum natural', 'Steel Drum bright', 'Steel Drum warm']
        self.assertEqual('Steel Drum', find_longest_common_word_prefix(names))

    def test_no_common_prefix(self):
        names = ['Foo', 'Bar', 'Baz']
        self.assertEqual('', find_longest_common_word_prefix(names))

    def test_single_preset(self):
        names = ['W1 roomy']
        self.assertEqual('W1 roomy', find_longest_common_word_prefix(names))

    def test_empty_list(self):
        names = []
        self.assertEqual('', find_longest_common_word_prefix(names))

    def test_case_insensitive_matching(self):
        names = ['W1 roomy', 'w1 Logical', 'W1 bright']
        self.assertEqual('W1', find_longest_common_word_prefix(names))

    def test_mixed_separators(self):
        names = ['Hand Pan - foo', 'Hand Pan bar', 'Hand Pan: baz']
        self.assertEqual('Hand Pan', find_longest_common_word_prefix(names))

    def test_partial_word_not_matched(self):
        names = ['W1foo', 'W1bar']
        self.assertEqual('', find_longest_common_word_prefix(names))


class CalculateDisplayNameTestCase(unittest.TestCase):
    def test_strip_prefix_with_space_separator(self):
        self.assertEqual('Natural', calculate_display_name('Steel Drum natural', 'Steel Drum'))

    def test_strip_prefix_with_hyphen_separator(self):
        self.assertEqual('Natural, foo', calculate_display_name('Hand Pan - natural, foo', 'Hand Pan'))

    def test_strip_prefix_case_insensitive(self):
        self.assertEqual('Natural', calculate_display_name('steel drum natural', 'Steel Drum'))

    def test_strip_prefix_with_em_dash(self):
        self.assertEqual('Natural', calculate_display_name('Hand Pan — natural', 'Hand Pan'))

    def test_strip_prefix_with_colon(self):
        self.assertEqual('Concert', calculate_display_name('Grotrian: Concert', 'Grotrian'))

    def test_exact_match_returns_default(self):
        self.assertEqual('Default', calculate_display_name('Steel Drum', 'Steel Drum'))

    def test_no_match_returns_original(self):
        self.assertEqual('Different Name', calculate_display_name('Different Name', 'Steel Drum'))

    def test_multiple_word_result(self):
        self.assertEqual('Recording 1', calculate_display_name('Ant. Petrof Recording 1', 'Ant. Petrof'))

    def test_single_letter_capitalization(self):
        self.assertEqual('A', calculate_display_name('Grotrian a', 'Grotrian'))

    def test_empty_prefix_capitalizes_name(self):
        self.assertEqual('Natural', calculate_display_name('natural', ''))

    def test_example_from_issue(self):
        # Test the examples from the issue
        self.assertEqual('Roomy', calculate_display_name('W1 roomy', 'W1'))
        self.assertEqual('Logical', calculate_display_name('W1 Logical', 'W1'))
        self.assertEqual('Bright', calculate_display_name('W1 - bright', 'W1'))


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
