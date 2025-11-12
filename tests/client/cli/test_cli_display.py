import unittest
from unittest.mock import Mock, patch

from pi_pianoteq.client.cli.cli_client import CliClient
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset
from prompt_toolkit.application import Application


class CliClientDisplayTestCase(unittest.TestCase):
    """
    Tests for CliClient display text generation.

    Tests that the correct formatted text is generated for:
    - Normal mode display
    - Instrument menu
    - Preset menu
    - Search results
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_api = Mock()
        self.piano = Instrument("Piano", "Piano", "#FF0000", "#0000FF")
        self.piano.add_preset(Preset("Piano - Bright", "Bright"))
        self.piano.add_preset(Preset("Piano - Dark", "Dark"))

        self.strings = Instrument("Strings", "Strings", "#00FF00", "#0000FF")
        self.strings.add_preset(Preset("Strings - Legato", "Legato"))

        self.mock_api.get_current_instrument.return_value = self.piano
        self.mock_api.get_current_preset.return_value = Preset("Piano - Bright", "Bright")
        self.mock_api.get_instruments.return_value = [self.piano, self.strings]
        self.mock_api.get_presets.return_value = self.piano.presets

    def test_get_normal_text_contains_instrument(self):
        """Normal mode display should show current instrument name."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            text = client._get_normal_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Piano", text_string)

    def test_get_normal_text_contains_preset(self):
        """Normal mode display should show current preset display name."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            text = client._get_normal_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Bright", text_string)

    def test_get_normal_text_shows_controls(self):
        """Normal mode display should show control instructions."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            text = client._get_normal_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Up/Down", text_string)
            self.assertIn("Left/Right", text_string)
            self.assertIn("Open instrument menu", text_string)
            self.assertIn("Open preset menu", text_string)
            self.assertIn("Search", text_string)

    def test_get_instrument_menu_text_shows_instruments(self):
        """Instrument menu should show all instrument names."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            text = client._get_instrument_menu_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Piano", text_string)
            self.assertIn("Strings", text_string)

    def test_get_instrument_menu_text_highlights_selection(self):
        """Instrument menu should highlight the selected item."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            client.current_menu_index = 0
            text = client._get_instrument_menu_text()

            # Should contain "> Piano" for highlighted item
            text_string = ''.join([item[1] for item in text])
            self.assertIn("> Piano", text_string)

    def test_get_preset_menu_text_shows_presets(self):
        """Preset menu should show all preset display names."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client._open_preset_menu("Piano")
            text = client._get_preset_menu_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Bright", text_string)
            self.assertIn("Dark", text_string)

    def test_get_preset_menu_text_highlights_selection(self):
        """Preset menu should highlight the selected item."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client._open_preset_menu("Piano")
            client.current_menu_index = 1
            text = client._get_preset_menu_text()

            # Should contain "> Dark" for highlighted item
            text_string = ''.join([item[1] for item in text])
            self.assertIn("> Dark", text_string)

    def test_get_search_text_shows_query(self):
        """Search display should show the current search query."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("Pia")

            text = client._get_search_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("Pia", text_string)
            self.assertIn("Search:", text_string)

    def test_get_search_text_shows_result_count(self):
        """Search display should show the number of results."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("Pia")

            text = client._get_search_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("1 result(s)", text_string)

    def test_get_search_text_shows_no_matches(self):
        """Search display should show 'No matches found' for no results."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            client.search_manager.set_query("xyz")

            text = client._get_search_text()
            text_string = ''.join([item[1] for item in text])

            self.assertIn("No matches found", text_string)

    def test_get_search_text_combined_shows_type_indicators(self):
        """Combined search should show [I] and [P] type indicators."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('combined')
            text = client._get_search_text()
            text_string = ''.join([item[1] for item in text])

            # Should have [I] for instruments and [P] for presets
            self.assertIn("[I]", text_string)
            self.assertIn("[P]", text_string)

    def test_get_search_text_instrument_only_no_type_indicators(self):
        """Instrument-only search should not show type indicators."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            text = client._get_search_text()
            text_string = ''.join([item[1] for item in text])

            # Should not have type indicators for single-context search
            # Count occurrences - there might be [I] in "[I]f" or similar
            # So we check that Piano appears without [I] prefix
            lines = text_string.split('\n')
            piano_lines = [l for l in lines if 'Piano' in l]
            # At least one line should have Piano without [I] before it
            has_plain_piano = any('Piano' in l and '[I] Piano' not in l for l in piano_lines)
            self.assertTrue(has_plain_piano or '[I]' not in text_string)

    def test_display_text_routing_normal_mode(self):
        """_get_display_text should route to _get_normal_text in normal mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            with patch.object(client, '_get_normal_text', return_value=[]) as mock_normal:
                client._get_display_text()
                mock_normal.assert_called_once()

    def test_display_text_routing_instrument_menu(self):
        """_get_display_text should route to _get_instrument_menu_text in menu mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.menu_mode = True
            with patch.object(client, '_get_instrument_menu_text', return_value=[]) as mock_menu:
                client._get_display_text()
                mock_menu.assert_called_once()

    def test_display_text_routing_preset_menu(self):
        """_get_display_text should route to _get_preset_menu_text in preset menu mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client._open_preset_menu("Piano")
            with patch.object(client, '_get_preset_menu_text', return_value=[]) as mock_preset:
                client._get_display_text()
                mock_preset.assert_called_once()

    def test_display_text_routing_search_mode(self):
        """_get_display_text should route to _get_search_text in search mode."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            client.search_manager.enter_search('instrument')
            with patch.object(client, '_get_search_text', return_value=[]) as mock_search:
                client._get_display_text()
                mock_search.assert_called_once()

    def test_formatted_text_structure_normal_mode(self):
        """Normal mode text should return list of (style, text) tuples."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            text = client._get_normal_text()

            self.assertIsInstance(text, list)
            self.assertTrue(all(isinstance(item, tuple) for item in text))
            self.assertTrue(all(len(item) == 2 for item in text))
            self.assertTrue(all(isinstance(item[0], str) and isinstance(item[1], str) for item in text))

    def test_scroll_indicators_shown_when_needed(self):
        """Menu should show scroll indicators when items exceed visible area."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            # Add many instruments to force scrolling
            instruments = [Instrument(f"Inst{i:02d}", f"Inst{i:02d}", "#FFF", "#000") for i in range(20)]
            self.mock_api.get_instruments.return_value = instruments
            client.instrument_names = [i.name for i in instruments]

            client.menu_mode = True
            client.current_menu_index = 10
            client._update_scroll_offset()

            text = client._get_instrument_menu_text()
            text_string = ''.join([item[1] for item in text])

            # Should show "..." indicators when scrolling
            self.assertIn("...", text_string)

    def test_truncates_long_names(self):
        """Display should truncate very long instrument/preset names."""
        with patch.object(Application, 'run'):
            client = CliClient(api=None)
            client.set_api(self.mock_api)

            # Create instrument with very long name
            long_name = "A" * 100
            long_instrument = Instrument(long_name, long_name, "#FFF", "#000")
            self.mock_api.get_instruments.return_value = [long_instrument]
            client.instrument_names = [long_name]

            client.menu_mode = True
            text = client._get_instrument_menu_text()
            text_string = ''.join([item[1] for item in text])

            # Should not contain the full 100-character name
            self.assertNotIn("A" * 100, text_string)
            # But should contain a truncated version
            self.assertIn("A" * 50, text_string)
