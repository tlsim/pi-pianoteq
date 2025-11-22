"""
State monitor for tracking Pianoteq state changes.

Polls Pianoteq's getInfo() API periodically to detect when the preset or
modification state changes outside of the program. Notifies subscribers
via callbacks only when actual changes are detected.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpc, PianoteqJsonRpcError

logger = logging.getLogger(__name__)


@dataclass
class PianoteqState:
    """Current state of Pianoteq."""
    preset_name: str
    modified: bool


class StateMonitor:
    """
    Monitors Pianoteq state and notifies subscribers of changes.

    Runs a background thread that polls getInfo() periodically.
    Only calls callbacks when state actually changes to minimize overhead.
    """

    def __init__(self, jsonrpc: PianoteqJsonRpc, poll_interval: float = 1.0):
        """
        Initialize state monitor.

        Args:
            jsonrpc: Pianoteq JSON-RPC client
            poll_interval: How often to poll for state changes (seconds)
        """
        self.jsonrpc = jsonrpc
        self.poll_interval = poll_interval

        self._callbacks: List[Callable[[PianoteqState], None]] = []
        self._callbacks_lock = threading.Lock()

        self._current_state: Optional[PianoteqState] = None
        self._state_lock = threading.Lock()

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def subscribe(self, callback: Callable[[PianoteqState], None]) -> None:
        """
        Subscribe to state changes.

        The callback will be called only when the state changes (preset name
        or modified flag). It will not be called on every poll, only when
        actual changes are detected.

        Args:
            callback: Function to call when state changes.
                     Receives PianoteqState as argument.
        """
        with self._callbacks_lock:
            self._callbacks.append(callback)
            logger.debug(f"State change callback registered (total: {len(self._callbacks)})")

    def unsubscribe(self, callback: Callable[[PianoteqState], None]) -> None:
        """Unsubscribe from state changes."""
        with self._callbacks_lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
                logger.debug(f"State change callback unregistered (total: {len(self._callbacks)})")

    def get_current_state(self) -> Optional[PianoteqState]:
        """Get the last known state (thread-safe)."""
        with self._state_lock:
            return self._current_state

    def start(self) -> None:
        """Start the state monitoring thread."""
        if self._running:
            logger.warning("StateMonitor already running")
            return

        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="StateMonitor")
        self._thread.start()
        logger.info(f"State monitor started (poll interval: {self.poll_interval}s)")

    def stop(self) -> None:
        """Stop the state monitoring thread."""
        if not self._running:
            return

        logger.info("Stopping state monitor...")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self._running = False
        logger.info("State monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        while not self._stop_event.is_set():
            try:
                self._check_state()
            except Exception as e:
                logger.warning(f"Error checking Pianoteq state: {e}")

            # Sleep in small increments to allow quick shutdown
            for _ in range(int(self.poll_interval * 10)):
                if self._stop_event.is_set():
                    break
                time.sleep(0.1)

    def _check_state(self) -> None:
        """Check current Pianoteq state and notify if changed."""
        try:
            info = self.jsonrpc.get_info()
            new_state = PianoteqState(
                preset_name=info.current_preset.name,
                modified=info.modified
            )

            # Check if state changed
            state_changed = False
            with self._state_lock:
                if self._current_state is None:
                    # First check - initialize state but don't notify
                    self._current_state = new_state
                    logger.debug(f"Initial state: {new_state.preset_name} (modified={new_state.modified})")
                elif (self._current_state.preset_name != new_state.preset_name or
                      self._current_state.modified != new_state.modified):
                    # State changed - update and notify
                    logger.info(f"State change detected: {self._current_state.preset_name} "
                               f"(modified={self._current_state.modified}) -> "
                               f"{new_state.preset_name} (modified={new_state.modified})")
                    self._current_state = new_state
                    state_changed = True

            # Notify subscribers (outside lock to avoid deadlock)
            if state_changed:
                self._notify_subscribers(new_state)

        except PianoteqJsonRpcError as e:
            logger.debug(f"Failed to get Pianoteq state: {e}")

    def _notify_subscribers(self, state: PianoteqState) -> None:
        """Notify all subscribers of state change."""
        with self._callbacks_lock:
            callbacks = self._callbacks.copy()

        for callback in callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
