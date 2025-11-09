import unittest
import time

from pi_pianoteq.util.button_suppression import ButtonSuppression


class ButtonSuppressionTestCase(unittest.TestCase):
    def test_initial_state_allows_action(self):
        """Without any record() call, allow_action should return True"""
        suppression = ButtonSuppression(300)
        self.assertTrue(suppression.allow_action())

    def test_immediate_action_after_record_is_blocked(self):
        """Immediately after record(), allow_action should return False"""
        suppression = ButtonSuppression(300)
        suppression.record()
        self.assertFalse(suppression.allow_action())

    def test_action_allowed_after_threshold(self):
        """After threshold time has elapsed, allow_action should return True"""
        suppression = ButtonSuppression(100)  # 100ms threshold for faster test
        suppression.record()
        time.sleep(0.12)  # 120ms > 100ms threshold
        self.assertTrue(suppression.allow_action())

    def test_action_blocked_before_threshold(self):
        """Before threshold time elapses, allow_action should return False"""
        suppression = ButtonSuppression(200)
        suppression.record()
        time.sleep(0.05)  # 50ms < 200ms threshold
        self.assertFalse(suppression.allow_action())

    def test_custom_threshold(self):
        """Suppression should respect custom threshold values"""
        suppression = ButtonSuppression(50)
        suppression.record()
        time.sleep(0.06)  # 60ms > 50ms threshold
        self.assertTrue(suppression.allow_action())

    def test_multiple_records_reset_timer(self):
        """Multiple record() calls should reset the timer"""
        suppression = ButtonSuppression(100)
        suppression.record()
        time.sleep(0.06)  # 60ms elapsed
        suppression.record()  # Reset timer
        # Now only ~0ms has elapsed since last record()
        self.assertFalse(suppression.allow_action())

    def test_default_threshold_value(self):
        """Default threshold should be 300ms"""
        suppression = ButtonSuppression()
        self.assertEqual(300, suppression.threshold_ms)


if __name__ == '__main__':
    unittest.main()
