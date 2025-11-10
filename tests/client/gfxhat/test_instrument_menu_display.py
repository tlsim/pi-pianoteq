import unittest
from unittest.mock import Mock, MagicMock, patch

from gfxhat import touch
from pi_pianoteq.client.gfxhat.instrument_menu_display import InstrumentMenuDisplay


class InstrumentMenuDisplayTestCase(unittest.TestCase):
    """Test InstrumentMenuDisplay specific behaviors."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_api.get_instrument_names.return_value = ["Piano", "Strings", "Guitar"]
        self.mock_api.get_current_instrument.return_value = "Piano"

        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)

        self.on_exit = Mock()
        self.on_enter_preset_menu = Mock()

    def create_display(self):
        """Helper to create InstrumentMenuDisplay with mocks."""
        return InstrumentMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            on_enter_preset_menu=self.on_enter_preset_menu
        )

    def test_get_menu_options_includes_instruments_and_shutdown(self):
        """Menu options should include all instruments plus shutdown."""
        display = self.create_display()

        self.assertEqual(len(display.menu_options), 4)  # 3 instruments + shutdown
        self.assertEqual(display.menu_options[0].name, "Piano")
        self.assertEqual(display.menu_options[1].name, "Strings")
        self.assertEqual(display.menu_options[2].name, "Guitar")
        self.assertEqual(display.menu_options[3].name, "Shut down")

    def test_set_instrument_calls_api_and_exits(self):
        """Selecting an instrument should call API and exit menu."""
        display = self.create_display()

        display.set_instrument("Strings")

        self.mock_api.set_instrument.assert_called_once_with("Strings")
        self.on_exit.assert_called_once()

    def test_update_instrument_positions_on_current(self):
        """update_instrument should position menu on current instrument."""
        self.mock_api.get_current_instrument.return_value = "Guitar"
        display = self.create_display()

        display.update_instrument()

        # Should position on Guitar (index 2)
        self.assertEqual(display.current_menu_option, 2)

    def test_update_instrument_with_unknown_instrument(self):
        """update_instrument with unknown instrument should not crash."""
        self.mock_api.get_current_instrument.return_value = "Unknown"
        display = self.create_display()

        # Should not raise error
        display.update_instrument()

    def test_enter_held_opens_preset_menu_for_instrument(self):
        """ENTER held on instrument should call on_enter_preset_menu."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 1  # Strings

        handler(touch.ENTER, 'held')

        self.on_enter_preset_menu.assert_called_once_with("Strings")

    def test_enter_held_on_shutdown_does_nothing(self):
        """ENTER held on 'Shut down' should not open preset menu."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 3  # Shut down

        handler(touch.ENTER, 'held')

        self.on_enter_preset_menu.assert_not_called()

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_shutdown_option_triggers_menu(self, mock_touch):
        """Selecting shutdown option should trigger shutdown menu."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 3  # Shut down

        handler(touch.ENTER, 'release')

        # Should have opened shutdown menu
        self.assertTrue(display.menu_open)

    def test_get_image_returns_shutdown_display_when_menu_open(self):
        """get_image should return shutdown display image when menu is open."""
        display = self.create_display()

        display.menu_open = True
        display.shutdown_display.get_image = Mock(return_value="shutdown_image")

        image = display.get_image()

        self.assertEqual(image, "shutdown_image")

    def test_get_image_returns_main_image_when_menu_closed(self):
        """get_image should return main menu image when shutdown menu closed."""
        display = self.create_display()

        display.menu_open = False

        image = display.get_image()

        self.assertIsNotNone(image)
        self.assertEqual(image, display.image)

    def test_get_backlight_returns_shutdown_backlight_when_menu_open(self):
        """get_backlight should return shutdown backlight when menu is open."""
        display = self.create_display()

        display.menu_open = True
        display.shutdown_display.get_backlight = Mock(return_value="shutdown_backlight")

        backlight = display.get_backlight()

        self.assertEqual(backlight, "shutdown_backlight")

    def test_get_backlight_returns_main_backlight_when_menu_closed(self):
        """get_backlight should return main backlight when shutdown menu closed."""
        display = self.create_display()

        display.menu_open = False

        backlight = display.get_backlight()

        self.assertEqual(backlight, display.backlight)

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_on_enter_menu_opens_shutdown_menu(self, mock_touch):
        """on_enter_menu should set menu_open flag."""
        display = self.create_display()

        display.on_enter_menu()

        self.assertTrue(display.menu_open)

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_on_exit_menu_closes_shutdown_menu(self, mock_touch):
        """on_exit_menu should clear menu_open flag."""
        display = self.create_display()

        display.menu_open = True
        display.on_exit_menu()

        self.assertFalse(display.menu_open)

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_update_handler_sets_shutdown_handler_when_menu_open(self, mock_touch):
        """update_handler should set shutdown handler when menu is open."""
        display = self.create_display()
        display.menu_open = True

        mock_shutdown_handler = Mock()
        display.shutdown_display.get_handler = Mock(return_value=mock_shutdown_handler)

        display.update_handler()

        # Should have set handler 6 times (one per button)
        self.assertEqual(mock_touch.on.call_count, 6)

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_update_handler_sets_main_handler_when_menu_closed(self, mock_touch):
        """update_handler should set main handler when menu is closed."""
        display = self.create_display()
        display.menu_open = False

        display.update_handler()

        # Should have set handler 6 times (one per button)
        self.assertEqual(mock_touch.on.call_count, 6)

    def test_base_handler_still_works(self):
        """Base MenuDisplay handler functionality should still work."""
        display = self.create_display()
        handler = display.get_handler()

        # Test basic navigation
        display.current_menu_option = 0
        handler(touch.DOWN, 'press')

        self.assertEqual(display.current_menu_option, 1)

    def test_back_button_exits_menu(self):
        """BACK button should still exit the instrument menu."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.BACK, 'press')

        self.on_exit.assert_called_once()

    def test_enter_release_triggers_instrument_selection(self):
        """ENTER release should trigger instrument selection."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 1  # Strings

        handler(touch.ENTER, 'release')

        # Should have called set_instrument and exited
        self.mock_api.set_instrument.assert_called_once_with("Strings")
        self.on_exit.assert_called_once()

    def test_shutdown_display_initialized(self):
        """ShutdownDisplay should be initialized."""
        display = self.create_display()

        self.assertIsNotNone(display.shutdown_display)

    def test_menu_open_flag_initialized_false(self):
        """menu_open flag should be initialized to False."""
        display = self.create_display()

        self.assertFalse(display.menu_open)

    def test_instrument_menu_options_are_callable(self):
        """Instrument menu options should have callable triggers."""
        display = self.create_display()

        # Get Piano option (index 0)
        piano_option = display.menu_options[0]

        # Should be able to trigger it
        piano_option.trigger()

        self.mock_api.set_instrument.assert_called_once_with("Piano")

    @patch('pi_pianoteq.client.gfxhat.instrument_menu_display.touch')
    def test_shutdown_option_is_callable(self, mock_touch):
        """Shutdown option should have callable trigger."""
        display = self.create_display()

        # Get shutdown option (last)
        shutdown_option = display.menu_options[-1]

        # Should be able to trigger it
        shutdown_option.trigger()

        # Should have set menu_open
        self.assertTrue(display.menu_open)

    def test_multiple_instruments_all_selectable(self):
        """All instrument options should be selectable."""
        display = self.create_display()
        handler = display.get_handler()

        instruments = ["Piano", "Strings", "Guitar"]
        for i, instrument in enumerate(instruments):
            self.mock_api.set_instrument.reset_mock()
            self.on_exit.reset_mock()

            display.current_menu_option = i
            handler(touch.ENTER, 'release')

            self.mock_api.set_instrument.assert_called_once_with(instrument)
            self.on_exit.assert_called_once()

    def test_enter_held_with_different_instruments(self):
        """ENTER held should work for all instrument options."""
        display = self.create_display()
        handler = display.get_handler()

        instruments = ["Piano", "Strings", "Guitar"]
        for i, instrument in enumerate(instruments):
            self.on_enter_preset_menu.reset_mock()

            display.current_menu_option = i
            handler(touch.ENTER, 'held')

            self.on_enter_preset_menu.assert_called_once_with(instrument)

    def test_update_instrument_updates_scroller(self):
        """update_instrument should update scrolling text."""
        self.mock_api.get_current_instrument.return_value = "Strings"
        display = self.create_display()

        # Mock the scroller
        display.option_scroller = Mock()
        display.option_scroller.get_offset.return_value = 0

        display.update_instrument()

        # Should update scroller to Strings
        display.option_scroller.update_text.assert_called_once_with("Strings")
