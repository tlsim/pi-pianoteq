import unittest
import time

from pi_pianoteq.util.button_debouncer import ButtonDebouncer


class ButtonDebouncerTestCase(unittest.TestCase):
    def test_initial_state_allows_action(self):
        """Without any record() call, allow_action should return True"""
        debouncer = ButtonDebouncer(300)
        self.assertTrue(debouncer.allow_action())

    def test_immediate_action_after_record_is_blocked(self):
        """Immediately after record(), allow_action should return False"""
        debouncer = ButtonDebouncer(300)
        debouncer.record()
        self.assertFalse(debouncer.allow_action())

    def test_action_allowed_after_threshold(self):
        """After threshold time has elapsed, allow_action should return True"""
        debouncer = ButtonDebouncer(100)  # 100ms threshold for faster test
        debouncer.record()
        time.sleep(0.12)  # 120ms > 100ms threshold
        self.assertTrue(debouncer.allow_action())

    def test_action_blocked_before_threshold(self):
        """Before threshold time elapses, allow_action should return False"""
        debouncer = ButtonDebouncer(200)
        debouncer.record()
        time.sleep(0.05)  # 50ms < 200ms threshold
        self.assertFalse(debouncer.allow_action())

    def test_custom_threshold(self):
        """Debouncer should respect custom threshold values"""
        debouncer = ButtonDebouncer(50)
        debouncer.record()
        time.sleep(0.06)  # 60ms > 50ms threshold
        self.assertTrue(debouncer.allow_action())

    def test_multiple_records_reset_timer(self):
        """Multiple record() calls should reset the timer"""
        debouncer = ButtonDebouncer(100)
        debouncer.record()
        time.sleep(0.06)  # 60ms elapsed
        debouncer.record()  # Reset timer
        # Now only ~0ms has elapsed since last record()
        self.assertFalse(debouncer.allow_action())

    def test_default_threshold_value(self):
        """Default threshold should be 300ms"""
        debouncer = ButtonDebouncer()
        self.assertEqual(300, debouncer.threshold_ms)


if __name__ == '__main__':
    unittest.main()
