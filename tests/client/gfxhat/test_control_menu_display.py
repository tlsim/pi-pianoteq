import unittest
from unittest.mock import Mock, patch

from gfxhat import touch
from pi_pianoteq.client.gfxhat.control_menu_display import ControlMenuDisplay


class ControlMenuDisplayTestCase(unittest.TestCase):
    """Test ControlMenuDisplay specific behaviors."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)
        self.on_exit = Mock()
        self.on_select_instrument = Mock()

    def create_display(self):
        """Helper to create ControlMenuDisplay with mocks."""
        return ControlMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            on_select_instrument=self.on_select_instrument
        )

    def test_get_menu_options_includes_instrument_and_shutdown(self):
        """Menu options should include Select Instrument and Shut down."""
        display = self.create_display()

        self.assertEqual(len(display.menu_options), 2)
        self.assertEqual(display.menu_options[0].name, "Select Instrument")
        self.assertEqual(display.menu_options[1].name, "Shut down")

    def test_select_instrument_option_calls_callback(self):
        """Selecting 'Select Instrument' should call on_select_instrument."""
        display = self.create_display()

        # Trigger the first menu option (Select Instrument)
        display.menu_options[0].trigger()

        self.on_select_instrument.assert_called_once()

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_shutdown_option_triggers_menu(self, mock_touch):
        """Selecting shutdown option should trigger shutdown menu."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 1  # Shut down

        handler(touch.ENTER, 'release')

        # Should have opened shutdown menu
        self.assertTrue(display.shutdown_menu_open)

    def test_get_image_returns_shutdown_display_when_menu_open(self):
        """get_image should return shutdown display image when menu is open."""
        display = self.create_display()

        display.shutdown_menu_open = True
        display.shutdown_display.get_image = Mock(return_value="shutdown_image")

        image = display.get_image()

        self.assertEqual(image, "shutdown_image")

    def test_get_image_returns_main_image_when_menu_closed(self):
        """get_image should return main menu image when shutdown menu closed."""
        display = self.create_display()

        display.shutdown_menu_open = False

        image = display.get_image()

        self.assertIsNotNone(image)
        self.assertEqual(image, display.image)

    def test_get_backlight_returns_shutdown_backlight_when_menu_open(self):
        """get_backlight should return shutdown backlight when menu is open."""
        display = self.create_display()

        display.shutdown_menu_open = True
        display.shutdown_display.get_backlight = Mock(return_value="shutdown_backlight")

        backlight = display.get_backlight()

        self.assertEqual(backlight, "shutdown_backlight")

    def test_get_backlight_returns_main_backlight_when_menu_closed(self):
        """get_backlight should return main backlight when shutdown menu closed."""
        display = self.create_display()

        display.shutdown_menu_open = False

        backlight = display.get_backlight()

        self.assertEqual(backlight, display.backlight)

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_on_enter_menu_opens_shutdown_menu(self, mock_touch):
        """on_enter_menu should set shutdown_menu_open flag."""
        display = self.create_display()

        display.on_enter_menu()

        self.assertTrue(display.shutdown_menu_open)

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_on_exit_menu_closes_shutdown_menu(self, mock_touch):
        """on_exit_menu should clear shutdown_menu_open flag."""
        display = self.create_display()

        display.shutdown_menu_open = True
        display.on_exit_menu()

        self.assertFalse(display.shutdown_menu_open)

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_update_handler_sets_shutdown_handler_when_menu_open(self, mock_touch):
        """update_handler should set shutdown handler when menu is open."""
        display = self.create_display()
        display.shutdown_menu_open = True

        mock_shutdown_handler = Mock()
        display.shutdown_display.get_handler = Mock(return_value=mock_shutdown_handler)

        display.update_handler()

        # Should have set handler 6 times (one per button)
        self.assertEqual(mock_touch.on.call_count, 6)

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_update_handler_sets_main_handler_when_menu_closed(self, mock_touch):
        """update_handler should set main handler when menu is closed."""
        display = self.create_display()
        display.shutdown_menu_open = False

        display.update_handler()

        # Should have set handler 6 times (one per button)
        self.assertEqual(mock_touch.on.call_count, 6)

    def test_shutdown_display_initialized(self):
        """ShutdownDisplay should be initialized."""
        display = self.create_display()

        self.assertIsNotNone(display.shutdown_display)

    def test_shutdown_menu_open_flag_initialized_false(self):
        """shutdown_menu_open flag should be initialized to False."""
        display = self.create_display()

        self.assertFalse(display.shutdown_menu_open)

    @patch('pi_pianoteq.client.gfxhat.control_menu_display.touch')
    def test_shutdown_option_is_callable(self, mock_touch):
        """Shutdown option should have callable trigger."""
        display = self.create_display()

        # Get shutdown option (last)
        shutdown_option = display.menu_options[1]

        # Should be able to trigger it
        shutdown_option.trigger()

        # Should have set shutdown_menu_open
        self.assertTrue(display.shutdown_menu_open)

    def test_base_handler_still_works(self):
        """Base MenuDisplay handler functionality should still work."""
        display = self.create_display()
        handler = display.get_handler()

        # Test basic navigation
        display.current_menu_option = 0
        handler(touch.DOWN, 'press')

        self.assertEqual(display.current_menu_option, 1)

    def test_back_button_exits_menu(self):
        """BACK button should exit the control menu."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.BACK, 'press')

        self.on_exit.assert_called_once()

    def test_get_heading(self):
        """get_heading should return 'Menu:'."""
        display = self.create_display()

        self.assertEqual(display.get_heading(), "Menu:")
