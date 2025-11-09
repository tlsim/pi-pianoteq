import time


class ButtonDebouncer:
    """
    Prevents action button presses shortly after navigation button presses.

    Used to filter out accidental middle button presses that occur when the user
    brushes the button while navigating with arrow keys.
    """

    def __init__(self, threshold_ms=300):
        """
        Initialize debouncer.

        Args:
            threshold_ms: Minimum milliseconds between navigation press and action press
        """
        self.threshold_ms = threshold_ms
        self.last_nav_time = 0

    def on_navigation(self):
        """Record a navigation button press timestamp."""
        self.last_nav_time = time.time()

    def allow_action(self):
        """
        Check if enough time has elapsed since last navigation press.

        Returns:
            True if action should be allowed, False if it should be debounced
        """
        elapsed_ms = (time.time() - self.last_nav_time) * 1000
        return elapsed_ms >= self.threshold_ms
