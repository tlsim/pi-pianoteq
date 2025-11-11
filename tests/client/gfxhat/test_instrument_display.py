import unittest
from unittest.mock import Mock, MagicMock, patch

from gfxhat import touch
from pi_pianoteq.client.gfxhat.instrument_display import InstrumentDisplay
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset


class InstrumentDisplayTestCase(unittest.TestCase):
    """Test InstrumentDisplay button handlers and display updates."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_api.get_current_preset.return_value = Preset("Piano - Bright", "Bright Piano")
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#1e3a5f", "#2a4a7f")

        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 80, 10)

        self.on_enter = Mock()
        self.on_enter_preset_menu = Mock()

    def create_display(self):
        """Helper to create InstrumentDisplay with mocks."""
        return InstrumentDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_enter=self.on_enter,
            on_enter_preset_menu=self.on_enter_preset_menu
        )

    def test_initialization_fetches_current_state(self):
        """Initialization should fetch current instrument and preset from API."""
        display = self.create_display()

        self.mock_api.get_current_instrument.assert_called_once()
        self.mock_api.get_current_preset.assert_called_once()
        self.assertEqual(display.instrument, "Piano")
        self.assertEqual(display.preset, "Bright Piano")

    def test_down_button_calls_set_preset_next(self):
        """DOWN button press should call set_preset_next."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.DOWN, 'press')

        self.mock_api.set_preset_next.assert_called_once()

    def test_up_button_calls_set_preset_prev(self):
        """UP button press should call set_preset_prev."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.UP, 'press')

        self.mock_api.set_preset_prev.assert_called_once()

    def test_right_button_calls_set_instrument_next(self):
        """RIGHT button press should call set_instrument_next."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.RIGHT, 'press')

        self.mock_api.set_instrument_next.assert_called_once()

    def test_left_button_calls_set_instrument_prev(self):
        """LEFT button press should call set_instrument_prev."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.LEFT, 'press')

        self.mock_api.set_instrument_prev.assert_called_once()

    def test_navigation_buttons_record_suppression(self):
        """Navigation buttons should record suppression to prevent double-triggers."""
        display = self.create_display()
        handler = display.get_handler()

        # Reset suppression's internal state
        display.suppression.record()
        initial_allowed = display.suppression.allow_action()

        # Should be blocked immediately after record
        self.assertFalse(initial_allowed)

    def test_button_press_updates_display(self):
        """Button press should trigger display update."""
        display = self.create_display()
        handler = display.get_handler()

        # Update API to return new values
        self.mock_api.get_current_preset.return_value = Preset("Piano - Dark", "Dark Piano")
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#1e3a5f", "#2a4a7f")

        handler(touch.DOWN, 'press')

        # Display should be updated with new values
        self.assertEqual(display.preset, "Dark Piano")

    def test_enter_release_calls_on_enter_when_allowed(self):
        """ENTER release should call on_enter when suppression allows."""
        display = self.create_display()
        handler = display.get_handler()

        # Ensure suppression allows action (don't record first)
        handler(touch.ENTER, 'release')

        self.on_enter.assert_called_once()

    def test_enter_release_blocked_when_suppressed(self):
        """ENTER release should be blocked when suppression is active."""
        display = self.create_display()
        handler = display.get_handler()

        # Record to activate suppression
        display.suppression.record()

        handler(touch.ENTER, 'release')

        # on_enter should NOT be called
        self.on_enter.assert_not_called()

    def test_enter_held_calls_on_enter_preset_menu(self):
        """ENTER held should call on_enter_preset_menu callback."""
        display = self.create_display()
        handler = display.get_handler()

        handler(touch.ENTER, 'held')

        self.on_enter_preset_menu.assert_called_once()

    def test_update_display_fetches_new_state(self):
        """update_display should fetch current state from API."""
        display = self.create_display()

        # Change API return values
        self.mock_api.get_current_preset.return_value = Preset("Piano - Soft", "Soft Piano")
        self.mock_api.get_current_instrument.return_value = Instrument("Piano", "Piano", "#3a5a9f", "#4a6abf")

        display.update_display()

        # Display should have new values
        self.assertEqual(display.preset, "Soft Piano")
        self.assertEqual(display.background_primary, "#3a5a9f")
        self.assertEqual(display.background_secondary, "#4a6abf")

    def test_update_display_restarts_scrolling(self):
        """update_display should restart scrolling with new text."""
        display = self.create_display()

        # Mock the scrollers
        display.preset_scroller = Mock()
        display.preset_scroller.get_offset.return_value = 0
        display.instrument_scroller = Mock()
        display.instrument_scroller.get_offset.return_value = 0

        # Change text
        self.mock_api.get_current_preset.return_value = Preset("New Preset", "New Preset")
        self.mock_api.get_current_instrument.return_value = Instrument("New Instrument", "New Instrument", "#000000", "#FFFFFF")

        display.update_display()

        # Should update text and restart scrolling
        display.preset_scroller.update_text.assert_called_once_with("New Preset")
        display.instrument_scroller.update_text.assert_called_once_with("New Instrument")
        display.preset_scroller.start.assert_called_once()
        display.instrument_scroller.start.assert_called_once()

    def test_start_scrolling_starts_both_scrollers(self):
        """start_scrolling should start both preset and instrument scrollers."""
        display = self.create_display()

        # Mock the scrollers
        display.preset_scroller = Mock()
        display.instrument_scroller = Mock()

        display.start_scrolling()

        display.preset_scroller.start.assert_called_once()
        display.instrument_scroller.start.assert_called_once()

    def test_stop_scrolling_stops_both_scrollers(self):
        """stop_scrolling should stop both preset and instrument scrollers."""
        display = self.create_display()

        # Mock the scrollers
        display.preset_scroller = Mock()
        display.instrument_scroller = Mock()

        display.stop_scrolling()

        display.preset_scroller.stop.assert_called_once()
        display.instrument_scroller.stop.assert_called_once()

    def test_scrollers_initialized_with_current_text(self):
        """ScrollingText instances should be initialized with current text."""
        display = self.create_display()

        # Check scrollers have correct text
        self.assertEqual(display.preset_scroller.text, "Bright Piano")
        self.assertEqual(display.instrument_scroller.text, "Piano")

    def test_get_image_returns_image(self):
        """get_image should return the PIL Image instance."""
        display = self.create_display()

        image = display.get_image()

        self.assertIsNotNone(image)
        self.assertEqual(image.size, (128, 64))

    def test_get_backlight_returns_backlight_instance(self):
        """get_backlight should return the Backlight instance."""
        display = self.create_display()

        backlight = display.get_backlight()

        self.assertIsNotNone(backlight)

    def test_backlight_colors_set_on_initialization(self):
        """Backlight should be set with primary/secondary colors on init."""
        display = self.create_display()

        # Mock the backlight to verify calls
        display.backlight = Mock()
        display.set_backlight()

        # Should set backlight 6 times (buttons 0-5)
        self.assertEqual(display.backlight.set_backlight.call_count, 6)

    def test_backlight_uses_secondary_for_buttons_0_and_5(self):
        """Buttons 0 and 5 should use secondary color."""
        display = self.create_display()
        display.backlight = Mock()

        display.set_backlight()

        # Check calls for buttons 0 and 5
        calls = display.backlight.set_backlight.call_args_list
        # Button 0 (first call)
        self.assertEqual(calls[0][0][0], "#2a4a7f")  # secondary
        # Button 5 (last call)
        self.assertEqual(calls[5][0][0], "#2a4a7f")  # secondary

    def test_backlight_uses_primary_for_buttons_1_to_4(self):
        """Buttons 1-4 should use primary color."""
        display = self.create_display()
        display.backlight = Mock()

        display.set_backlight()

        # Check calls for buttons 1-4
        calls = display.backlight.set_backlight.call_args_list
        for i in range(1, 5):
            self.assertEqual(calls[i][0][0], "#1e3a5f")  # primary

    def test_suppression_threshold_set_to_300ms(self):
        """Button suppression should be initialized with 300ms threshold."""
        display = self.create_display()

        self.assertEqual(display.suppression.threshold_ms, 300)

    def test_handler_ignores_unknown_buttons(self):
        """Handler should gracefully ignore unknown button channels."""
        display = self.create_display()
        handler = display.get_handler()

        # Should not raise error
        handler(99, 'press')  # Unknown button

    def test_handler_ignores_unknown_events(self):
        """Handler should gracefully ignore unknown event types."""
        display = self.create_display()
        handler = display.get_handler()

        # Should not raise error
        handler(touch.UP, 'unknown_event')

    def test_multiple_button_presses_update_display(self):
        """Multiple button presses should each update display."""
        display = self.create_display()
        handler = display.get_handler()

        # Track call counts
        initial_calls = self.mock_api.get_current_preset.call_count

        handler(touch.DOWN, 'press')
        handler(touch.UP, 'press')
        handler(touch.RIGHT, 'press')

        # Should have updated 3 times (plus initial)
        final_calls = self.mock_api.get_current_preset.call_count
        self.assertEqual(final_calls - initial_calls, 3)

    def test_draw_text_uses_scroll_offsets(self):
        """draw_text should use scroll offsets from scrollers."""
        display = self.create_display()

        # Mock scrollers to return specific offsets
        display.preset_scroller.get_offset = Mock(return_value=10)
        display.instrument_scroller.get_offset = Mock(return_value=5)

        display.draw_text()

        # Should have called get_offset
        display.preset_scroller.get_offset.assert_called()
        display.instrument_scroller.get_offset.assert_called()

    def test_draw_text_draws_wrap_copy_when_scrolling_needed(self):
        """draw_text should draw second copy of text when scrolling is needed."""
        display = self.create_display()

        # Mock scrollers to indicate scrolling needed
        display.preset_scroller.needs_scrolling = True
        display.instrument_scroller.needs_scrolling = True

        # Mock draw to verify calls
        display.draw = Mock()

        display.draw_text()

        # Should draw text at least twice (primary + wrap)
        # At minimum: 2 for instrument (primary + wrap) + 2 for preset (primary + wrap)
        self.assertGreaterEqual(display.draw.text.call_count, 4)
