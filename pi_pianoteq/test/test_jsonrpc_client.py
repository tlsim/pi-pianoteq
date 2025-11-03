"""Tests for JSON-RPC client license detection."""

import unittest
from unittest.mock import Mock, patch
from pi_pianoteq.jsonrpc_client import PianoteqJsonRpc


class TestLicenseDetection(unittest.TestCase):
    """Test license detection via getActivationInfo API."""

    def setUp(self):
        """Create a JSON-RPC client instance."""
        self.client = PianoteqJsonRpc()

    @patch.object(PianoteqJsonRpc, '_call')
    def test_is_licensed_with_demo_version(self, mock_call):
        """Test that demo/trial version is correctly detected."""
        # Mock getActivationInfo response for demo version
        mock_call.return_value = [{"addons": [], "error_msg": "Demo"}]

        result = self.client.is_licensed()

        self.assertFalse(result)
        mock_call.assert_called_once_with('getActivationInfo')

    @patch.object(PianoteqJsonRpc, '_call')
    def test_is_licensed_with_licensed_version(self, mock_call):
        """Test that licensed version is correctly detected."""
        # Mock getActivationInfo response for licensed version
        mock_call.return_value = [{
            "addons": ["BechsteinDG", "Electric", "Hohner"],
            "email": "user@example.com",
            "error_msg": "",
            "status": 1
        }]

        result = self.client.is_licensed()

        self.assertTrue(result)
        mock_call.assert_called_once_with('getActivationInfo')

    @patch.object(PianoteqJsonRpc, '_call')
    def test_is_licensed_with_empty_response(self, mock_call):
        """Test handling of empty response (defaults to demo)."""
        # Mock empty response
        mock_call.return_value = []

        result = self.client.is_licensed()

        self.assertFalse(result)

    @patch.object(PianoteqJsonRpc, '_call')
    def test_get_activation_info_returns_dict(self, mock_call):
        """Test that get_activation_info extracts first element from list."""
        # Mock response as list with one element
        mock_call.return_value = [{"error_msg": "Demo", "addons": []}]

        result = self.client.get_activation_info()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["error_msg"], "Demo")

    @patch.object(PianoteqJsonRpc, '_call')
    def test_get_activation_info_with_empty_list(self, mock_call):
        """Test that get_activation_info handles empty list."""
        mock_call.return_value = []

        result = self.client.get_activation_info()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
