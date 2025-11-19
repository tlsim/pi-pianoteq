import unittest
from unittest.mock import Mock, patch, MagicMock

from pi_pianoteq.client.gfxhat.preset_menu_display import PresetMenuDisplay
from pi_pianoteq.instrument.preset import Preset
from pi_pianoteq.instrument.instrument import Instrument


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

    def _configure_scroller_mock(self, mock_scroller_class):
        """Configure ScrollingText mock to return proper values."""
        mock_scroller = Mock()
        mock_scroller.needs_scrolling = False
        mock_scroller.get_offset.return_value = 0
        mock_scroller_class.return_value = mock_scroller
        return mock_scroller

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_get_menu_options_creates_options_from_api(self, mock_image, mock_draw, mock_scroller_class):
        """Menu options should include Randomise plus options from API preset list."""
        self._configure_scroller_mock(mock_scroller_class)
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark"),
            Preset("Medium", "Medium")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should create 4 menu options: Randomise + 3 presets
        self.assertEqual(4, len(menu.menu_options))
        self.assertEqual("Randomise", menu.menu_options[0].name)
        self.assertEqual("Bright", menu.menu_options[1].name)
        self.assertEqual("Dark", menu.menu_options[2].name)
        self.assertEqual("Medium", menu.menu_options[3].name)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_set_preset_calls_api_and_exits(self, mock_image, mock_draw, mock_scroller):
        """Selecting a preset should call API and trigger exit callback."""
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        menu.set_preset("Dark")

        # Should call API with instrument name and preset name
        self.mock_api.set_preset.assert_called_once_with("Piano", "Dark")
        # Should trigger exit callback
        self.mock_on_exit.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_current_preset_highlighted_for_current_instrument(self, mock_image, mock_draw, mock_scroller):
        """
        Current preset should be highlighted when viewing current instrument.

        If user is viewing presets for the currently loaded instrument,
        the menu should automatically position on the current preset.
        """
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#000000", "#FFFFFF")
        self.mock_api.get_current_preset.return_value = Preset("Medium", "Medium")
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark"),
            Preset("Medium", "Medium"),
            Preset("Soft", "Soft")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"  # Viewing current instrument
        )

        # Should position on "Medium" (index 3: Randomise at 0, then Bright, Dark, Medium)
        self.assertEqual(3, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_no_highlighting_for_different_instrument(self, mock_image, mock_draw, mock_scroller):
        """
        Current preset should NOT be highlighted when viewing different instrument.

        If user is browsing a different instrument's presets, the menu
        should start at the first preset (index 0), not the current preset
        of the currently loaded instrument.
        """
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#000000", "#FFFFFF")
        self.mock_api.get_current_preset.return_value = Preset("Medium", "Medium")
        self.mock_api.get_presets.return_value = [
            Preset("Plucked", "Plucked"),
            Preset("Muted", "Muted"),
            Preset("Sustained", "Sustained")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Strings"  # Viewing different instrument
        )

        # Should stay at default position (0) - not search for "Medium"
        self.assertEqual(0, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_current_preset_not_in_list(self, mock_image, mock_draw, mock_scroller):
        """
        Should handle gracefully if current preset not in list.

        This is an edge case that shouldn't happen in normal operation,
        but the code should not crash if API returns inconsistent data.
        """
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#000000", "#FFFFFF")
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_current_preset.return_value = Preset("NonExistent", "NonExistent")
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark"),
            Preset("Medium", "Medium")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should stay at default position (0) if preset not found
        self.assertEqual(0, menu.current_menu_option)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_empty_preset_list(self, mock_image, mock_draw, mock_scroller):
        """Should have Randomise option even with empty preset list."""
        self.mock_api.get_presets.return_value = []
        self._configure_scroller_mock(mock_scroller)

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should have 1 option (Randomise) even with no presets
        self.assertEqual(1, len(menu.menu_options))
        self.assertEqual("Randomise", menu.menu_options[0].name)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_stores_instrument_name(self, mock_image, mock_draw, mock_scroller):
        """Should store the instrument name for later use."""
        self.mock_api.get_presets.return_value = [Preset("Bright", "Bright")]
        self._configure_scroller_mock(mock_scroller)

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "TestInstrument"
        )

        self.assertEqual("TestInstrument", menu.instrument_name)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    @patch('gfxhat.touch')
    def test_ignore_first_enter_release(self, mock_touch, mock_image, mock_draw, mock_scroller):
        """First ENTER release should be ignored to prevent spurious selection."""
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]
        self._configure_scroller_mock(mock_scroller)
        mock_touch.ENTER = 0

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        handler = menu.get_handler()

        # First ENTER release should be ignored
        handler(mock_touch.ENTER, 'release')

        # API should not be called
        self.mock_api.set_preset.assert_not_called()
        self.mock_on_exit.assert_not_called()

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    @patch('gfxhat.touch')
    def test_second_enter_release_triggers_selection(self, mock_touch, mock_image, mock_draw, mock_scroller):
        """Second ENTER release should trigger preset selection."""
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]
        self._configure_scroller_mock(mock_scroller)
        mock_touch.ENTER = 0

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        handler = menu.get_handler()

        # First release ignored
        handler(mock_touch.ENTER, 'release')

        # Second release should trigger selection
        handler(mock_touch.ENTER, 'release')

        # Should have called API and exited
        self.mock_api.set_preset.assert_called_once()
        self.mock_on_exit.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_preset_selected_flag_set_on_selection(self, mock_image, mock_draw, mock_scroller):
        """preset_selected flag should be set when user selects a preset."""
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]
        self._configure_scroller_mock(mock_scroller)

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Initially False
        self.assertFalse(menu.preset_selected)

        # Select a preset
        menu.set_preset("Dark")

        # Should be True
        self.assertTrue(menu.preset_selected)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_uses_display_names_but_stores_raw_names(self, mock_image, mock_draw, mock_scroller):
        """Menu should show display names but use raw names for API calls."""
        # Piano presets have "Piano " prefix stripped in display_name
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_presets.return_value = [
            Preset("Piano Bright", "Bright"),
            Preset("Piano Dark", "Dark")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # First option is Randomise (index 0), presets start at index 1
        self.assertEqual("Randomise", menu.menu_options[0].name)
        # Menu options should show display names (without prefix)
        self.assertEqual("Bright", menu.menu_options[1].name)
        self.assertEqual("Dark", menu.menu_options[2].name)

        # But stored raw names should include prefix
        self.assertEqual("Piano Bright", menu.menu_options[1].options[0])
        self.assertEqual("Piano Dark", menu.menu_options[2].options[0])

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_randomise_option_appears_first(self, mock_image, mock_draw, mock_scroller):
        """Test that 'Randomise' appears as first menu option."""
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        self.assertEqual("Randomise", menu.menu_options[0].name)

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_randomise_calls_api_and_closes_menu(self, mock_image, mock_draw, mock_scroller):
        """Test that selecting Randomise randomizes and closes menu."""
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("Dark", "Dark")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        menu.randomize_preset()

        self.mock_api.randomize_current_preset.assert_called_once()
        self.assertTrue(menu.preset_selected)
        self.mock_on_exit.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.menu_display.ScrollingText')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.new')
    def test_filters_special_presets(self, mock_image, mock_draw, mock_scroller):
        """Test that presets starting with __ are filtered out."""
        self._configure_scroller_mock(mock_scroller)
        self.mock_api.get_presets.return_value = [
            Preset("Bright", "Bright"),
            Preset("__SPECIAL__", "Special"),
            Preset("Dark", "Dark")
        ]

        menu = PresetMenuDisplay(
            self.mock_api, 128, 64, self.mock_font,
            self.mock_on_exit, "Piano"
        )

        # Should have Randomise + 2 regular presets (special preset filtered)
        self.assertEqual(3, len(menu.menu_options))
        self.assertEqual("Randomise", menu.menu_options[0].name)
        self.assertEqual("Bright", menu.menu_options[1].name)
        self.assertEqual("Dark", menu.menu_options[2].name)


if __name__ == '__main__':
    unittest.main()
