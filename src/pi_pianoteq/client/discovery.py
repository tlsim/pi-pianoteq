"""
Client discovery and loading for Pi-Pianoteq.

This module provides functionality to discover and load client implementations,
both built-in and external.
"""

import pkgutil
import importlib
import inspect
from typing import Dict, Type, Optional
from pi_pianoteq.client.client import Client


def discover_builtin_clients() -> Dict[str, Type[Client]]:
    """
    Scan pi_pianoteq.client.* for Client subclasses.

    Returns:
        Dictionary mapping client names to client classes (e.g., {'gfxhat': GfxhatClient, 'cli': CliClient})
    """
    clients = {}

    # Import the client package to get its path
    import pi_pianoteq.client as client_package

    # Scan all subpackages and modules in pi_pianoteq.client
    for importer, modname, ispkg in pkgutil.iter_modules(client_package.__path__):
        if modname in ['client', 'client_api', 'discovery']:
            # Skip base classes and this module
            continue

        try:
            # Import the module
            full_module_name = f'pi_pianoteq.client.{modname}'
            module = importlib.import_module(full_module_name)

            # Look for subpackages (like cli/ and gfxhat/)
            if ispkg:
                # Try to import a *_client.py module within the subpackage
                try:
                    submodule_name = f'{full_module_name}.{modname}_client'
                    submodule = importlib.import_module(submodule_name)
                    module = submodule
                except ImportError:
                    # If there's no *_client.py, scan all modules in the subpackage
                    pass

            # Find Client subclasses in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, Client) and
                    obj is not Client and
                    obj.__module__.startswith('pi_pianoteq.client')):
                    # Use the module/package name as the client name
                    clients[modname] = obj
                    break  # Only take the first Client subclass from each module

        except ImportError:
            # Skip modules that can't be imported (e.g., missing dependencies)
            continue

    return clients


def get_client_info(client_class: Type[Client]) -> Dict[str, str]:
    """
    Extract metadata from client class.

    Args:
        client_class: The client class to extract info from

    Returns:
        Dictionary with 'name' and 'description' keys
    """
    # Get description from class docstring
    doc = client_class.__doc__ or "No description"

    # Take the first line of the docstring as the description
    description = doc.strip().split('\n')[0].strip()

    return {
        'name': client_class.__name__,
        'description': description
    }


def load_client(client_spec: str) -> Type[Client]:
    """
    Load client from spec string.

    Args:
        client_spec: Client specification:
            - 'gfxhat' or 'cli' -> built-in client
            - 'mypackage.module:ClassName' -> external client

    Returns:
        Client class

    Raises:
        ImportError: If client module cannot be imported
        AttributeError: If client class cannot be found
        ValueError: If client spec is invalid
    """
    # Check if it's a built-in client first
    builtin_clients = discover_builtin_clients()
    if client_spec in builtin_clients:
        return builtin_clients[client_spec]

    # Try to load as external client (format: 'package.module:ClassName')
    if ':' not in client_spec:
        raise ValueError(
            f"Invalid client spec '{client_spec}'. "
            f"Use a built-in client name or 'package.module:ClassName' format."
        )

    module_name, class_name = client_spec.split(':', 1)

    # Import the module
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import module '{module_name}': {e}")

    # Get the class from the module
    try:
        client_class = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f"Module '{module_name}' has no class '{class_name}'")

    # Verify it's a Client subclass
    if not (inspect.isclass(client_class) and issubclass(client_class, Client)):
        raise ValueError(f"{class_name} is not a Client subclass")

    return client_class
