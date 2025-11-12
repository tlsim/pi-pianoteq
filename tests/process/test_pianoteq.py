"""Tests for Pianoteq process management."""

import time
import unittest
from unittest.mock import Mock, MagicMock, patch, call

from pi_pianoteq.process.pianoteq import Pianoteq
from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpcError


class TestPianoteqQuit(unittest.TestCase):
    """Test Pianoteq quit() method for graceful shutdown."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_jsonrpc = Mock()
        with patch('pi_pianoteq.process.pianoteq.Config'):
            self.pianoteq = Pianoteq(jsonrpc_client=self.mock_jsonrpc)

    def test_quit_with_no_process(self):
        """Test quit() handles case when process is None."""
        self.pianoteq.process = None

        # Should return without error
        self.pianoteq.quit()

        # Should not attempt to call JSON-RPC
        self.mock_jsonrpc._call.assert_not_called()

    def test_quit_with_already_exited_process(self):
        """Test quit() handles case when process already exited."""
        mock_process = Mock()
        mock_process.returncode = 0  # Process already exited
        self.pianoteq.process = mock_process

        self.pianoteq.quit()

        # Should not attempt to quit or terminate
        self.mock_jsonrpc._call.assert_not_called()
        mock_process.terminate.assert_not_called()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_quit_graceful_success(self, mock_sleep):
        """Test quit() successfully quits via JSON-RPC."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.side_effect = [None, None, 0]  # Exits on third poll
        self.pianoteq.process = mock_process

        self.pianoteq.quit(timeout=5.0)

        # Should send quit command
        self.mock_jsonrpc._call.assert_called_once_with('quit')
        # Should poll process
        self.assertEqual(mock_process.poll.call_count, 3)
        # Should not terminate since graceful quit succeeded
        mock_process.terminate.assert_not_called()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    @patch('pi_pianoteq.process.pianoteq.time.time')
    def test_quit_graceful_timeout_fallback_to_terminate(self, mock_time, mock_sleep):
        """Test quit() falls back to terminate() if graceful quit times out."""
        # Mock time to simulate timeout
        # Need enough values for quit() loop + terminate() loop
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.side_effect = [None, None, None, None, None, None, 0]  # Exits on terminate
        self.pianoteq.process = mock_process

        self.pianoteq.quit(timeout=5.0)

        # Should send quit command
        self.mock_jsonrpc._call.assert_called_once_with('quit')
        # Should fall back to terminate
        mock_process.terminate.assert_called_once()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_quit_jsonrpc_error_with_delayed_exit(self, mock_sleep):
        """Test quit() handles JSON-RPC error and waits for process to exit."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.side_effect = [None, None, 0]  # Process exits after a few polls
        self.pianoteq.process = mock_process

        # Simulate JSON-RPC error (expected when Pianoteq closes connection)
        self.mock_jsonrpc._call.side_effect = PianoteqJsonRpcError("Connection closed")

        self.pianoteq.quit(timeout=5.0)

        # Should attempt quit command
        self.mock_jsonrpc._call.assert_called_once_with('quit')
        # Should poll process and see it exited, no need to terminate
        self.assertEqual(mock_process.poll.call_count, 3)
        mock_process.terminate.assert_not_called()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_quit_jsonrpc_connection_closes_immediately(self, mock_sleep):
        """Test quit() handles Pianoteq closing connection immediately."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.return_value = 0  # Process exits immediately
        self.pianoteq.process = mock_process

        # Simulate connection close (expected behavior)
        self.mock_jsonrpc._call.side_effect = PianoteqJsonRpcError("Connection refused")

        self.pianoteq.quit(timeout=5.0)

        # Should attempt quit command (even if it errors)
        self.mock_jsonrpc._call.assert_called_once_with('quit')
        # Process exits immediately, so should not need terminate
        mock_process.poll.assert_called_once()
        mock_process.terminate.assert_not_called()

    def test_quit_without_jsonrpc_client(self):
        """Test quit() falls back to terminate() when no JSON-RPC client."""
        with patch('pi_pianoteq.process.pianoteq.Config'):
            pianoteq = Pianoteq(jsonrpc_client=None)

        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.return_value = 0
        pianoteq.process = mock_process

        pianoteq.quit()

        # Should fall back to terminate immediately
        mock_process.terminate.assert_called_once()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_quit_exception_during_jsonrpc_fallback_to_terminate(self, mock_sleep):
        """Test quit() handles unexpected exceptions during JSON-RPC call."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.return_value = 0
        self.pianoteq.process = mock_process

        # Simulate unexpected error
        self.mock_jsonrpc._call.side_effect = Exception("Unexpected error")

        self.pianoteq.quit(timeout=5.0)

        # Should fall back to terminate
        mock_process.terminate.assert_called_once()


class TestPianoteqTerminate(unittest.TestCase):
    """Test Pianoteq terminate() method."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('pi_pianoteq.process.pianoteq.Config'):
            self.pianoteq = Pianoteq()

    def test_terminate_with_no_process(self):
        """Test terminate() handles case when process is None."""
        self.pianoteq.process = None

        # Should return without error
        self.pianoteq.terminate()

    def test_terminate_with_already_exited_process(self):
        """Test terminate() handles case when process already exited."""
        mock_process = Mock()
        mock_process.returncode = 0  # Process already exited
        self.pianoteq.process = mock_process

        self.pianoteq.terminate()

        # Should not attempt to terminate
        mock_process.terminate.assert_not_called()
        mock_process.kill.assert_not_called()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_terminate_success_with_sigterm(self, mock_sleep):
        """Test terminate() successfully terminates with SIGTERM."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.side_effect = [None, None, 0]  # Exits on third poll
        self.pianoteq.process = mock_process

        self.pianoteq.terminate(timeout=3.0)

        # Should call terminate (SIGTERM)
        mock_process.terminate.assert_called_once()
        # Should poll process
        self.assertEqual(mock_process.poll.call_count, 3)
        # Should not need kill (SIGKILL)
        mock_process.kill.assert_not_called()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    @patch('pi_pianoteq.process.pianoteq.time.time')
    def test_terminate_timeout_fallback_to_sigkill(self, mock_time, mock_sleep):
        """Test terminate() falls back to SIGKILL if SIGTERM times out."""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 1, 2, 3, 4]  # Exceeds 3 second timeout

        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.return_value = None  # Never exits on poll
        self.pianoteq.process = mock_process

        self.pianoteq.terminate(timeout=3.0)

        # Should call terminate (SIGTERM)
        mock_process.terminate.assert_called_once()
        # Should fall back to kill (SIGKILL)
        mock_process.kill.assert_called_once()
        # Should wait for process to die
        mock_process.wait.assert_called_once()

    @patch('pi_pianoteq.process.pianoteq.time.sleep')
    def test_terminate_immediate_exit(self, mock_sleep):
        """Test terminate() handles immediate process exit."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.poll.return_value = 0  # Exits immediately
        self.pianoteq.process = mock_process

        self.pianoteq.terminate(timeout=3.0)

        # Should call terminate
        mock_process.terminate.assert_called_once()
        # Should not need kill
        mock_process.kill.assert_not_called()
        mock_process.wait.assert_not_called()


