"""Tests for JSON-RPC client license detection."""

import unittest
from unittest.mock import Mock, patch
from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpc
from pi_pianoteq.rpc.types import ActivationInfo


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
    def test_get_activation_info_returns_typed_object(self, mock_call):
        """Test that get_activation_info extracts first element from list and returns ActivationInfo."""
        # Mock response as list with one element
        mock_call.return_value = [{"error_msg": "Demo", "addons": []}]

        result = self.client.get_activation_info()

        self.assertIsInstance(result, ActivationInfo)
        self.assertEqual(result.error_msg, "Demo")
        self.assertEqual(result.addons, [])

    @patch.object(PianoteqJsonRpc, '_call')
    def test_get_activation_info_with_empty_list(self, mock_call):
        """Test that get_activation_info handles empty list."""
        mock_call.return_value = []

        result = self.client.get_activation_info()

        self.assertIsInstance(result, ActivationInfo)
        self.assertEqual(result.error_msg, "Demo")  # Default value
        self.assertEqual(result.addons, [])


class TestRandomization(unittest.TestCase):
    """Test randomization API methods."""

    def setUp(self):
        """Create a JSON-RPC client instance."""
        self.client = PianoteqJsonRpc()

    @patch.object(PianoteqJsonRpc, '_call')
    def test_randomize_parameters_with_default_amount(self, mock_call):
        """Test randomize_parameters with default amount (1.0)."""
        mock_call.return_value = None

        self.client.randomize_parameters()

        mock_call.assert_called_once_with('randomizeParameters', [1.0])

    @patch.object(PianoteqJsonRpc, '_call')
    def test_randomize_parameters_with_custom_amount(self, mock_call):
        """Test randomize_parameters with custom amount."""
        mock_call.return_value = None

        self.client.randomize_parameters(0.5)

        mock_call.assert_called_once_with('randomizeParameters', [0.5])

    @patch.object(PianoteqJsonRpc, '_call')
    def test_randomize_parameters_with_zero_amount(self, mock_call):
        """Test randomize_parameters with zero amount (no change)."""
        mock_call.return_value = None

        self.client.randomize_parameters(0.0)

        mock_call.assert_called_once_with('randomizeParameters', [0.0])


if __name__ == '__main__':
    unittest.main()
