import logging
import subprocess
import time
from os.path import expanduser
from typing import List, Optional

from pi_pianoteq.config.config import Config

logger = logging.getLogger(__name__)


class Pianoteq:
    def __init__(self, jsonrpc_client=None):
        self.headless = Config.PIANOTEQ_HEADLESS
        self.mapping_name = Config.MIDI_MAPPING_NAME
        self.executable = expanduser(Config.PIANOTEQ_DIR) + Config.PIANOTEQ_BIN
        self.process = None
        self.jsonrpc_client = jsonrpc_client

    def get_presets(self) -> List[str]:
        pianoteq_proc = subprocess.run([self.executable, '--list-presets'],
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return output.splitlines()

    def get_version(self) -> str:
        pianoteq_proc = subprocess.run([self.executable, '--version'],
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return ' '.join(output.splitlines())

    def start(self):
        args = [self.executable, '--midimapping', self.mapping_name, '--serve', '']
        if self.headless:
            args.append('--headless')
        self.process = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def quit(self, timeout: float = 5.0):
        """
        Gracefully quit Pianoteq using JSON-RPC API, then terminate process if needed.

        Args:
            timeout: Maximum time to wait for graceful exit (seconds)
        """
        if self.process is None:
            logger.debug("No Pianoteq process to quit")
            return

        if self.process.returncode is not None:
            logger.debug("Pianoteq process already exited")
            return

        # Try graceful quit via JSON-RPC API
        if self.jsonrpc_client is not None:
            try:
                logger.info("Sending quit command to Pianoteq via JSON-RPC")
                from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpcError
                try:
                    self.jsonrpc_client.quit()
                except PianoteqJsonRpcError:
                    # Pianoteq may close the connection immediately, causing an error
                    pass

                # Wait for process to exit gracefully
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self.process.poll() is not None:
                        logger.info("Pianoteq exited gracefully")
                        return
                    time.sleep(0.1)

                logger.warning(f"Pianoteq did not exit within {timeout}s after quit command")
            except Exception as e:
                logger.warning(f"Failed to send quit command to Pianoteq: {e}")

        # Fallback to SIGTERM
        self.terminate()

    def terminate(self, timeout: float = 3.0):
        """
        Terminate the Pianoteq process using SIGTERM, then SIGKILL if needed.

        Args:
            timeout: Maximum time to wait for process to exit (seconds)
        """
        if self.process is None:
            return

        if self.process.returncode is not None:
            return

        logger.info("Terminating Pianoteq process with SIGTERM")
        self.process.terminate()

        # Wait for process to exit
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                logger.info("Pianoteq process terminated")
                return
            time.sleep(0.1)

        # Force kill if still running
        logger.warning(f"Pianoteq did not terminate within {timeout}s, sending SIGKILL")
        self.process.kill()
        self.process.wait()
        logger.info("Pianoteq process killed")
