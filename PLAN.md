# Implementation Plan: Client Discovery & Configuration

## Overview
Replace hardcoded client selection (`--cli` flag) with a flexible, discoverable system that supports:
- Config-based default client selection
- CLI override capability
- Auto-discovery of built-in clients
- Easy integration of external custom clients

## 1. Client Discovery Module

**File:** `src/pi_pianoteq/client/discovery.py`

**Purpose:** Auto-discover available clients and load them dynamically

**Key functions:**
```python
def discover_builtin_clients() -> Dict[str, Type[Client]]:
    """
    Scan pi_pianoteq.client.* for Client subclasses.
    Returns: {'gfxhat': GfxhatClient, 'cli': CliClient}
    """

def get_client_info(client_class: Type[Client]) -> Dict[str, str]:
    """
    Extract metadata from client class (name, description).
    Uses class docstring or __doc__ attribute.
    """

def load_client(client_spec: str) -> Type[Client]:
    """
    Load client from spec string:
    - 'gfxhat' or 'cli' -> built-in client
    - 'mypackage.module:ClassName' -> external client

    Raises: ImportError, AttributeError if client not found
    """
```

**Implementation notes:**
- Use `pkgutil.iter_modules()` to scan `pi_pianoteq.client.*`
- Check if module has a class inheriting from `Client`
- Cache discovered clients to avoid repeated scanning

## 2. Config File Changes

**File:** `src/pi_pianoteq/config/pi_pianoteq.conf`

Add new section:
```ini
[Client]
# Built-in clients: 'gfxhat', 'cli'
# External clients: 'package.module:ClassName'
# Default: gfxhat
CLIENT = gfxhat
```

**File:** `src/pi_pianoteq/config/config.py`

Add:
```python
CLIENT_SECTION = 'Client'

class Config:
    CLIENT = 'gfxhat'  # Default

    # Load from config file in _load_config()
```

## 3. Main Entry Point Refactor

**File:** `src/pi_pianoteq/__main__.py`

**Changes:**

### 3.1 Argument Parser
```python
parser.add_argument(
    '--client',
    type=str,
    help='Specify client to use (e.g., "cli", "gfxhat", or "mypackage:MyClient")'
)

parser.add_argument(
    '--list-clients',
    action='store_true',
    help='List available built-in clients and exit'
)

parser.add_argument(
    '--cli',
    action='store_true',
    help='(DEPRECATED: use --client cli) Use CLI client'
)
```

### 3.2 Client Selection Logic
Replace lines 118-128 with:
```python
# Handle --list-clients
if args.list_clients:
    list_clients()
    return 0

# Determine which client to use
client_spec = None

# Deprecated --cli flag
if args.cli:
    logger.warning(
        "The --cli flag is deprecated and will be removed in a future version. "
        "Use --client cli instead."
    )
    client_spec = 'cli'
# CLI override
elif args.client:
    client_spec = args.client
# Config default
else:
    client_spec = Config.CLIENT

# Load and instantiate client
try:
    from pi_pianoteq.client.discovery import load_client
    ClientClass = load_client(client_spec)
    client = ClientClass(api=None)
except (ImportError, AttributeError) as e:
    logger.error(f"Failed to load client '{client_spec}': {e}")
    print(f"ERROR: Could not load client '{client_spec}'")
    print("Use --list-clients to see available built-in clients")
    return 1
```

### 3.3 List Clients Function
```python
def list_clients():
    """Display available built-in clients"""
    from pi_pianoteq.client.discovery import discover_builtin_clients, get_client_info

    print("Available built-in clients:")
    print()

    clients = discover_builtin_clients()
    for name, client_class in sorted(clients.items()):
        info = get_client_info(client_class)
        print(f"  {name:12} - {info.get('description', 'No description')}")

    print()
    print("Usage:")
    print(f"  pi-pianoteq --client <name>")
    print(f"  pi-pianoteq --client mypackage.module:ClassName")
    print()
    print("To set a default client, edit the config file:")
    print(f"  {USER_CONFIG_PATH}")
```

