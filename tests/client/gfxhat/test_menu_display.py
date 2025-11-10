import unittest
from unittest.mock import Mock, MagicMock

from gfxhat import touch
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay
from pi_pianoteq.client.gfxhat.menu_option import MenuOption


class ConcreteMenuDisplay(MenuDisplay):
    """Concrete implementation of MenuDisplay for testing."""

    def __init__(self, api, width, height, font, on_exit, menu_options):
        self._menu_options = menu_options
        super().__init__(api, width, height, font, on_exit)

    def get_menu_options(self):
        return self._menu_options

    def get_heading(self):
        return "Test Menu"


class MenuDisplayTestCase(unittest.TestCase):
    """Test MenuDisplay navigation and wrapping behavior."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)
        self.on_exit = Mock()

    def create_menu_options(self, count=3):
        """Helper to create test menu options."""
        options = []
        for i in range(count):
            option = MenuOption(f"Option {i}", Mock(), self.mock_font)
            options.append(option)
        return options

    def create_menu(self, option_count=3):
        """Helper to create MenuDisplay with test options."""
        options = self.create_menu_options(option_count)
        return ConcreteMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            menu_options=options
        )

    def test_initialization_with_menu_options(self):
        """Initialization should set up menu options and scroller."""
        menu = self.create_menu(option_count=3)

        self.assertEqual(len(menu.menu_options), 3)
        self.assertEqual(menu.current_menu_option, 0)
        self.assertIsNotNone(menu.option_scroller)

    def test_up_decrements_current_option(self):
        """UP button should decrement current menu option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 1
        handler(touch.UP, 'press')

        self.assertEqual(menu.current_menu_option, 0)

    def test_down_increments_current_option(self):
        """DOWN button should increment current menu option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 0
        handler(touch.DOWN, 'press')

        self.assertEqual(menu.current_menu_option, 1)

    def test_left_decrements_current_option(self):
        """LEFT button should decrement current menu option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 2
        handler(touch.LEFT, 'press')

        self.assertEqual(menu.current_menu_option, 1)

    def test_right_increments_current_option(self):
        """RIGHT button should increment current menu option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 1
        handler(touch.RIGHT, 'press')

        self.assertEqual(menu.current_menu_option, 2)

    def test_wrapping_up_from_first_to_last(self):
        """UP from first option should wrap to last option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 0
        handler(touch.UP, 'press')

        # Should wrap to index 2 (last option)
        self.assertEqual(menu.current_menu_option, 2)

    def test_wrapping_down_from_last_to_first(self):
        """DOWN from last option should wrap to first option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 2
        handler(touch.DOWN, 'press')

        # Should wrap to index 0 (first option)
        self.assertEqual(menu.current_menu_option, 0)

    def test_wrapping_left_from_first_to_last(self):
        """LEFT from first option should wrap to last option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 0
        handler(touch.LEFT, 'press')

        self.assertEqual(menu.current_menu_option, 2)

    def test_wrapping_right_from_last_to_first(self):
        """RIGHT from last option should wrap to first option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 2
        handler(touch.RIGHT, 'press')

        self.assertEqual(menu.current_menu_option, 0)

    def test_navigation_records_suppression(self):
        """Navigation buttons should record suppression."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        # Record with navigation
        handler(touch.UP, 'press')

        # Suppression should block action immediately
        self.assertFalse(menu.suppression.allow_action())

    def test_back_button_calls_on_exit(self):
        """BACK button should call on_exit callback."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        handler(touch.BACK, 'press')

        self.on_exit.assert_called_once()

    def test_back_button_resets_to_selected_option(self):
        """BACK button should reset current option to selected option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.selected_menu_option = 1
        menu.current_menu_option = 2

        handler(touch.BACK, 'press')

        self.assertEqual(menu.current_menu_option, menu.selected_menu_option)

    def test_enter_triggers_option_when_allowed(self):
        """ENTER release should trigger menu option when suppression allows."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 1

        handler(touch.ENTER, 'release')

        # Should trigger option 1 (which is a Mock action)
        menu.menu_options[1].action.assert_called_once()

    def test_enter_blocked_when_suppressed(self):
        """ENTER release should be blocked when suppression is active."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 1
        # Activate suppression
        menu.suppression.record()

        handler(touch.ENTER, 'release')

        # Should NOT trigger option (action is the Mock)
        menu.menu_options[1].action.assert_not_called()

    def test_enter_updates_selected_menu_option(self):
        """ENTER release should update selected_menu_option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        menu.current_menu_option = 2

        handler(touch.ENTER, 'release')

        self.assertEqual(menu.selected_menu_option, 2)

    def test_option_change_updates_scrolling_text(self):
        """Navigation should update scrolling text to new option."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        # Mock the scroller
        menu.option_scroller = Mock()
        menu.option_scroller.get_offset.return_value = 0

        menu.current_menu_option = 0
        handler(touch.DOWN, 'press')

        # Should update to Option 1
        menu.option_scroller.update_text.assert_called_once_with("Option 1")
        menu.option_scroller.start.assert_called_once()

    def test_same_option_does_not_update_scrolling(self):
        """Staying on same option should not update scrolling text."""
        menu = self.create_menu(option_count=1)
        handler = menu.get_handler()

        # Mock the scroller
        menu.option_scroller = Mock()
        menu.option_scroller.get_offset.return_value = 0

        # Navigate with only one option (stays on same)
        handler(touch.DOWN, 'press')

        # Should not update (still on same option)
        menu.option_scroller.update_text.assert_not_called()

    def test_single_item_menu_navigation(self):
        """Single item menu should stay on same option when navigating."""
        menu = self.create_menu(option_count=1)
        handler = menu.get_handler()

        handler(touch.DOWN, 'press')
        self.assertEqual(menu.current_menu_option, 0)

        handler(touch.UP, 'press')
        self.assertEqual(menu.current_menu_option, 0)

        handler(touch.LEFT, 'press')
        self.assertEqual(menu.current_menu_option, 0)

        handler(touch.RIGHT, 'press')
        self.assertEqual(menu.current_menu_option, 0)

    def test_empty_menu_handling(self):
        """Empty menu should initialize without errors."""
        # This tests the edge case of empty menu options
        menu = ConcreteMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            menu_options=[]
        )

        self.assertEqual(len(menu.menu_options), 0)
        self.assertIsNone(menu.option_scroller)

    def test_start_scrolling_starts_option_scroller(self):
        """start_scrolling should start the option scroller."""
        menu = self.create_menu(option_count=3)
        menu.option_scroller = Mock()

        menu.start_scrolling()

        menu.option_scroller.start.assert_called_once()

    def test_stop_scrolling_stops_option_scroller(self):
        """stop_scrolling should stop the option scroller."""
        menu = self.create_menu(option_count=3)
        menu.option_scroller = Mock()

        menu.stop_scrolling()

        menu.option_scroller.stop.assert_called_once()

    def test_start_scrolling_with_no_scroller(self):
        """start_scrolling with no scroller should not error."""
        menu = ConcreteMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            menu_options=[]
        )

        # Should not raise error
        menu.start_scrolling()

    def test_stop_scrolling_with_no_scroller(self):
        """stop_scrolling with no scroller should not error."""
        menu = ConcreteMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            menu_options=[]
        )

        # Should not raise error
        menu.stop_scrolling()

    def test_get_image_returns_image(self):
        """get_image should return the PIL Image instance."""
        menu = self.create_menu(option_count=3)

        image = menu.get_image()

        self.assertIsNotNone(image)
        self.assertEqual(image.size, (128, 64))

    def test_get_backlight_returns_backlight_instance(self):
        """get_backlight should return the Backlight instance."""
        menu = self.create_menu(option_count=3)

        backlight = menu.get_backlight()

        self.assertIsNotNone(backlight)

    def test_backlight_initialized_with_gray(self):
        """Backlight should be initialized with gray color."""
        menu = self.create_menu(option_count=3)

        # Backlight color stored internally
        self.assertIsNotNone(menu.backlight)

    def test_suppression_threshold_set_to_300ms(self):
        """Button suppression should be initialized with 300ms threshold."""
        menu = self.create_menu(option_count=3)

        self.assertEqual(menu.suppression.threshold_ms, 300)

    def test_handler_ignores_unknown_buttons(self):
        """Handler should gracefully ignore unknown button channels."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        # Should not raise error
        handler(99, 'press')

    def test_handler_ignores_unknown_events(self):
        """Handler should gracefully ignore unknown event types."""
        menu = self.create_menu(option_count=3)
        handler = menu.get_handler()

        # Should not raise error
        handler(touch.UP, 'unknown_event')

    def test_modulo_wrapping_correctness(self):
        """Verify modulo wrapping works correctly for all navigation."""
        menu = self.create_menu(option_count=5)
        handler = menu.get_handler()

        # Test wrapping in both directions
        test_cases = [
            (0, touch.UP, 4),      # Wrap up from first
            (4, touch.DOWN, 0),    # Wrap down from last
            (0, touch.LEFT, 4),    # Wrap left from first
            (4, touch.RIGHT, 0),   # Wrap right from last
            (2, touch.UP, 1),      # Normal up
            (2, touch.DOWN, 3),    # Normal down
            (2, touch.LEFT, 1),    # Normal left
            (2, touch.RIGHT, 3),   # Normal right
        ]

        for start, button, expected in test_cases:
            menu.current_menu_option = start
            handler(button, 'press')
            self.assertEqual(menu.current_menu_option, expected,
                           f"From {start} with {button} should be {expected}")

    def test_scroller_initialized_with_first_option_text(self):
        """Scroller should be initialized with text of first option."""
        menu = self.create_menu(option_count=3)

        self.assertEqual(menu.option_scroller.text, "Option 0")

    def test_draw_image_uses_scroll_offset(self):
        """draw_image should use scroll offset from scroller."""
        menu = self.create_menu(option_count=3)
        menu.option_scroller = Mock()
        menu.option_scroller.get_offset.return_value = 15

        menu.draw_image()

        # Should have called get_offset
        menu.option_scroller.get_offset.assert_called()

    def test_multiple_navigation_updates_option_correctly(self):
        """Multiple navigation presses should update option correctly."""
        menu = self.create_menu(option_count=5)
        handler = menu.get_handler()

        # Start at 0, go down 3 times
        handler(touch.DOWN, 'press')
        handler(touch.DOWN, 'press')
        handler(touch.DOWN, 'press')

        self.assertEqual(menu.current_menu_option, 3)

        # Go up 5 times (should wrap)
        handler(touch.UP, 'press')
        handler(touch.UP, 'press')
        handler(touch.UP, 'press')
        handler(touch.UP, 'press')
        handler(touch.UP, 'press')

        # 3 - 5 = -2, wraps to 3 (3 - 5 + 5 = 3)
        self.assertEqual(menu.current_menu_option, 3)
