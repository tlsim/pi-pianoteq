import json
import logging
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

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

    def get_presets(self) -> List[Dict]:
        """
        Get list of all available presets from Pianoteq.

        Returns:
            List of preset dictionaries with fields:
            - name: Preset name (str)
            - instr: Instrument name (str) - authoritative grouping
            - class: Instrument class (str) - e.g. "Acoustic Piano", "Electric Piano"
            - license: License name (str)
            - license_status: Status (str) - "demo", "full", "trial", etc.
            - bank: Bank name (str)
            - collection: Collection name (str)
            - author: Author name (str)
            - comment: Description (str)
            - file: File path (str)

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug("Fetching preset list from Pianoteq JSON-RPC API")
        result = self._call('getListOfPresets')
        logger.info(f"Retrieved {len(result)} presets from Pianoteq")
        return result

    def get_info(self) -> Dict:
        """
        Get current state information from Pianoteq.

        Returns:
            Dictionary with Pianoteq state info including:
            - version: Pianoteq version
            - product_name: Product name
            - current_preset: Currently loaded preset info
            - etc.

        Raises:
            PianoteqJsonRpcError: If the call fails
        """
        logger.debug("Fetching Pianoteq state info")
        return self._call('getInfo')

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
