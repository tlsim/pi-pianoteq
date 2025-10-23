import threading
import time


class ScrollingText:
    """
    Helper class for smooth marquee-style scrolling text on small displays.

    Automatically scrolls text that exceeds max_width in a continuous loop.
    Threading-based for smooth animation.
    """

    def __init__(self, text, font, max_width, scroll_speed=5, update_interval=0.1, initial_delay=1.0):
        """
        Initialize scrolling text.

        Args:
            text: The text to display
            font: PIL font object for measuring text
            max_width: Maximum width in pixels before scrolling
            scroll_speed: Pixels to scroll per update (default: 5)
            update_interval: Seconds between updates (default: 0.1)
            initial_delay: Seconds to wait before starting scroll (default: 1.0)
        """
        self.text = text
        self.font = font
        self.max_width = max_width
        self.scroll_speed = scroll_speed
        self.update_interval = update_interval
        self.initial_delay = initial_delay

        # Calculate text width
        bbox = self.font.getbbox(self.text)
        self.text_width = bbox[2] - bbox[0]

        # Scrolling state
        self.scroll_offset = 0
        self.needs_scrolling = self.text_width > self.max_width

        # Threading
        self.scroll_thread = None
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()

    def start(self):
        """Start the scrolling animation if text is too long."""
        if not self.needs_scrolling:
            return

        if self.scroll_thread and self.scroll_thread.is_alive():
            return  # Already running

        self.stop_flag.clear()
        self.scroll_thread = threading.Thread(target=self._scroll_worker, daemon=True)
        self.scroll_thread.start()

    def stop(self):
        """Stop the scrolling animation and reset offset."""
        if self.scroll_thread and self.scroll_thread.is_alive():
            self.stop_flag.set()
            self.scroll_thread.join(timeout=0.5)

        with self.lock:
            self.scroll_offset = 0

    def _scroll_worker(self):
        """Background thread worker for scrolling animation."""
        # Initial delay before starting scroll
        if not self.stop_flag.wait(self.initial_delay):
            while not self.stop_flag.is_set():
                with self.lock:
                    self.scroll_offset += self.scroll_speed

                    # Continuous loop: wrap when we've scrolled past the end
                    # Add some padding (20px) before wrapping for visual separation
                    if self.scroll_offset >= self.text_width + 20:
                        self.scroll_offset = 0

                time.sleep(self.update_interval)

    def get_offset(self):
        """Get current scroll offset (thread-safe)."""
        with self.lock:
            return self.scroll_offset

    def update_text(self, new_text):
        """
        Update the text and recalculate if scrolling is needed.
        Restarts scrolling if currently running.
        """
        was_running = self.scroll_thread and self.scroll_thread.is_alive()

        if was_running:
            self.stop()

        self.text = new_text
        bbox = self.font.getbbox(self.text)
        self.text_width = bbox[2] - bbox[0]
        self.needs_scrolling = self.text_width > self.max_width
        self.scroll_offset = 0

        if was_running:
            self.start()
