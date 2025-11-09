import time


class ButtonSuppression:
    """
    Creates a suppression window after trigger button presses.

    Used to suppress action button presses that occur shortly after trigger
    button presses, preventing accidental adjacent button presses when the user
    brushes the action button while pressing other buttons.
    """

    def __init__(self, threshold_ms=300):
        """
        Initialize suppression window.

        Args:
            threshold_ms: Suppression window duration in milliseconds
        """
        self.threshold_ms = threshold_ms
        self.last_trigger_time = 0

    def record(self):
        """Open a suppression window by recording a trigger button press timestamp."""
        self.last_trigger_time = time.time()

    def allow_action(self):
        """
        Check if the suppression window has closed.

        Returns:
            True if action should be allowed, False if still suppressed
        """
        elapsed_ms = (time.time() - self.last_trigger_time) * 1000
        return elapsed_ms >= self.threshold_ms
