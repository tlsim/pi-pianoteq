"""Tests for StateMonitor class."""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
from pi_pianoteq.state.state_monitor import StateMonitor, PianoteqState
from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpcError
from pi_pianoteq.rpc.types import PianoteqInfo, CurrentPreset


class TestStateMonitor(unittest.TestCase):
    """Test StateMonitor polling and callback functionality."""

    def setUp(self):
        """Create mock JSON-RPC client."""
        self.mock_jsonrpc = Mock()
        self.monitor = StateMonitor(self.mock_jsonrpc, poll_interval=0.1)

    def tearDown(self):
        """Ensure monitor is stopped."""
        if self.monitor._running:
            self.monitor.stop()

    def test_initial_state_is_none(self):
        """Test that initial state is None before first poll."""
        self.assertIsNone(self.monitor.get_current_state())

    def test_subscribe_adds_callback(self):
        """Test that subscribe adds callback to list."""
        callback = Mock()
        self.monitor.subscribe(callback)

        self.assertIn(callback, self.monitor._callbacks)

    def test_unsubscribe_removes_callback(self):
        """Test that unsubscribe removes callback from list."""
        callback = Mock()
        self.monitor.subscribe(callback)
        self.monitor.unsubscribe(callback)

        self.assertNotIn(callback, self.monitor._callbacks)

    def test_first_check_initializes_state_without_callback(self):
        """Test that first state check sets state but doesn't call callbacks."""
        callback = Mock()
        self.monitor.subscribe(callback)

        # Mock getInfo response
        mock_info = PianoteqInfo(
            current_preset=CurrentPreset(name="Test Preset"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info

        # Check state
        self.monitor._check_state()

        # State should be set
        state = self.monitor.get_current_state()
        self.assertIsNotNone(state)
        self.assertEqual(state.preset_name, "Test Preset")
        self.assertFalse(state.modified)

        # Callback should not be called on first check
        callback.assert_not_called()

    def test_state_change_triggers_callback(self):
        """Test that state change calls subscribed callbacks."""
        callback = Mock()
        self.monitor.subscribe(callback)

        # Initial state
        mock_info1 = PianoteqInfo(
            current_preset=CurrentPreset(name="Preset 1"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info1
        self.monitor._check_state()

        # Change state
        mock_info2 = PianoteqInfo(
            current_preset=CurrentPreset(name="Preset 2"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info2
        self.monitor._check_state()

        # Callback should be called once with new state
        callback.assert_called_once()
        called_state = callback.call_args[0][0]
        self.assertEqual(called_state.preset_name, "Preset 2")

    def test_modified_flag_change_triggers_callback(self):
        """Test that modified flag change alone triggers callback."""
        callback = Mock()
        self.monitor.subscribe(callback)

        # Initial state
        mock_info1 = PianoteqInfo(
            current_preset=CurrentPreset(name="Test Preset"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info1
        self.monitor._check_state()

        # Change only modified flag
        mock_info2 = PianoteqInfo(
            current_preset=CurrentPreset(name="Test Preset"),
            modified=True
        )
        self.mock_jsonrpc.get_info.return_value = mock_info2
        self.monitor._check_state()

        # Callback should be called with modified=True
        callback.assert_called_once()
        called_state = callback.call_args[0][0]
        self.assertTrue(called_state.modified)

    def test_no_change_does_not_trigger_callback(self):
        """Test that unchanged state doesn't trigger callbacks."""
        callback = Mock()
        self.monitor.subscribe(callback)

        # Initial state
        mock_info = PianoteqInfo(
            current_preset=CurrentPreset(name="Test Preset"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info

        # Check twice with same state
        self.monitor._check_state()
        callback.reset_mock()
        self.monitor._check_state()

        # Callback should not be called second time
        callback.assert_not_called()

    def test_api_error_is_logged_not_raised(self):
        """Test that API errors are logged but don't crash monitor."""
        self.mock_jsonrpc.get_info.side_effect = PianoteqJsonRpcError("Connection failed")

        # Should not raise exception
        self.monitor._check_state()

        # State should remain None
        self.assertIsNone(self.monitor.get_current_state())

    def test_callback_exception_is_logged(self):
        """Test that callback exceptions are logged but don't stop other callbacks."""
        callback1 = Mock(side_effect=Exception("Callback error"))
        callback2 = Mock()

        self.monitor.subscribe(callback1)
        self.monitor.subscribe(callback2)

        # Setup state change
        mock_info1 = PianoteqInfo(
            current_preset=CurrentPreset(name="Preset 1"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info1
        self.monitor._check_state()

        mock_info2 = PianoteqInfo(
            current_preset=CurrentPreset(name="Preset 2"),
            modified=False
        )
        self.mock_jsonrpc.get_info.return_value = mock_info2

        # Should not raise exception, both callbacks called
        self.monitor._check_state()

        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_start_creates_thread(self):
        """Test that start() creates and starts background thread."""
        self.monitor.start()

        self.assertTrue(self.monitor._running)
        self.assertIsNotNone(self.monitor._thread)
        self.assertTrue(self.monitor._thread.is_alive())

        self.monitor.stop()

    def test_stop_terminates_thread(self):
        """Test that stop() terminates background thread."""
        # Mock getInfo to prevent errors
        self.mock_jsonrpc.get_info.return_value = PianoteqInfo(
            current_preset=CurrentPreset(name="Test"),
            modified=False
        )

        self.monitor.start()
        self.assertTrue(self.monitor._running)

        self.monitor.stop()
        self.assertFalse(self.monitor._running)

    def test_multiple_start_calls_ignored(self):
        """Test that multiple start() calls don't create multiple threads."""
        self.monitor.start()
        thread1 = self.monitor._thread

        self.monitor.start()
        thread2 = self.monitor._thread

        # Should be same thread
        self.assertIs(thread1, thread2)

        self.monitor.stop()

    def test_stop_on_non_running_monitor(self):
        """Test that stop() on non-running monitor is safe."""
        # Should not raise exception
        self.monitor.stop()
        self.assertFalse(self.monitor._running)


class TestPianoteqState(unittest.TestCase):
    """Test PianoteqState dataclass."""

    def test_state_creation(self):
        """Test creating PianoteqState."""
        state = PianoteqState(preset_name="Test Preset", modified=True)

        self.assertEqual(state.preset_name, "Test Preset")
        self.assertTrue(state.modified)

    def test_state_equality(self):
        """Test PianoteqState equality comparison."""
        state1 = PianoteqState(preset_name="Test", modified=False)
        state2 = PianoteqState(preset_name="Test", modified=False)
        state3 = PianoteqState(preset_name="Test", modified=True)

        self.assertEqual(state1, state2)
        self.assertNotEqual(state1, state3)


if __name__ == '__main__':
    unittest.main()
