import unittest
from unittest.mock import Mock, patch, MagicMock

from pi_pianoteq.client.gfxhat.preset_menu_display import PresetMenuDisplay


class PresetMenuDisplayTestCase(unittest.TestCase):
    """
    Tests for PresetMenuDisplay class.

    Tests the preset selection menu including:
    - Menu option generation from API
    - Preset selection triggering API calls
    - Current preset highlighting (context-aware)
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_api = Mock()
        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)
        self.mock_on_exit = Mock()

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_get_menu_options_creates_options_from_api(self, mock_image, mock_draw, mock_scroller):
        """Menu options should be created from API preset list."""
        self.mock_api.get_preset_names.return_value = ["Bright", "Dark", "Medium"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should create 3 menu options
        self.assertEqual(3, len(menu.menu_options))
        self.assertEqual("Bright", menu.menu_options[0].name)
        self.assertEqual("Dark", menu.menu_options[1].name)
        self.assertEqual("Medium", menu.menu_options[2].name)

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_set_preset_calls_api_and_exits(self, mock_image, mock_draw, mock_scroller):
        """Selecting a preset should call API and trigger exit callback."""
        self.mock_api.get_preset_names.return_value = ["Bright", "Dark"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        menu.set_preset("Dark")

        # Should call API with instrument name and preset name
        self.mock_api.set_preset.assert_called_once_with("Piano", "Dark")
        # Should trigger exit callback
        self.mock_on_exit.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_current_preset_highlighted_for_current_instrument(self, mock_image, mock_draw, mock_scroller):
        """
        Current preset should be highlighted when viewing current instrument.

        If user is viewing presets for the currently loaded instrument,
        the menu should automatically position on the current preset.
        """
        self.mock_api.get_current_instrument.return_value = "Piano"
        self.mock_api.get_current_preset.return_value = "Medium"
        self.mock_api.get_preset_names.return_value = ["Bright", "Dark", "Medium", "Soft"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"  # Viewing current instrument
        )

        # Should position on "Medium" (index 2)
        self.assertEqual(2, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_no_highlighting_for_different_instrument(self, mock_image, mock_draw, mock_scroller):
        """
        Current preset should NOT be highlighted when viewing different instrument.

        If user is browsing a different instrument's presets, the menu
        should start at the first preset (index 0), not the current preset
        of the currently loaded instrument.
        """
        self.mock_api.get_current_instrument.return_value = "Piano"
        self.mock_api.get_current_preset.return_value = "Medium"  # Piano preset
        self.mock_api.get_preset_names.return_value = ["Plucked", "Muted", "Sustained"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Strings"  # Viewing different instrument
        )

        # Should stay at default position (0) - not search for "Medium"
        self.assertEqual(0, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_current_preset_not_in_list(self, mock_image, mock_draw, mock_scroller):
        """
        Should handle gracefully if current preset not in list.

        This is an edge case that shouldn't happen in normal operation,
        but the code should not crash if API returns inconsistent data.
        """
        self.mock_api.get_current_instrument.return_value = "Piano"
        self.mock_api.get_current_preset.return_value = "NonExistent"
        self.mock_api.get_preset_names.return_value = ["Bright", "Dark", "Medium"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should stay at default position (0) if preset not found
        self.assertEqual(0, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_empty_preset_list(self, mock_image, mock_draw, mock_scroller):
        """Should handle empty preset list without crashing."""
        self.mock_api.get_preset_names.return_value = []

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        self.assertEqual(0, len(menu.menu_options))

    @patch('pi_pianoteq.client.gfxhat.preset_menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_stores_instrument_name(self, mock_image, mock_draw, mock_scroller):
        """Should store the instrument name for later use."""
        self.mock_api.get_preset_names.return_value = ["Bright"]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "TestInstrument"
        )

        self.assertEqual("TestInstrument", menu.instrument_name)


if __name__ == '__main__':
    unittest.main()
