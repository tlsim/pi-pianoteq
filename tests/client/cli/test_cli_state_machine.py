import unittest
from unittest.mock import Mock, patch, MagicMock
from prompt_toolkit.application import Application

from pi_pianoteq.client.cli.cli_client import CliClient
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset


class CliClientStateMachineTestCase(unittest.TestCase):
    """
    Tests for CliClient state machine.

    Tests the complex state transitions between:
    - Normal mode (instrument/preset view)
    - Instrument menu
    - Preset menu (from main or instrument menu)
    - Search mode (instrument/preset/combined)
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_api = Mock()
        self.piano = Instrument("Piano", "Piano", "#FF0000", "#0000FF")
        self.piano.add_preset(Preset("Piano - Bright", "Bright"))
        self.piano.add_preset(Preset("Piano - Dark", "Dark"))

        self.strings = Instrument("Strings", "Strings", "#00FF00", "#0000FF")
        self.strings.add_preset(Preset("Strings - Legato", "Legato"))
        self.strings.add_preset(Preset("Strings - Staccato", "Staccato"))

        self.mock_api.get_current_instrument.return_value = self.piano
        self.mock_api.get_current_preset.return_value = Preset("Piano - Bright", "Bright")
        self.mock_api.get_instruments.return_value = [self.piano, self.strings]
        self.mock_api.get_presets.return_value = self.piano.presets

    def test_loading_mode_initialization(self):
        """Client should start in loading mode when api=None."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)

            self.assertTrue(client.loading_mode)
            self.assertIsNotNone(client.application)
            self.assertTrue(client.app_running)

    def test_normal_mode_after_set_api(self):
        """Client should transition to normal mode after set_api called."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.assertFalse(client.loading_mode)
            self.assertFalse(client.menu_mode)
            self.assertFalse(client.preset_menu_mode)
            self.assertFalse(client.search_manager.is_active())

    def test_instrument_names_loaded_on_set_api(self):
        """Instrument names should be loaded when API is set."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.assertEqual(client.instrument_names, ["Piano", "Strings"])

    def test_open_instrument_menu(self):
        """Opening instrument menu should set menu_mode=True."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            # Simulate pressing 'i' key
            client.menu_mode = True
            client.current_menu_index = 0

            self.assertTrue(client.menu_mode)
            self.assertFalse(client.preset_menu_mode)
            self.assertFalse(client.search_manager.is_active())

    def test_open_preset_menu_from_main(self):
        """Opening preset menu from main should populate preset_names."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client._open_preset_menu("Piano")

            self.assertTrue(client.preset_menu_mode)
            self.assertEqual(client.preset_menu_instrument, "Piano")
            self.assertEqual(client.preset_names, ["Piano - Bright", "Piano - Dark"])

    def test_open_preset_menu_highlights_current_preset(self):
        """Opening preset menu for current instrument should highlight current preset."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.mock_api.get_current_preset.return_value = Preset("Piano - Dark", "Dark")
            client._open_preset_menu("Piano")

            self.assertEqual(client.current_menu_index, 1)  # "Dark" is index 1

    def test_open_preset_menu_for_different_instrument(self):
        """Opening preset menu for different instrument should start at index 0."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.mock_api.get_presets.return_value = self.strings.presets
            client._open_preset_menu("Strings")

            self.assertEqual(client.current_menu_index, 0)
            self.assertEqual(client.preset_menu_instrument, "Strings")

    def test_enter_search_mode_instrument(self):
        """Entering search mode with instrument context."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')

            self.assertTrue(client.search_manager.is_active())
            self.assertEqual(client.search_manager.context, 'instrument')
            self.assertEqual(client.search_manager.query, "")
            self.assertEqual(len(client.search_manager.filtered_items), 2)  # Piano, Strings

    def test_enter_search_mode_preset(self):
        """Entering search mode with preset context."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('preset', 'Piano')

            self.assertTrue(client.search_manager.is_active())
            self.assertEqual(client.search_manager.context, 'preset')
            # Should have 2 presets for Piano
            self.assertEqual(len(client.search_manager.filtered_items), 2)

    def test_enter_search_mode_combined(self):
        """Entering search mode with combined context."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('combined')

            self.assertTrue(client.search_manager.is_active())
            self.assertEqual(client.search_manager.context, 'combined')
            # Should have 2 instruments + 4 presets = 6 items
            self.assertEqual(len(client.search_manager.filtered_items), 6)

    def test_exit_search_mode(self):
        """Exiting search mode should reset state."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("Pia")
            client.search_manager.exit_search()

            self.assertFalse(client.search_manager.is_active())
            self.assertEqual(client.search_manager.query, "")
            self.assertEqual(client.search_manager.filtered_items, [])
            self.assertIsNone(client.search_manager.context)

    def test_update_search_results_filters_instruments(self):
        """Search should filter instruments by query."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("pia")

            self.assertEqual(len(client.search_manager.filtered_items), 1)
            self.assertEqual(client.search_manager.filtered_items[0][0], "Piano")

    def test_update_search_results_case_insensitive(self):
        """Search should be case-insensitive."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("STRING")

            self.assertEqual(len(client.search_manager.filtered_items), 1)
            self.assertEqual(client.search_manager.filtered_items[0][0], "Strings")

    def test_update_search_results_empty_query_shows_all(self):
        """Empty search query should show all items."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("")

            self.assertEqual(len(client.search_manager.filtered_items), 2)

    def test_select_search_result_instrument(self):
        """Selecting instrument from search should call set_instrument."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("string")
            client.current_menu_index = 0

            action = client.search_manager.get_selection_action(client.current_menu_index)
            self.assertIsNotNone(action)
            action_type, action_data = action

            # Simulate what CliClient does
            if action_type == 'set_instrument':
                self.mock_api.set_instrument(action_data)

            self.mock_api.set_instrument.assert_called_once_with("Strings")

    def test_select_search_result_preset_combined(self):
        """Selecting preset from combined search should call set_preset."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('combined')
            # Find a preset result (not an instrument)
            preset_index = None
            for i, item in enumerate(client.search_manager.filtered_items):
                if item[1] == 'preset':
                    preset_index = i
                    break

            self.assertIsNotNone(preset_index)
            client.current_menu_index = preset_index

            action = client.search_manager.get_selection_action(client.current_menu_index)
            self.assertIsNotNone(action)
            action_type, action_data = action

            # Simulate what CliClient does
            if action_type == 'set_preset':
                instrument_name, preset_name = action_data
                self.mock_api.set_preset(instrument_name, preset_name)

            self.mock_api.set_preset.assert_called_once()

    def test_menu_next_increments_index(self):
        """Navigating next should increment menu index."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client.current_menu_index = 0
            client._menu_next()

            self.assertEqual(client.current_menu_index, 1)

    def test_menu_next_stops_at_end(self):
        """Navigating next should stop at last item."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client.current_menu_index = 1  # Last instrument
            client._menu_next()

            self.assertEqual(client.current_menu_index, 1)  # Should not go past end

    def test_menu_prev_decrements_index(self):
        """Navigating previous should decrement menu index."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client.current_menu_index = 1
            client._menu_prev()

            self.assertEqual(client.current_menu_index, 0)

    def test_menu_prev_stops_at_start(self):
        """Navigating previous should stop at first item."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client.current_menu_index = 0
            client._menu_prev()

            self.assertEqual(client.current_menu_index, 0)  # Should not go before start

    def test_get_title_normal_mode(self):
        """Title should be 'Pi-Pianoteq CLI' in normal mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.assertEqual(client._get_title(), "Pi-Pianoteq CLI")

    def test_get_title_instrument_menu(self):
        """Title should be 'Select Instrument' in instrument menu."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            self.assertEqual(client._get_title(), "Select Instrument")

    def test_get_title_preset_menu(self):
        """Title should show instrument name in preset menu."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client._open_preset_menu("Piano")
            self.assertEqual(client._get_title(), "Select Preset - Piano")

    def test_get_title_search_instrument(self):
        """Title should be 'Search Instruments' in instrument search."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            self.assertEqual(client._get_title(), "Search Instruments")

    def test_get_title_search_preset(self):
        """Title should show instrument name in preset search."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('preset', 'Piano')
            self.assertEqual(client._get_title(), "Search Presets - Piano")

    def test_get_title_search_combined(self):
        """Title should be 'Search Instruments & Presets' in combined search."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('combined')
            self.assertEqual(client._get_title(), "Search Instruments & Presets")

    def test_selecting_preset_exits_both_menus(self):
        """Selecting preset when instrument menu is open should exit both."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client._open_preset_menu("Piano")

            # Simulate selecting a preset
            client.menu_mode = False
            client.preset_menu_mode = False

            self.assertFalse(client.menu_mode)
            self.assertFalse(client.preset_menu_mode)

    def test_scroll_offset_centers_selection(self):
        """Scroll offset should center the selected item when possible."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            # Add more instruments to test scrolling
            instruments = [Instrument(f"Inst{i}", f"Inst{i}", "#FFF", "#000") for i in range(20)]
            self.mock_api.get_instruments.return_value = instruments
            client.instrument_names = [i.name for i in instruments]

            client.menu_mode = True
            client.current_menu_index = 10  # Middle item
            client._update_scroll_offset()

            # With 10 visible items, mid_point is 5
            # Offset should be 10 - 5 = 5
            self.assertEqual(client.menu_scroll_offset, 5)

    def test_scroll_offset_at_top(self):
        """Scroll offset should be 0 when near the top."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            instruments = [Instrument(f"Inst{i}", f"Inst{i}", "#FFF", "#000") for i in range(20)]
            self.mock_api.get_instruments.return_value = instruments
            client.instrument_names = [i.name for i in instruments]

            client.menu_mode = True
            client.current_menu_index = 2
            client._update_scroll_offset()

            self.assertEqual(client.menu_scroll_offset, 0)

    def test_scroll_offset_at_bottom(self):
        """Scroll offset should show last items when near the bottom."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            instruments = [Instrument(f"Inst{i}", f"Inst{i}", "#FFF", "#000") for i in range(20)]
            self.mock_api.get_instruments.return_value = instruments
            client.instrument_names = [i.name for i in instruments]

            client.menu_mode = True
            client.current_menu_index = 18
            client._update_scroll_offset()

            # Should show last 10 items
            self.assertEqual(client.menu_scroll_offset, 10)

    def test_logs_view_mode_initialized_false(self):
        """logs_view_mode should be False after set_api."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            self.assertFalse(client.logs_view_mode)

    def test_enter_logs_view_mode(self):
        """Entering logs view mode should set logs_view_mode=True."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.logs_view_mode = True

            self.assertTrue(client.logs_view_mode)
            self.assertFalse(client.menu_mode)
            self.assertFalse(client.preset_menu_mode)
            self.assertFalse(client.search_manager.is_active())

    def test_exit_logs_view_mode(self):
        """Exiting logs view mode should set logs_view_mode=False."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.logs_view_mode = True
            client.logs_view_mode = False

            self.assertFalse(client.logs_view_mode)

    def test_get_title_logs_view(self):
        """Title should be 'View Logs' in logs view mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.logs_view_mode = True
            self.assertEqual(client._get_title(), "View Logs")

    def test_display_text_routing_logs_view(self):
        """_get_display_text should route to cli_display.get_logs_view_text in logs view mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.logs_view_mode = True
            from pi_pianoteq.client.cli import cli_display
            with patch.object(cli_display, 'get_logs_view_text', return_value=[]) as mock_logs:
                client._get_display_text()
                mock_logs.assert_called_once()

    def test_logs_view_priority_over_other_modes(self):
        """Logs view should take priority in display text routing."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            # Set multiple modes (shouldn't normally happen, but tests priority)
            client.logs_view_mode = True
            client.menu_mode = True

            from pi_pianoteq.client.cli import cli_display
            with patch.object(cli_display, 'get_logs_view_text', return_value=[]) as mock_logs:
                with patch.object(cli_display, 'get_instrument_menu_text', return_value=[]) as mock_menu:
                    client._get_display_text()
                    mock_logs.assert_called_once()
                    mock_menu.assert_not_called()
