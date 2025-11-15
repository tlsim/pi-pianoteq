"""Logging configuration for Pi-Pianoteq"""
import logging
import os
import sys
from collections import deque
from typing import Optional


class BufferedLoggingHandler(logging.Handler):
    """
    Logging handler that stores messages in a buffer for display in CLI.

    Used to show log messages within the prompt_toolkit UI instead of
    printing directly to console.
    """

    def __init__(self, maxlen=100):
        super().__init__()
        self.buffer = deque(maxlen=maxlen)
        self.on_message_callback = None

    def set_callback(self, callback):
        """Set callback to trigger when new message arrives (e.g., app.invalidate)"""
        self.on_message_callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self.buffer.append(msg)
            # Trigger callback to update UI
            if self.on_message_callback:
                self.on_message_callback()
        except Exception:
            self.handleError(record)

    def get_messages(self):
        """Return all buffered messages as a list"""
        return list(self.buffer)


def setup_logging(handler: Optional[logging.Handler] = None):
    """
    Configure logging for the application.

    Args:
        handler: Optional handler from client, or None for default stdout/stderr

    If handler is provided, uses it for all logging.
    Otherwise uses default stdout (INFO/DEBUG) and stderr (WARNING/ERROR).

    Sets up a consistent logging format with timestamps, log levels, and module names.
    Log level can be controlled via PI_PIANOTEQ_LOG_LEVEL environment variable.
    Defaults to INFO level.
    """
    # Get log level from environment, default to INFO
    log_level = os.environ.get('PI_PIANOTEQ_LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Get the root logger and clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if handler:
        # Use client-provided handler
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        # Handler for INFO and DEBUG -> stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        # Only handle messages below WARNING level
        stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        root_logger.addHandler(stdout_handler)

        # Handler for WARNING and ERROR -> stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(formatter)
        root_logger.addHandler(stderr_handler)

    # Return root logger for convenience
    return logging.getLogger('pi_pianoteq')


def get_logger(name: str):
    """
    Get a logger for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
