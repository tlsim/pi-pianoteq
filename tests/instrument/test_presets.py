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


class PresetModifiedStateTestCase(unittest.TestCase):
    def test_preset_modified_defaults_to_false(self):
        preset = Preset('Test Preset')
        self.assertFalse(preset.modified)

    def test_preset_modified_can_be_set_on_init(self):
        preset = Preset('Test Preset', modified=True)
        self.assertTrue(preset.modified)

    def test_preset_modified_can_be_changed(self):
        preset = Preset('Test Preset')
        self.assertFalse(preset.modified)

        preset.modified = True
        self.assertTrue(preset.modified)

    def test_get_display_name_with_modified_unmodified(self):
        preset = Preset('Test Preset', display_name='Display Name', modified=False)
        self.assertEqual('Display Name', preset.get_display_name_with_modified())

    def test_get_display_name_with_modified_modified(self):
        preset = Preset('Test Preset', display_name='Display Name', modified=True)
        self.assertEqual('Display Name (modified)', preset.get_display_name_with_modified())

    def test_get_display_name_with_modified_uses_display_name_not_name(self):
        preset = Preset('Long Full Preset Name', display_name='Short', modified=True)
        self.assertEqual('Short (modified)', preset.get_display_name_with_modified())

    def test_get_display_name_with_modified_defaults_to_name(self):
        preset = Preset('Test Preset', modified=True)
        self.assertEqual('Test Preset (modified)', preset.get_display_name_with_modified())


class LibraryFindPresetTestCase(unittest.TestCase):
    def setUp(self):
        inst1 = Instrument(i1, i1, '#000000', '#FFFFFF')
        inst1.presets = [Preset(s1, 'Prelude'), Preset(s2, 'Jazz')]
        inst2 = Instrument(i2, i2, '#000000', '#FFFFFF')
        inst2.presets = [Preset(a1, 'Recording 1'), Preset(a2, 'Recording 2')]
        self.library = Library([inst1, inst2])

    def test_find_preset_by_name_first_instrument(self):
        result = self.library.find_preset_by_name(s1)
        self.assertIsNotNone(result)
        instrument, preset = result
        self.assertEqual(i1, instrument.name)
        self.assertEqual(s1, preset.name)

    def test_find_preset_by_name_second_instrument(self):
        result = self.library.find_preset_by_name(a2)
        self.assertIsNotNone(result)
        instrument, preset = result
        self.assertEqual(i2, instrument.name)
        self.assertEqual(a2, preset.name)

    def test_find_preset_by_name_not_found(self):
        result = self.library.find_preset_by_name('Nonexistent Preset')
        self.assertIsNone(result)

    def test_find_preset_by_name_empty_library(self):
        empty_library = Library([])
        result = empty_library.find_preset_by_name(s1)
        self.assertIsNone(result)

    def test_find_preset_by_name_case_sensitive(self):
        result = self.library.find_preset_by_name('steinway d prelude')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
