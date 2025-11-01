"""Tests for buffered logging handler."""

import unittest
import logging
from pi_pianoteq.logging_config import BufferedLoggingHandler


class TestBufferedLoggingHandler(unittest.TestCase):
    """Test BufferedLoggingHandler for CLI log display."""

    def setUp(self):
        """Create a handler instance for each test."""
        self.handler = BufferedLoggingHandler(maxlen=5)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

    def test_buffer_stores_messages(self):
        """Test that messages are stored in the buffer."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        self.handler.emit(record)
        messages = self.handler.get_messages()

        self.assertEqual(len(messages), 1)
        self.assertIn('Test message', messages[0])

    def test_buffer_respects_maxlen(self):
        """Test that buffer only keeps last N messages."""
        # Emit 10 messages to a buffer with maxlen=5
        for i in range(10):
            record = logging.LogRecord(
                name='test',
                level=logging.INFO,
                pathname='',
                lineno=0,
                msg=f'Message {i}',
                args=(),
                exc_info=None
            )
            self.handler.emit(record)

        messages = self.handler.get_messages()

        # Should only have last 5 messages
        self.assertEqual(len(messages), 5)
        self.assertIn('Message 5', messages[0])
        self.assertIn('Message 9', messages[4])

    def test_callback_is_triggered(self):
        """Test that callback is called when message is emitted."""
        callback_called = []

        def callback():
            callback_called.append(True)

        self.handler.set_callback(callback)

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        self.handler.emit(record)

        self.assertEqual(len(callback_called), 1)

    def test_callback_not_triggered_when_none(self):
        """Test that no error occurs when callback is None."""
        # Should not raise exception
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        self.handler.emit(record)
        messages = self.handler.get_messages()

        self.assertEqual(len(messages), 1)

    def test_get_messages_returns_copy(self):
        """Test that get_messages returns a list (not deque)."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        self.handler.emit(record)
        messages = self.handler.get_messages()

        self.assertIsInstance(messages, list)

    def test_formatter_is_applied(self):
        """Test that log formatter is applied to messages."""
        record = logging.LogRecord(
            name='test',
            level=logging.WARNING,
            pathname='',
            lineno=0,
            msg='Warning message',
            args=(),
            exc_info=None
        )

        self.handler.emit(record)
        messages = self.handler.get_messages()

        # Should contain level name from formatter
        self.assertIn('WARNING', messages[0])
        self.assertIn('Warning message', messages[0])


if __name__ == '__main__':
    unittest.main()
