import unittest
from unittest.mock import Mock, patch, MagicMock

from pi_pianoteq.client.gfxhat.gfxhat_client import GfxhatClient


@patch('pi_pianoteq.client.gfxhat.gfxhat_client.fonts')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.backlight')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.lcd')
@patch('pi_pianoteq.client.gfxhat.gfxhat_client.touch')
class GfxhatClientStateMachineTestCase(unittest.TestCase):
    """
    Tests for GfxhatClient state machine.

    Tests the complex state transitions between:
    - Loading mode (before API available)
    - Main display (instrument/preset view)
    - Instrument menu
    - Preset menu (from main or instrument menu)

    All hardware dependencies (LCD, touch, backlight) are mocked.
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.mock_api = Mock()
        self.mock_api.get_current_instrument.return_value = "Piano"
        self.mock_api.get_current_preset.return_value = "Bright"
        self.mock_api.get_current_preset_display_name.return_value = "Bright"
        self.mock_api.get_current_background_primary.return_value = "#FF0000"
        self.mock_api.get_current_background_secondary.return_value = "#0000FF"
        self.mock_api.get_instrument_names.return_value = ["Piano", "Strings"]
        self.mock_api.get_preset_names.return_value = ["Bright", "Dark"]

    def test_loading_mode_initialization(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Client should start in loading mode when api=None."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=None)

        self.assertTrue(client.loading_mode)
        self.assertIsNone(client.instrument_display)
        self.assertIsNone(client.menu_display)
        self.assertIsNone(client.preset_menu_display)
        self.assertIsNotNone(client.loading_display)

    def test_normal_mode_initialization(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Client should initialize displays when api provided."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)

        self.assertFalse(client.loading_mode)
        self.assertIsNotNone(client.instrument_display)
        self.assertIsNotNone(client.menu_display)
        self.mock_api.set_on_exit.assert_called_once()

    def test_get_display_in_loading_mode(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """get_display() should return loading display in loading mode."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=None)

        self.assertEqual(client.loading_display, client.get_display())

    def test_get_display_priority(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """
        get_display() should return displays in priority order:
        preset menu > instrument menu > main display
        """
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)

        # Default: main display
        self.assertEqual(client.instrument_display, client.get_display())

        # Instrument menu open
        client.menu_open = True
        self.assertEqual(client.menu_display, client.get_display())

        # Preset menu has highest priority
        client.preset_menu_open = True
        client.preset_menu_display = Mock()
        self.assertEqual(client.preset_menu_display, client.get_display())

    def test_on_enter_menu_transitions_state(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Opening instrument menu should transition state correctly."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)

        # Mock the displays to track method calls
        client.instrument_display.stop_scrolling = Mock()
        client.menu_display.update_instrument = Mock()
        client.menu_display.start_scrolling = Mock()

        client.on_enter_menu()

        self.assertTrue(client.menu_open)
        client.instrument_display.stop_scrolling.assert_called_once()
        client.menu_display.update_instrument.assert_called_once()
        client.menu_display.start_scrolling.assert_called_once()

    def test_on_exit_menu_returns_to_main(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Exiting instrument menu should return to main display."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)
        client.menu_open = True

        # Mock the displays
        client.menu_display.stop_scrolling = Mock()
        client.instrument_display.update_display = Mock()
        client.instrument_display.start_scrolling = Mock()

        client.on_exit_menu()

        self.assertFalse(client.menu_open)
        client.menu_display.stop_scrolling.assert_called_once()
        client.instrument_display.update_display.assert_called_once()
        client.instrument_display.start_scrolling.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.gfxhat_client.PresetMenuDisplay')
    def test_preset_menu_from_main_display(self, mock_preset_menu_class,
                                           mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Long press ENTER on main display should open preset menu for current instrument."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)
        client.instrument_display.stop_scrolling = Mock()

        mock_preset_menu = Mock()
        mock_preset_menu_class.return_value = mock_preset_menu

        client.on_enter_preset_menu_from_main()

        # Should stop main display scrolling
        client.instrument_display.stop_scrolling.assert_called_once()

        # Should create preset menu for current instrument
        self.mock_api.get_current_instrument.assert_called()
        mock_preset_menu_class.assert_called_once()
        created_instrument = mock_preset_menu_class.call_args[1]['instrument_name']
        self.assertEqual("Piano", created_instrument)

        # Should set state correctly
        self.assertTrue(client.preset_menu_open)
        self.assertEqual('main', client.preset_menu_source)

        # Should start preset menu scrolling
        mock_preset_menu.start_scrolling.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.gfxhat_client.PresetMenuDisplay')
    def test_preset_menu_from_instrument_menu(self, mock_preset_menu_class,
                                              mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Long press ENTER on instrument menu should open preset menu for highlighted instrument."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)
        client.menu_display.stop_scrolling = Mock()

        mock_preset_menu = Mock()
        mock_preset_menu_class.return_value = mock_preset_menu

        client.on_enter_preset_menu_from_instrument_menu("Strings")

        # Should stop menu scrolling (not instrument display)
        client.menu_display.stop_scrolling.assert_called_once()

        # Should create preset menu for specified instrument
        created_instrument = mock_preset_menu_class.call_args[1]['instrument_name']
        self.assertEqual("Strings", created_instrument)

        # Should track source as instrument_menu
        self.assertEqual('instrument_menu', client.preset_menu_source)

    def test_exit_preset_menu_returns_to_main(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Exiting preset menu from main display should return to main display."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)
        client.preset_menu_open = True
        client.preset_menu_source = 'main'
        client.preset_menu_display = Mock()

        client.instrument_display.update_display = Mock()
        client.instrument_display.start_scrolling = Mock()

        client.on_exit_preset_menu()

        self.assertFalse(client.preset_menu_open)
        client.preset_menu_display.stop_scrolling.assert_called_once()
        client.instrument_display.update_display.assert_called_once()
        client.instrument_display.start_scrolling.assert_called_once()

    def test_exit_preset_menu_returns_to_instrument_menu(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """Exiting preset menu from instrument menu should return to instrument menu."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)
        client.preset_menu_open = True
        client.preset_menu_source = 'instrument_menu'
        client.preset_menu_display = Mock()

        client.menu_display.start_scrolling = Mock()
        client.instrument_display.update_display = Mock()

        client.on_exit_preset_menu()

        self.assertFalse(client.preset_menu_open)
        client.preset_menu_display.stop_scrolling.assert_called_once()

        # Should return to menu, not update main display
        client.menu_display.start_scrolling.assert_called_once()
        client.instrument_display.update_display.assert_not_called()

    def test_cleanup_stops_all_scrolling(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """cleanup() should stop scrolling on all displays."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=self.mock_api)

        # Mock stop_scrolling on all displays
        client.instrument_display.stop_scrolling = Mock()
        client.menu_display.stop_scrolling = Mock()
        client.preset_menu_display = Mock()
        client.preset_menu_display.stop_scrolling = Mock()

        client.cleanup()

        client.instrument_display.stop_scrolling.assert_called_once()
        client.menu_display.stop_scrolling.assert_called_once()
        client.preset_menu_display.stop_scrolling.assert_called_once()
        self.assertTrue(client.interrupt)

    def test_cleanup_handles_uninitialized_displays(self, mock_touch, mock_lcd, mock_backlight, mock_fonts):
        """cleanup() should handle None displays gracefully."""
        mock_lcd.dimensions.return_value = (128, 64)
        mock_fonts.BitbuntuFull = "/fake/font.ttf"

        client = GfxhatClient(api=None)

        # Should not raise error when displays are None
        try:
            client.cleanup()
        except AttributeError:
            self.fail("cleanup() raised AttributeError for None displays")

        self.assertTrue(client.interrupt)


if __name__ == '__main__':
    unittest.main()
