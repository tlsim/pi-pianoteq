import time


class ButtonDebouncer:
    """
    Prevents action button presses shortly after trigger button presses.

    Used to filter out accidental action button presses that occur when the user
    brushes the button while pressing other buttons.
    """

    def __init__(self, threshold_ms=300):
        """
        Initialize debouncer.

        Args:
            threshold_ms: Minimum milliseconds between trigger press and action press
        """
        self.threshold_ms = threshold_ms
        self.last_trigger_time = 0

    def record(self):
        """Record a trigger button press timestamp."""
        self.last_trigger_time = time.time()

    def allow_action(self):
        """
        Check if enough time has elapsed since last trigger press.

        Returns:
            True if action should be allowed, False if it should be debounced
        """
        elapsed_ms = (time.time() - self.last_trigger_time) * 1000
        return elapsed_ms >= self.threshold_ms
