import unittest
from unittest.mock import Mock, patch
import time
import threading

from pi_pianoteq.client.gfxhat.scrolling_text import ScrollingText


class ScrollingTextTestCase(unittest.TestCase):
    """Test ScrollingText thread management and scrolling behavior."""

    def setUp(self):
        """Set up common mock font for tests."""
        self.mock_font = Mock()

    def test_short_text_no_scrolling_needed(self):
        """Short text that fits should not need scrolling."""
        self.mock_font.getbbox.return_value = (0, 0, 80, 10)  # Width 80, fits in 100

        scroller = ScrollingText("Short", self.mock_font, max_width=100)

        self.assertFalse(scroller.needs_scrolling)
        self.assertEqual(scroller.text_width, 80)

    def test_long_text_needs_scrolling(self):
        """Long text that doesn't fit should need scrolling."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)  # Width 150, exceeds 100

        scroller = ScrollingText("Very long text", self.mock_font, max_width=100)

        self.assertTrue(scroller.needs_scrolling)
        self.assertEqual(scroller.text_width, 150)

    def test_thread_starts_when_scrolling_needed(self):
        """Thread should start when text needs scrolling."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.1, update_interval=0.05)
        scroller.start()

        # Thread should be alive
        self.assertIsNotNone(scroller.scroll_thread)
        self.assertTrue(scroller.scroll_thread.is_alive())

        # Cleanup
        scroller.stop()

    def test_thread_does_not_start_when_not_needed(self):
        """Thread should not start when text doesn't need scrolling."""
        self.mock_font.getbbox.return_value = (0, 0, 80, 10)

        scroller = ScrollingText("Short", self.mock_font, max_width=100)
        scroller.start()

        # Thread should not be created
        self.assertIsNone(scroller.scroll_thread)

    def test_initial_delay_before_scrolling(self):
        """Offset should remain 0 during initial delay period."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.2, update_interval=0.05)
        scroller.start()

        # Check immediately - should be 0 during initial delay
        time.sleep(0.05)
        self.assertEqual(scroller.get_offset(), 0)

        # Cleanup
        scroller.stop()

    def test_offset_increments_by_scroll_speed(self):
        """Offset should increment by scroll_speed after initial delay."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 scroll_speed=5, initial_delay=0.05, update_interval=0.05)
        scroller.start()

        # Wait for initial delay + several updates
        time.sleep(0.25)

        offset = scroller.get_offset()
        # Should have scrolled (at least one update, but allow for timing variance)
        self.assertGreater(offset, 0)
        # Should be multiple of scroll_speed
        self.assertEqual(offset % 5, 0)

        # Cleanup
        scroller.stop()

    def test_offset_wraps_at_wrap_point(self):
        """Offset should wrap to 0 at text_width + wrap_gap."""
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)  # Small text for faster wrap

        scroller = ScrollingText("Text", self.mock_font, max_width=40,
                                 scroll_speed=10, wrap_gap=10,
                                 initial_delay=0.05, update_interval=0.05)
        scroller.start()

        # Wrap point = 50 (text_width) + 10 (wrap_gap) = 60
        # With scroll_speed=10, should wrap after 6 updates
        # Wait enough time for wrapping
        time.sleep(0.5)

        offset = scroller.get_offset()
        # Should have wrapped at least once, so offset < wrap_point
        self.assertLess(offset, 60)

        # Cleanup
        scroller.stop()

    def test_stop_sets_flag_and_joins_thread(self):
        """Stop should set stop flag and join thread."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.1, update_interval=0.05)
        scroller.start()
        self.assertTrue(scroller.scroll_thread.is_alive())

        scroller.stop()

        # Thread should be stopped
        self.assertFalse(scroller.scroll_thread.is_alive())
        # Stop flag should be set
        self.assertTrue(scroller.stop_flag.is_set())

    def test_stop_resets_offset_to_zero(self):
        """Stop should reset scroll offset to 0."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 scroll_speed=5, initial_delay=0.05, update_interval=0.05)
        scroller.start()

        # Wait for scrolling to start
        time.sleep(0.15)
        self.assertGreater(scroller.get_offset(), 0)

        scroller.stop()

        # Offset should be reset to 0
        self.assertEqual(scroller.get_offset(), 0)

    def test_stop_when_not_started_does_not_error(self):
        """Calling stop when thread not started should not raise error."""
        self.mock_font.getbbox.return_value = (0, 0, 80, 10)

        scroller = ScrollingText("Short", self.mock_font, max_width=100)

        # Should not raise error
        scroller.stop()

        self.assertEqual(scroller.get_offset(), 0)

    def test_start_when_already_running_does_nothing(self):
        """Calling start when already running should not create new thread."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.1, update_interval=0.05)
        scroller.start()
        first_thread = scroller.scroll_thread

        scroller.start()  # Second call

        # Should be same thread
        self.assertIs(scroller.scroll_thread, first_thread)

        # Cleanup
        scroller.stop()

    def test_update_text_stops_and_restarts_thread(self):
        """update_text should stop running thread, update, and restart."""
        self.mock_font.getbbox.side_effect = [
            (0, 0, 150, 10),  # Initial: long text
            (0, 0, 180, 10),  # After update: different long text
        ]

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.05, update_interval=0.05)
        scroller.start()
        time.sleep(0.1)  # Let it start scrolling
        self.assertTrue(scroller.scroll_thread.is_alive())

        scroller.update_text("Different long text")

        # Should have new text dimensions
        self.assertEqual(scroller.text, "Different long text")
        self.assertEqual(scroller.text_width, 180)
        # Offset should be reset
        self.assertEqual(scroller.get_offset(), 0)
        # Thread should still be running
        self.assertTrue(scroller.scroll_thread.is_alive())

        # Cleanup
        scroller.stop()

    def test_update_text_recalculates_needs_scrolling(self):
        """update_text should recalculate needs_scrolling flag."""
        self.mock_font.getbbox.side_effect = [
            (0, 0, 150, 10),  # Initial: needs scrolling
            (0, 0, 80, 10),   # After update: no scrolling needed
        ]

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.05, update_interval=0.05)
        self.assertTrue(scroller.needs_scrolling)
        scroller.start()
        time.sleep(0.1)

        scroller.update_text("Short")

        # Should no longer need scrolling
        self.assertFalse(scroller.needs_scrolling)
        # Thread should be stopped
        self.assertFalse(scroller.scroll_thread.is_alive())

    def test_update_text_when_not_running_does_not_restart(self):
        """update_text when not running should just update without starting."""
        self.mock_font.getbbox.side_effect = [
            (0, 0, 150, 10),  # Initial
            (0, 0, 180, 10),  # After update
        ]

        scroller = ScrollingText("Long text", self.mock_font, max_width=100)
        # Don't start

        scroller.update_text("Different text")

        # Should have new text
        self.assertEqual(scroller.text, "Different text")
        # Thread should not be running
        self.assertIsNone(scroller.scroll_thread)

    def test_get_offset_is_thread_safe(self):
        """get_offset should use lock for thread safety."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 scroll_speed=1, initial_delay=0.05, update_interval=0.01)
        scroller.start()

        # Rapid reads from different "threads" (main thread repeatedly)
        offsets = []
        for _ in range(20):
            offsets.append(scroller.get_offset())
            time.sleep(0.01)

        # Should get valid offsets without crashes
        self.assertTrue(all(isinstance(o, int) for o in offsets))
        self.assertTrue(all(o >= 0 for o in offsets))

        # Cleanup
        scroller.stop()

    def test_rapid_start_stop_cycles(self):
        """Rapid start/stop cycles should not cause errors or thread leaks."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.01, update_interval=0.01)

        for _ in range(5):
            scroller.start()
            time.sleep(0.02)
            scroller.stop()

        # Final state should be stopped with offset 0
        self.assertEqual(scroller.get_offset(), 0)
        if scroller.scroll_thread:
            self.assertFalse(scroller.scroll_thread.is_alive())

    def test_thread_cleanup_prevents_memory_leak(self):
        """Threads should be properly cleaned up (daemon=True and join)."""
        self.mock_font.getbbox.return_value = (0, 0, 150, 10)

        scroller = ScrollingText("Long text", self.mock_font, max_width=100,
                                 initial_delay=0.05, update_interval=0.05)
        scroller.start()

        # Thread should be daemon
        self.assertTrue(scroller.scroll_thread.daemon)

        scroller.stop()

        # Thread should be joined and stopped
        self.assertFalse(scroller.scroll_thread.is_alive())

    def test_custom_scroll_parameters(self):
        """Custom scroll_speed, update_interval, wrap_gap should be respected."""
        self.mock_font.getbbox.return_value = (0, 0, 100, 10)

        scroller = ScrollingText("Text", self.mock_font, max_width=80,
                                 scroll_speed=3, update_interval=0.1,
                                 wrap_gap=15, initial_delay=0.05)

        self.assertEqual(scroller.scroll_speed, 3)
        self.assertEqual(scroller.update_interval, 0.1)
        self.assertEqual(scroller.wrap_gap, 15)
        self.assertEqual(scroller.initial_delay, 0.05)

    def test_text_width_calculation_from_bbox(self):
        """Text width should be calculated correctly from font bbox."""
        self.mock_font.getbbox.return_value = (5, 0, 125, 10)  # x0=5, x1=125

        scroller = ScrollingText("Test", self.mock_font, max_width=100)

        # Width = x1 - x0 = 125 - 5 = 120
        self.assertEqual(scroller.text_width, 120)