## 4. CLI Mode Detection

**Challenge:** Lines like `setup_logging(cli_mode=args.cli, ...)` need to detect CLI client

**Solution:** Add method to Client base class:
```python
# In src/pi_pianoteq/client/client.py
class Client(ABC):
    def is_cli_mode(self) -> bool:
        """Override in CLI client to return True for buffered logging"""
        return False

# In src/pi_pianoteq/client/cli/cli_client.py
class CliClient(Client):
    def is_cli_mode(self) -> bool:
        return True
```

Then in `__main__.py`:
```python
log_buffer = client.log_buffer if client.is_cli_mode() else None
setup_logging(cli_mode=client.is_cli_mode(), log_buffer=log_buffer)
```

## 5. Documentation Updates

**File:** `docs/source/guide.rst`

Add section after "Creating Your Client":
```rst
Using Your Custom Client
========================

Once you've created your client, there are several ways to use it:

CLI Override
------------

Run once with your custom client:

.. code-block:: bash

   pi-pianoteq --client mypackage.myclient:MyClient

Set as Default
--------------

Edit your config file to make it the default:

.. code-block:: bash

   pi-pianoteq --init-config  # If you haven't already
   nano ~/.config/pi_pianoteq/pi_pianoteq.conf

Add:

.. code-block:: ini

   [Client]
   CLIENT = mypackage.myclient:MyClient

Now ``pi-pianoteq`` will use your client by default.

Systemd Service
---------------

To use your client in a systemd service, edit the service file:

.. code-block:: ini

   [Service]
   ExecStart=/path/to/venv/bin/pi-pianoteq --client mypackage:MyClient

Discovery
---------

List available built-in clients:

.. code-block:: bash

   pi-pianoteq --list-clients
```

## 6. Testing

**File:** `tests/client/test_discovery.py`

```python
def test_discover_builtin_clients():
    """Test that gfxhat and cli clients are discovered"""
    clients = discover_builtin_clients()
    assert 'gfxhat' in clients
    assert 'cli' in clients

def test_load_builtin_client():
    """Test loading built-in client by name"""
    client_class = load_client('cli')
    assert client_class.__name__ == 'CliClient'

def test_load_external_client():
    """Test loading external client by module:class spec"""
    # Create a mock external client for testing

def test_load_invalid_client():
    """Test that loading invalid client raises appropriate error"""
    with pytest.raises(ImportError):
        load_client('nonexistent')
```

**File:** `tests/config/test_config.py`

Add test for CLIENT config option loading.

## 7. Migration Path

**Backward Compatibility:**
- ✅ `--cli` continues to work (with deprecation warning)
- ✅ Default behavior unchanged (`gfxhat` is still default)
- ✅ Existing deployments work without changes

**Deprecation Timeline:**
- Version X.Y.Z: Add deprecation warning for `--cli`
- Version X.Y+1.Z: Remove `--cli` support (documented in CHANGELOG)

## 8. Benefits Summary

For **End Users:**
- No args needed for default setup
- Easy to try different clients
- Config-based = set once, works automatically

For **Developers:**
- Simple integration: just specify module path
- Discoverable: `--list-clients` shows options
- Documented: clear examples in dev guide

For **Maintainers:**
- No hardcoded client imports
- Easy to add new built-in clients
- Consistent pattern for all client selection

## Implementation Tasks

- [ ] Create client discovery module (src/pi_pianoteq/client/discovery.py)
- [ ] Add CLIENT config option to pi_pianoteq.conf and Config class
- [ ] Update __main__.py to use config-based client selection
- [ ] Add --client CLI argument to override config
- [ ] Add --list-clients CLI argument for discovery
- [ ] Deprecate --cli argument (keep working, show warning)
- [ ] Add is_cli_mode() method to Client base class
- [ ] Update developer documentation with client configuration examples
- [ ] Write tests for client discovery
- [ ] Update CHANGELOG.md
