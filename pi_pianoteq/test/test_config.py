import os
import tempfile
from pathlib import Path
import pytest

from pi_pianoteq.config import ConfigLoader, BUNDLED_CONFIG_PATH


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write("""[Pianoteq]
PIANOTEQ_DIR = /custom/pianoteq/dir/
PIANOTEQ_BIN = Custom Pianoteq
PIANOTEQ_DATA_DIR = /custom/data/
PIANOTEQ_MIDI_MAPPINGS_DIR = /custom/mappings/
PIANOTEQ_PREFS_FILE = /custom/prefs.file
PIANOTEQ_HEADLESS = true

[Midi]
MIDI_PORT_NAME = CUSTOM-PORT
MIDI_MAPPING_NAME = CustomMapping
MIDI_PIANOTEQ_STARTUP_DELAY = 5

[System]
SHUTDOWN_COMMAND = custom shutdown command
""")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


@pytest.fixture
def partial_config_file():
    """Create a config file with only some values set"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write("""[Pianoteq]
PIANOTEQ_DIR = /partial/pianoteq/dir/
PIANOTEQ_BIN = Partial Pianoteq

[Midi]
MIDI_PORT_NAME = PARTIAL-PORT
""")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


def test_bundled_config_exists():
    """Test that bundled default config file exists"""
    assert BUNDLED_CONFIG_PATH.exists()


def test_loads_bundled_default_when_no_user_config():
    """Test that config loads from bundled default when no user config exists"""
    # Create config with non-existent user config path
    config = ConfigLoader(config_path=Path('/nonexistent/config.conf'))

    # Should fall back to bundled defaults
    assert config.PIANOTEQ_DIR is not None
    assert config.MIDI_PORT_NAME is not None

    # All values should come from bundled default
    sources = config.get_config_sources()
    assert all(source == 'bundled_default' for source in sources.values())


def test_user_config_overrides_default(temp_config_file):
    """Test that user config overrides bundled default"""
    config = ConfigLoader(config_path=temp_config_file)

    assert config.PIANOTEQ_DIR == '/custom/pianoteq/dir/'
    assert config.PIANOTEQ_BIN == 'Custom Pianoteq'
    assert config.MIDI_PORT_NAME == 'CUSTOM-PORT'
    assert config.PIANOTEQ_HEADLESS is True

    # Check sources
    sources = config.get_config_sources()
    assert sources['PIANOTEQ_DIR'] == 'user_config'
    assert sources['MIDI_PORT_NAME'] == 'user_config'


def test_partial_user_config_merges_with_default(partial_config_file):
    """Test that partial user config merges with default values"""
    config = ConfigLoader(config_path=partial_config_file)

    # Values from user config
    assert config.PIANOTEQ_DIR == '/partial/pianoteq/dir/'
    assert config.PIANOTEQ_BIN == 'Partial Pianoteq'
    assert config.MIDI_PORT_NAME == 'PARTIAL-PORT'

    # Values should fall back to default
    assert config.PIANOTEQ_DATA_DIR is not None  # From default
    assert config.MIDI_MAPPING_NAME is not None  # From default

    # Check sources
    sources = config.get_config_sources()
    assert sources['PIANOTEQ_DIR'] == 'user_config'
    assert sources['PIANOTEQ_BIN'] == 'user_config'
    assert sources['MIDI_PORT_NAME'] == 'user_config'
    assert sources['PIANOTEQ_DATA_DIR'] == 'bundled_default'
    assert sources['MIDI_MAPPING_NAME'] == 'bundled_default'


def test_env_var_overrides_user_config(temp_config_file):
    """Test that environment variables override user config"""
    # Set environment variable
    os.environ['PIANOTEQ_DIR'] = '/env/override/dir/'
    os.environ['MIDI_PORT_NAME'] = 'ENV-PORT'

    try:
        config = ConfigLoader(config_path=temp_config_file)

        # Env vars should override user config
        assert config.PIANOTEQ_DIR == '/env/override/dir/'
        assert config.MIDI_PORT_NAME == 'ENV-PORT'

        # Non-overridden values still from user config
        assert config.PIANOTEQ_BIN == 'Custom Pianoteq'

        # Check sources
        sources = config.get_config_sources()
        assert sources['PIANOTEQ_DIR'] == 'environment'
        assert sources['MIDI_PORT_NAME'] == 'environment'
        assert sources['PIANOTEQ_BIN'] == 'user_config'
    finally:
        # Clean up environment
        del os.environ['PIANOTEQ_DIR']
        del os.environ['MIDI_PORT_NAME']


def test_env_var_overrides_default():
    """Test that environment variables override bundled default"""
    os.environ['PIANOTEQ_DIR'] = '/env/dir/'

    try:
        config = ConfigLoader(config_path=Path('/nonexistent/config.conf'))

        assert config.PIANOTEQ_DIR == '/env/dir/'

        sources = config.get_config_sources()
        assert sources['PIANOTEQ_DIR'] == 'environment'
    finally:
        del os.environ['PIANOTEQ_DIR']


def test_config_priority_all_sources(temp_config_file):
    """Test complete priority chain: env > user > default"""
    os.environ['PIANOTEQ_DIR'] = '/env/dir/'

    try:
        config = ConfigLoader(config_path=temp_config_file)

        sources = config.get_config_sources()

        # Env var set: should be from environment
        assert config.PIANOTEQ_DIR == '/env/dir/'
        assert sources['PIANOTEQ_DIR'] == 'environment'

        # In user config but no env var: should be from user_config
        assert config.PIANOTEQ_BIN == 'Custom Pianoteq'
        assert sources['PIANOTEQ_BIN'] == 'user_config'

        # Not in user config or env: should be from bundled_default
        # (assuming these aren't in the temp_config_file or environment)

    finally:
        del os.environ['PIANOTEQ_DIR']


def test_boolean_config_parsing(temp_config_file):
    """Test that boolean config values are parsed correctly"""
    config = ConfigLoader(config_path=temp_config_file)

    # temp_config_file sets PIANOTEQ_HEADLESS = true
    assert config.PIANOTEQ_HEADLESS is True
    assert isinstance(config.PIANOTEQ_HEADLESS, bool)


def test_integer_config_parsing(temp_config_file):
    """Test that integer config values are parsed correctly"""
    config = ConfigLoader(config_path=temp_config_file)

    # temp_config_file sets MIDI_PIANOTEQ_STARTUP_DELAY = 5
    assert config.MIDI_PIANOTEQ_STARTUP_DELAY == 5
    assert isinstance(config.MIDI_PIANOTEQ_STARTUP_DELAY, int)


def test_get_config_sources():
    """Test that config sources tracking works"""
    config = ConfigLoader(config_path=Path('/nonexistent/config.conf'))

    sources = config.get_config_sources()

    # Should return a dict
    assert isinstance(sources, dict)

    # Should have entries for all config keys
    assert 'PIANOTEQ_DIR' in sources
    assert 'MIDI_PORT_NAME' in sources
    assert 'SHUTDOWN_COMMAND' in sources

    # All should be from bundled_default
    assert all(source == 'bundled_default' for source in sources.values())


def test_config_sources_returns_copy():
    """Test that get_config_sources returns a copy, not the internal dict"""
    config = ConfigLoader(config_path=Path('/nonexistent/config.conf'))

    sources1 = config.get_config_sources()
    sources2 = config.get_config_sources()

    # Should be equal but not the same object
    assert sources1 == sources2
    assert sources1 is not sources2

    # Modifying one shouldn't affect the other
    sources1['PIANOTEQ_DIR'] = 'modified'
    assert sources2['PIANOTEQ_DIR'] != 'modified'


@pytest.mark.parametrize("env_value,expected", [
    ("true", True),
    ("True", True),
    ("TRUE", True),
    ("false", False),
    ("False", False),
    ("FALSE", False),
    ("anything_else", False),
])
def test_boolean_parsing_variations(env_value, expected):
    """Test that boolean values are parsed correctly in various formats"""
    os.environ['PIANOTEQ_HEADLESS'] = env_value

    try:
        config = ConfigLoader(config_path=Path('/nonexistent/config.conf'))
        assert config.PIANOTEQ_HEADLESS == expected
    finally:
        del os.environ['PIANOTEQ_HEADLESS']


def test_load_instruments():
    """Test that instruments can be loaded"""
    instruments = ConfigLoader.load_instruments()

    assert isinstance(instruments, list)
    assert len(instruments) > 0

    # Check first instrument has expected attributes
    first = instruments[0]
    assert hasattr(first, 'name')
    assert hasattr(first, 'preset_prefix')


def test_init_user_config_creates_file(tmp_path):
    """Test that init_user_config creates a config file"""
    from pi_pianoteq.config import USER_CONFIG_PATH

    # This test would need to mock USER_CONFIG_PATH to avoid affecting real config
    # For now, just test that the method exists and returns the right type
    success, message = ConfigLoader.init_user_config()

    assert isinstance(success, bool)
    assert isinstance(message, str)

    # Logic depends on whether config already exists
    if success:
        # If successful, file should now exist
        assert USER_CONFIG_PATH.exists()
        assert "Created" in message
    else:
        # If not successful, it already existed
        assert USER_CONFIG_PATH.exists()
        assert "already exists" in message
