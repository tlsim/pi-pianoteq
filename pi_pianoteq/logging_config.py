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

    Logs are sent to stdout, which systemd captures via journalctl.
    """
    # Get log level from environment, default to INFO
    log_level = os.environ.get('PI_PIANOTEQ_LOG_LEVEL', 'INFO').upper()

    # Convert string to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout,
        force=True  # Override any existing configuration
    )

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
