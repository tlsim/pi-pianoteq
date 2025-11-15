"""Tests for client discovery module"""
import pytest
from pi_pianoteq.client.discovery import (
    discover_builtin_clients,
    discover_builtin_clients_with_errors,
    get_client_info,
    load_client
)
from pi_pianoteq.client.client import Client
from pi_pianoteq.client.cli.cli_client import CliClient
from pi_pianoteq.client.gfxhat.gfxhat_client import GfxhatClient


class TestDiscoverBuiltinClients:
    """Test built-in client discovery"""

    def test_discover_finds_gfxhat_and_cli(self):
        """Test that gfxhat and cli clients are discovered"""
        clients = discover_builtin_clients()
        assert 'gfxhat' in clients
        assert 'cli' in clients

    def test_discovered_clients_are_client_subclasses(self):
        """Test that all discovered clients are Client subclasses"""
        clients = discover_builtin_clients()
        for name, client_class in clients.items():
            assert issubclass(client_class, Client)

    def test_gfxhat_client_class(self):
        """Test that gfxhat client is GfxhatClient"""
        clients = discover_builtin_clients()
        assert clients['gfxhat'] == GfxhatClient

    def test_cli_client_class(self):
        """Test that cli client is CliClient"""
        clients = discover_builtin_clients()
        assert clients['cli'] == CliClient


class TestGetClientInfo:
    """Test client info extraction"""

    def test_get_cli_client_info(self):
        """Test extracting info from CLI client"""
        info = get_client_info(CliClient)
        assert 'name' in info
        assert 'description' in info
        assert info['name'] == 'CliClient'
        assert len(info['description']) > 0

    def test_get_gfxhat_client_info(self):
        """Test extracting info from GFX HAT client"""
        info = get_client_info(GfxhatClient)
        assert 'name' in info
        assert 'description' in info
        assert info['name'] == 'GfxhatClient'
        assert len(info['description']) > 0


class TestLoadClient:
    """Test client loading"""

    def test_load_builtin_cli_client(self):
        """Test loading built-in CLI client by name"""
        client_class = load_client('cli')
        assert client_class == CliClient

    def test_load_builtin_gfxhat_client(self):
        """Test loading built-in GFX HAT client by name"""
        client_class = load_client('gfxhat')
        assert client_class == GfxhatClient

    def test_load_external_client_by_module_spec(self):
        """Test loading external client by module:class spec"""
        # Use CliClient as an example external client
        client_class = load_client('pi_pianoteq.client.cli.cli_client:CliClient')
        assert client_class == CliClient

    def test_load_invalid_client_raises_value_error(self):
        """Test that loading invalid client raises ValueError"""
        with pytest.raises(ValueError):
            load_client('nonexistent')

    def test_load_client_with_invalid_module_raises_import_error(self):
        """Test that loading client with invalid module raises ImportError"""
        with pytest.raises(ImportError):
            load_client('nonexistent.module:NonexistentClient')

    def test_load_client_with_invalid_class_raises_attribute_error(self):
        """Test that loading client with invalid class raises AttributeError"""
        with pytest.raises(AttributeError):
            load_client('pi_pianoteq.client.cli.cli_client:NonexistentClass')

    def test_load_client_with_non_client_class_raises_value_error(self):
        """Test that loading a non-Client class raises ValueError"""
        # Try to load a class that's not a Client subclass
        with pytest.raises(ValueError):
            load_client('pi_pianoteq.client.discovery:get_client_info')

    def test_load_client_with_invalid_spec_format_raises_value_error(self):
        """Test that loading client with invalid spec format raises ValueError"""
        # Missing colon
        with pytest.raises(ValueError):
            load_client('some_invalid_spec_without_colon')


class TestDiscoverBuiltinClientsWithErrors:
    """Test client discovery with error tracking"""

    def test_discovers_both_available_and_unavailable(self):
        """Test that both available and unavailable clients are discovered"""
        available, unavailable = discover_builtin_clients_with_errors()

        # In test environment (with mocked gfxhat), both should be available
        assert 'cli' in available
        assert 'gfxhat' in available

    def test_returns_tuple_of_dicts(self):
        """Test that function returns tuple of two dicts"""
        result = discover_builtin_clients_with_errors()
        assert isinstance(result, tuple)
        assert len(result) == 2
        available, unavailable = result
        assert isinstance(available, dict)
        assert isinstance(unavailable, dict)

    def test_available_clients_are_client_subclasses(self):
        """Test that all available clients are Client subclasses"""
        available, _ = discover_builtin_clients_with_errors()
        for name, client_class in available.items():
            assert issubclass(client_class, Client)

    def test_unavailable_clients_have_error_messages(self):
        """Test that unavailable clients have error message strings"""
        _, unavailable = discover_builtin_clients_with_errors()
        for name, error_msg in unavailable.items():
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0
