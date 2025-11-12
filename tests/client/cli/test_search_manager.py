import unittest
from unittest.mock import Mock

from pi_pianoteq.client.cli.search_manager import SearchManager
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset


class SearchManagerTestCase(unittest.TestCase):
    """Tests for SearchManager class."""

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_api = Mock()

        # Create test instruments with presets
        self.piano = Instrument("Piano", "Piano", "#FF0000", "#0000FF")
        self.piano.add_preset(Preset("Piano - Bright", "Bright"))
        self.piano.add_preset(Preset("Piano - Dark", "Dark"))
        self.piano.add_preset(Preset("Piano - Mellow", "Mellow"))

        self.strings = Instrument("Strings", "Strings", "#00FF00", "#0000FF")
        self.strings.add_preset(Preset("Strings - Legato", "Legato"))
        self.strings.add_preset(Preset("Strings - Staccato", "Staccato"))

        self.brass = Instrument("Brass", "Brass", "#0000FF", "#FF0000")
        self.brass.add_preset(Preset("Brass - Loud", "Loud"))

        self.mock_api.get_instruments.return_value = [self.piano, self.strings, self.brass]
        self.mock_api.get_presets.return_value = self.piano.presets

    def test_initialization(self):
        """SearchManager should initialize with empty state."""
        manager = SearchManager(self.mock_api)

        self.assertEqual(manager.query, "")
        self.assertIsNone(manager.context)
        self.assertEqual(manager.filtered_items, [])
        self.assertIsNone(manager.preset_menu_instrument)

    def test_enter_search_instrument_context(self):
        """Entering instrument search should populate filtered_items with instruments."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        self.assertEqual(manager.context, 'instrument')
        self.assertEqual(manager.query, "")
        self.assertEqual(len(manager.filtered_items), 3)  # Piano, Strings, Brass

        # Check item structure
        piano_item = manager.filtered_items[0]
        self.assertEqual(piano_item[0], "Piano")  # display name
        self.assertEqual(piano_item[1], "instrument")  # type
        self.assertEqual(piano_item[2], "Piano")  # data

    def test_enter_search_preset_context(self):
        """Entering preset search should populate filtered_items with presets."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('preset', 'Piano')

        self.assertEqual(manager.context, 'preset')
        self.assertEqual(manager.preset_menu_instrument, 'Piano')
        self.assertEqual(len(manager.filtered_items), 3)  # Bright, Dark, Mellow

        # Check item structure
        preset_item = manager.filtered_items[0]
        self.assertEqual(preset_item[0], "Bright")  # display name
        self.assertEqual(preset_item[1], "preset")  # type
        self.assertEqual(preset_item[2], "Piano - Bright")  # data (raw name)

    def test_enter_search_combined_context(self):
        """Entering combined search should populate with both instruments and presets."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('combined')

        self.assertEqual(manager.context, 'combined')
        # 3 instruments + 6 presets (3 piano + 2 strings + 1 brass) = 9 items
        self.assertEqual(len(manager.filtered_items), 9)

        # Check that we have both types
        item_types = [item[1] for item in manager.filtered_items]
        self.assertIn('instrument', item_types)
        self.assertIn('preset', item_types)

    def test_exit_search_resets_state(self):
        """Exiting search should reset all state."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')
        manager.set_query("Pia")

        manager.exit_search()

        self.assertEqual(manager.query, "")
        self.assertIsNone(manager.context)
        self.assertEqual(manager.filtered_items, [])
        self.assertIsNone(manager.preset_menu_instrument)

    def test_set_query_updates_results(self):
        """Setting query should update filtered results."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        manager.set_query("Pia")

        self.assertEqual(manager.query, "Pia")
        self.assertEqual(len(manager.filtered_items), 1)
        self.assertEqual(manager.filtered_items[0][0], "Piano")

    def test_search_is_case_insensitive(self):
        """Search should be case-insensitive."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        manager.set_query("PIANO")

        self.assertEqual(len(manager.filtered_items), 1)
        self.assertEqual(manager.filtered_items[0][0], "Piano")

    def test_search_filters_by_substring(self):
        """Search should match substrings."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        manager.set_query("ass")  # Should match "Brass"

        self.assertEqual(len(manager.filtered_items), 1)
        self.assertEqual(manager.filtered_items[0][0], "Brass")

    def test_empty_query_shows_all_items(self):
        """Empty query should show all items."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        manager.set_query("XYZ")  # Filter to none
        self.assertEqual(len(manager.filtered_items), 0)

        manager.set_query("")  # Clear query

        self.assertEqual(len(manager.filtered_items), 3)  # All instruments

    def test_search_presets_filters_correctly(self):
        """Preset search should filter by preset display names."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('preset', 'Piano')

        manager.set_query("dark")

        self.assertEqual(len(manager.filtered_items), 1)
        self.assertEqual(manager.filtered_items[0][0], "Dark")

    def test_combined_search_filters_both_types(self):
        """Combined search should filter both instruments and presets."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('combined')

        # Search for "ia" should match "Piano" instrument and its presets
        manager.set_query("ia")

        # Should find Piano instrument + presets with "ia" in name
        piano_items = [item for item in manager.filtered_items if 'Piano' in item[0]]
        self.assertGreater(len(piano_items), 0)

    def test_get_selection_action_instrument(self):
        """Getting selection action for instrument should return correct action."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        action = manager.get_selection_action(0)  # Select Piano

        self.assertIsNotNone(action)
        action_type, action_data = action
        self.assertEqual(action_type, 'set_instrument')
        self.assertEqual(action_data, 'Piano')

    def test_get_selection_action_preset_single(self):
        """Getting selection action for preset in preset context."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('preset', 'Piano')

        action = manager.get_selection_action(0)  # Select first preset

        self.assertIsNotNone(action)
        action_type, action_data = action
        self.assertEqual(action_type, 'set_preset_single')
        self.assertEqual(action_data, 'Piano - Bright')

    def test_get_selection_action_preset_combined(self):
        """Getting selection action for preset in combined context."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('combined')

        # Find a preset in the results
        preset_index = None
        for i, item in enumerate(manager.filtered_items):
            if item[1] == 'preset':
                preset_index = i
                break

        self.assertIsNotNone(preset_index)
        action = manager.get_selection_action(preset_index)

        self.assertIsNotNone(action)
        action_type, action_data = action
        self.assertEqual(action_type, 'set_preset')
        self.assertIsInstance(action_data, tuple)
        self.assertEqual(len(action_data), 2)  # (instrument_name, preset_name)

    def test_get_selection_action_invalid_index(self):
        """Getting selection action with invalid index should return None."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        action = manager.get_selection_action(999)

        self.assertIsNone(action)

    def test_get_selection_action_empty_results(self):
        """Getting selection action with no results should return None."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')
        manager.set_query("NOMATCH")

        action = manager.get_selection_action(0)

        self.assertIsNone(action)

    def test_has_results_true(self):
        """has_results should return True when there are results."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        self.assertTrue(manager.has_results())

    def test_has_results_false(self):
        """has_results should return False when there are no results."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')
        manager.set_query("NOMATCH")

        self.assertFalse(manager.has_results())

    def test_result_count(self):
        """result_count should return correct count."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        self.assertEqual(manager.result_count(), 3)

        manager.set_query("Pia")
        self.assertEqual(manager.result_count(), 1)

    def test_is_active_true(self):
        """is_active should return True when search is active."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('instrument')

        self.assertTrue(manager.is_active())

    def test_is_active_false(self):
        """is_active should return False when search is not active."""
        manager = SearchManager(self.mock_api)

        self.assertFalse(manager.is_active())

        manager.enter_search('instrument')
        manager.exit_search()

        self.assertFalse(manager.is_active())

    def test_preset_search_without_instrument(self):
        """Preset search without specifying instrument should return no results."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('preset')  # No instrument specified

        self.assertEqual(len(manager.filtered_items), 0)

    def test_combined_search_preset_display_format(self):
        """Combined search should format preset display names with instrument."""
        manager = SearchManager(self.mock_api)
        manager.enter_search('combined')

        # Find a preset item
        preset_items = [item for item in manager.filtered_items if item[1] == 'preset']

        self.assertGreater(len(preset_items), 0)

        # Check format: "PresetDisplayName (InstrumentName)"
        first_preset = preset_items[0]
        self.assertIn('(', first_preset[0])
        self.assertIn(')', first_preset[0])
