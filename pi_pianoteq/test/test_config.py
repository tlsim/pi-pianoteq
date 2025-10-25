import os
import tempfile
import json
from pathlib import Path
import pytest

from pi_pianoteq.config import (
    ConfigLoader,
    BUNDLED_CONFIG_PATH,
    BUNDLED_INSTRUMENTS_PATH,
    DEFAULT_PRIMARY_COLOR,
    DEFAULT_SECONDARY_COLOR,
    COLOR_CATEGORIES
)


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


# Tests for instruments loading and validation

def test_bundled_instruments_exists():
    """Test that bundled instruments.json file exists"""
    assert BUNDLED_INSTRUMENTS_PATH.exists()


def test_load_instruments_from_bundled():
    """Test loading instruments from bundled default"""
    instruments = ConfigLoader.load_instruments()

    assert isinstance(instruments, list)
    assert len(instruments) > 0

    # Check first instrument has expected attributes
    first = instruments[0]
    assert hasattr(first, 'name')
    assert hasattr(first, 'preset_prefix')
    assert hasattr(first, 'background_primary')
    assert hasattr(first, 'background_secondary')


def test_validate_hex_color():
    """Test hex color validation"""
    assert ConfigLoader._validate_hex_color('#000000') is True
    assert ConfigLoader._validate_hex_color('#FFFFFF') is True
    assert ConfigLoader._validate_hex_color('#af2523') is True
    assert ConfigLoader._validate_hex_color('#AF2523') is True

    # Invalid formats
    assert ConfigLoader._validate_hex_color('000000') is False  # Missing #
    assert ConfigLoader._validate_hex_color('#00000') is False  # Too short
    assert ConfigLoader._validate_hex_color('#0000000') is False  # Too long
    assert ConfigLoader._validate_hex_color('#GGGGGG') is False  # Invalid hex
    assert ConfigLoader._validate_hex_color('not a color') is False


def test_validate_instrument_entry_valid():
    """Test validation of valid instrument entry"""
    entry = {
        'name': 'Test Instrument',
        'preset_prefix': 'Test',
        'background_primary': '#000000',
        'background_secondary': '#FFFFFF'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    assert result['name'] == 'Test Instrument'
    assert result['preset_prefix'] == 'Test'
    assert result['background_primary'] == '#000000'
    assert result['background_secondary'] == '#FFFFFF'


def test_validate_instrument_entry_missing_name():
    """Test validation fails when name is missing"""
    entry = {
        'preset_prefix': 'Test',
        'background_primary': '#000000',
        'background_secondary': '#FFFFFF'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)
    assert result is None


def test_validate_instrument_entry_missing_preset_prefix():
    """Test validation fails when preset_prefix is missing"""
    entry = {
        'name': 'Test Instrument',
        'background_primary': '#000000',
        'background_secondary': '#FFFFFF'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)
    assert result is None


def test_validate_instrument_entry_missing_colors():
    """Test validation succeeds with default colors when colors are missing"""
    entry = {
        'name': 'Test Instrument',
        'preset_prefix': 'Test'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    assert result['name'] == 'Test Instrument'
    assert result['preset_prefix'] == 'Test'
    assert result['background_primary'] == DEFAULT_PRIMARY_COLOR
    assert result['background_secondary'] == DEFAULT_SECONDARY_COLOR


def test_validate_instrument_entry_invalid_colors():
    """Test validation replaces invalid colors with defaults"""
    entry = {
        'name': 'Test Instrument',
        'preset_prefix': 'Test',
        'background_primary': 'invalid',
        'background_secondary': '#ZZZ'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    assert result['background_primary'] == DEFAULT_PRIMARY_COLOR
    assert result['background_secondary'] == DEFAULT_SECONDARY_COLOR


def test_init_user_instruments():
    """Test that init_user_instruments returns correct types"""
    success, message = ConfigLoader.init_user_instruments()

    assert isinstance(success, bool)
    assert isinstance(message, str)

    # If successful, message should mention created
    # If not successful, should mention already exists
    if success:
        assert "Created" in message
    else:
        assert "already exists" in message


# Tests for category support

def test_validate_instrument_entry_with_category():
    """Test validation with category field"""
    entry = {
        'name': 'Test Piano',
        'preset_prefix': 'Test',
        'category': 'piano'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    assert result['name'] == 'Test Piano'
    assert result['preset_prefix'] == 'Test'
    # Should resolve piano category to its colors
    assert result['background_primary'] == '#040404'
    assert result['background_secondary'] == '#2e3234'


def test_validate_instrument_entry_category_overrides_default():
    """Test that category overrides defaults"""
    entry = {
        'name': 'Test Electric',
        'preset_prefix': 'Test',
        'category': 'electric-tines'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    # Should use electric-tines colors, not default piano colors
    assert result['background_primary'] == '#af2523'
    assert result['background_secondary'] == '#1b1b1b'


def test_validate_instrument_entry_manual_colors_override_category():
    """Test that manual colors override category"""
    entry = {
        'name': 'Test',
        'preset_prefix': 'Test',
        'category': 'piano',  # This would give #040404/#2e3234
        'background_primary': '#ff0000',  # But manual color overrides
        'background_secondary': '#00ff00'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    # Manual colors should win
    assert result['background_primary'] == '#ff0000'
    assert result['background_secondary'] == '#00ff00'


def test_validate_instrument_entry_invalid_category():
    """Test that invalid category falls back to default"""
    entry = {
        'name': 'Test',
        'preset_prefix': 'Test',
        'category': 'nonexistent-category'
    }

    result = ConfigLoader._validate_instrument_entry(entry, 0)

    assert result is not None
    # Should fall back to default piano colors
    assert result['background_primary'] == '#040404'
    assert result['background_secondary'] == '#2e3234'


def test_all_color_categories_defined():
    """Test that all expected color categories are defined"""
    expected_categories = [
        'piano', 'electric-tines', 'electric-keys', 'vibraphone',
        'percussion-mallet', 'percussion-wood', 'percussion-metal',
        'harpsichord', 'harp', 'historical'
    ]

    for category in expected_categories:
        assert category in COLOR_CATEGORIES
        primary, secondary = COLOR_CATEGORIES[category]
        # Verify colors are valid hex
        assert ConfigLoader._validate_hex_color(primary)
        assert ConfigLoader._validate_hex_color(secondary)


def test_migrated_instruments_use_categories():
    """Test that migrated bundled instruments.json uses categories"""
    import json

    with open(BUNDLED_INSTRUMENTS_PATH) as f:
        instruments_json = json.load(f)

    # Check that at least some instruments use the category field
    categories_found = [inst.get('category') for inst in instruments_json if 'category' in inst]

    assert len(categories_found) > 0, "Bundled instruments.json should use category field"

    # All categories should be valid
    for category in categories_found:
        if category is not None:
            assert category in COLOR_CATEGORIES, f"Invalid category '{category}' in bundled instruments.json"