class TestPianoteqInvertedLogicFix(unittest.TestCase):
    """Test that the inverted logic bug in terminate() is fixed."""

    def test_terminate_correctly_checks_returncode_is_none(self):
        """Verify terminate() checks if process is still running (returncode is None)."""
        with patch('pi_pianoteq.process.pianoteq.Config'):
            pianoteq = Pianoteq()

        # Test 1: Process still running (returncode is None)
        mock_process = Mock()
        mock_process.returncode = None  # Process is still running
        mock_process.poll.return_value = 0  # Will exit immediately
        pianoteq.process = mock_process

        pianoteq.terminate()

        # Should attempt to terminate because returncode is None
        mock_process.terminate.assert_called_once()

    def test_terminate_skips_already_exited_process(self):
        """Verify terminate() skips process when already exited (returncode is not None)."""
        with patch('pi_pianoteq.process.pianoteq.Config'):
            pianoteq = Pianoteq()

        # Test 2: Process already exited (returncode is not None)
        mock_process = Mock()
        mock_process.returncode = 0  # Process already exited
        pianoteq.process = mock_process

        pianoteq.terminate()

        # Should NOT attempt to terminate because returncode is not None
        mock_process.terminate.assert_not_called()
        mock_process.kill.assert_not_called()


if __name__ == '__main__':
    unittest.main()
