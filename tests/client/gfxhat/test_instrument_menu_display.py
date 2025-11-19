import unittest
from unittest.mock import Mock, MagicMock, patch

from gfxhat import touch
from pi_pianoteq.client.gfxhat.instrument_menu_display import InstrumentMenuDisplay
from pi_pianoteq.instrument.instrument import Instrument


class InstrumentMenuDisplayTestCase(unittest.TestCase):
    """Test InstrumentMenuDisplay specific behaviors."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_api.get_instruments.return_value = [
            Instrument("Piano", "Piano", "#000000", "#FFFFFF"),
            Instrument("Strings", "Strings", "#111111", "#EEEEEE"),
            Instrument("Guitar", "Guitar", "#222222", "#DDDDDD")
        ]
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#000000", "#FFFFFF")

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

    def test_get_menu_options_includes_instruments(self):
        """Menu options should include all instruments."""
        display = self.create_display()

        self.assertEqual(len(display.menu_options), 3)  # 3 instruments
        self.assertEqual(display.menu_options[0].name, "Piano")
        self.assertEqual(display.menu_options[1].name, "Strings")
        self.assertEqual(display.menu_options[2].name, "Guitar")

    def test_set_instrument_calls_api_and_exits(self):
        """Selecting an instrument should call API and exit menu."""
        display = self.create_display()

        display.set_instrument("Strings")

        self.mock_api.set_instrument.assert_called_once_with("Strings")
        self.on_exit.assert_called_once()

    def test_update_instrument_positions_on_current(self):
        """update_instrument should position menu on current instrument."""
        self.mock_api.get_current_instrument.return_value = Instrument("Guitar", "Guitar", "#222222", "#DDDDDD")
        display = self.create_display()

        display.update_instrument()

        # Should position on Guitar (index 2)
        self.assertEqual(display.current_menu_option, 2)

    def test_update_instrument_with_unknown_instrument(self):
        """update_instrument with unknown instrument should not crash."""
        self.mock_api.get_current_instrument.return_value = Instrument("Unknown", "Unknown", "#000000", "#FFFFFF")
        display = self.create_display()

        # Should not raise error
        display.update_instrument()

    def test_enter_held_opens_preset_menu_for_instrument(self):
        """ENTER held on instrument should call on_enter_preset_menu after threshold."""
        display = self.create_display()
        handler = display.get_handler()

        display.current_menu_option = 1  # Strings

        # Send held events to meet threshold (default: 2)
        handler(touch.ENTER, 'held')
        self.on_enter_preset_menu.assert_not_called()

        handler(touch.ENTER, 'held')
        self.on_enter_preset_menu.assert_called_once_with("Strings")


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

    def test_instrument_menu_options_are_callable(self):
        """Instrument menu options should have callable triggers."""
        display = self.create_display()

        # Get Piano option (index 0)
        piano_option = display.menu_options[0]

        # Should be able to trigger it
        piano_option.trigger()

        self.mock_api.set_instrument.assert_called_once_with("Piano")

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
        """ENTER held should work for all instrument options after threshold."""
        display = self.create_display()
        handler = display.get_handler()

        instruments = ["Piano", "Strings", "Guitar"]
        for i, instrument in enumerate(instruments):
            self.on_enter_preset_menu.reset_mock()

            display.current_menu_option = i
            # Send held events to meet threshold (default: 2)
            handler(touch.ENTER, 'held')
            self.on_enter_preset_menu.assert_not_called()

            handler(touch.ENTER, 'held')
            self.on_enter_preset_menu.assert_called_once_with(instrument)

            # Release to clean up held_count for next iteration
            handler(touch.ENTER, 'release')

    def test_update_instrument_updates_scroller(self):
        """update_instrument should update scrolling text."""
        self.mock_api.get_current_instrument.return_value = Instrument("Strings", "Strings", "#111111", "#EEEEEE")
        display = self.create_display()

        # Mock the scroller
        display.option_scroller = Mock()
        display.option_scroller.get_offset.return_value = 0

        display.update_instrument()

        # Should update scroller to Strings
        display.option_scroller.update_text.assert_called_once_with("Strings")
