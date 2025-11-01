"""Logging configuration for Pi-Pianoteq"""
import logging
import os
import sys


def setup_logging():
    """
    Configure logging for the application.

    Sets up a consistent logging format with timestamps, log levels, and module names.
    Log level can be controlled via PI_PIANOTEQ_LOG_LEVEL environment variable.
    Defaults to INFO level.

    INFO and DEBUG messages are sent to stdout.
    WARNING and ERROR messages are sent to stderr.
    Both streams are captured by systemd/journalctl.
    """
    # Get log level from environment, default to INFO
    log_level = os.environ.get('PI_PIANOTEQ_LOG_LEVEL', 'INFO').upper()

    # Convert string to logging constant
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
