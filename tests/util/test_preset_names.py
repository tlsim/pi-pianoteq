import unittest

from pi_pianoteq.util.preset_names import find_longest_common_word_prefix, calculate_display_name


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


if __name__ == '__main__':
    unittest.main()
