import json
import logging
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .types import PresetInfo, PianoteqInfo, ActivationInfo

logger = logging.getLogger(__name__)


class PianoteqJsonRpcError(Exception):
    """Exception raised for JSON-RPC errors"""
    pass


class PianoteqJsonRpc:
    """
    Client for Pianoteq JSON-RPC API.

    Pianoteq must be running with --serve flag to enable the API server
    on localhost:8081.
    """

    def __init__(self, url: str = 'http://localhost:8081/jsonrpc'):
        """
        Initialize JSON-RPC client.

        Args:
            url: JSON-RPC endpoint URL (default: http://localhost:8081/jsonrpc)
        """
        self.url = url
        self._request_id = 0

    def _call(self, method: str, params: Optional[List] = None) -> Dict:
        """
        Make a JSON-RPC call to Pianoteq.

        Args:
            method: JSON-RPC method name
            params: Optional list of parameters

        Returns:
            Result dict from JSON-RPC response

        Raises:
            PianoteqJsonRpcError: If the call fails or Pianoteq is not running
        """
        if params is None:
            params = []

        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._request_id
        }

        try:
            req = Request(
                self.url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urlopen(req, timeout=5) as response:
                response_data = json.loads(response.read().decode('utf-8'))

            if 'error' in response_data:
                error = response_data['error']
                raise PianoteqJsonRpcError(
                    f"JSON-RPC error: {error.get('message', 'Unknown error')}"
                )

            return response_data.get('result')

        except (URLError, HTTPError) as e:
            raise PianoteqJsonRpcError(
                f"Failed to connect to Pianoteq JSON-RPC server at {self.url}. "
                f"Is Pianoteq running with --serve flag? Error: {e}"
            )
        except json.JSONDecodeError as e:
            raise PianoteqJsonRpcError(f"Invalid JSON response from Pianoteq: {e}")

    def get_presets(self) -> List[PresetInfo]:
        """
        Get list of all available presets from Pianoteq.

        Returns:
            List of PresetInfo objects with typed fields for preset metadata.
        """
        logger.debug("Fetching preset list from Pianoteq JSON-RPC API")
        result = self._call('getListOfPresets')
        logger.info(f"Retrieved {len(result)} presets from Pianoteq")
        return [PresetInfo.from_dict(preset) for preset in result]

    def get_info(self) -> PianoteqInfo:
        """
        Get current state information from Pianoteq.

        Returns:
            PianoteqInfo object with typed fields for version, product info,
            current preset, and other state information.

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug("Fetching Pianoteq state info")
        result = self._call('getInfo')
        # getInfo returns a list with one element
        data = result[0] if result else {}
        return PianoteqInfo.from_dict(data)

    def get_activation_info(self) -> ActivationInfo:
        """
        Get activation/license information from Pianoteq.

        Returns:
            ActivationInfo object with typed fields for license status,
            addons, and license holder information (if licensed).

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug("Fetching Pianoteq activation info")
        result = self._call('getActivationInfo')
        # getActivationInfo returns a list with one element
        data = result[0] if result else {}
        return ActivationInfo(**data)

    def is_licensed(self) -> bool:
        """
        Check if Pianoteq is licensed (not demo/trial).

        Returns:
            True if licensed, False if demo/trial

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        activation_info = self.get_activation_info()
        # Demo/trial version has error_msg="Demo", licensed has error_msg=""
        return activation_info.error_msg != 'Demo'

    def load_preset(self, name: str, bank: str = "") -> None:
        """
        Load a preset by name.

        Args:
            name: Preset name
            bank: Bank name (default: empty for factory presets)

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug(f"Loading preset: {name} (bank: {bank or 'factory'})")
        self._call('loadPreset', [name, bank])

    def randomize_parameters(self, amount: float = 1.0) -> None:
        """
        Randomize parameter values.

        Args:
            amount: Randomization amount (0.0-1.0, default 1.0)
                   0.0 = no change, 1.0 = maximum randomization

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug(f"Randomizing parameters with amount={amount}")
        self._call('randomizeParameters', [amount])

    def quit(self) -> None:
        """
        Send quit command to Pianoteq to exit gracefully.

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug("Sending quit command to Pianoteq")
        self._call('quit')
