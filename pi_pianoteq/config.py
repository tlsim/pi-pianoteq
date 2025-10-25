import json
import logging
import os
import re
import shutil
from configparser import ConfigParser
from os import path
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pi_pianoteq.instrument.Instrument import Instrument

logger = logging.getLogger(__name__)

CONFIG_FILE = 'pi_pianoteq.conf'
INSTRUMENTS_FILE = 'instruments.json'
PTQ_SECTION = 'Pianoteq'
MIDI_SECTION = 'Midi'
SYSTEM_SECTION = 'System'

# Config file locations (in priority order: user config > bundled default)
USER_CONFIG_DIR = Path.home() / '.config' / 'pi_pianoteq'
USER_CONFIG_PATH = USER_CONFIG_DIR / CONFIG_FILE
BUNDLED_CONFIG_PATH = Path(__file__).parent / CONFIG_FILE

# Instruments file locations (in priority order: user config > bundled default)
USER_INSTRUMENTS_PATH = USER_CONFIG_DIR / INSTRUMENTS_FILE
BUNDLED_INSTRUMENTS_PATH = Path(__file__).parent / INSTRUMENTS_FILE

# Default colors if not specified (using common piano colors from bundled config)
# These provide visible backlight while being neutral
DEFAULT_PRIMARY_COLOR = '#040404'    # Nearly black but visible
DEFAULT_SECONDARY_COLOR = '#2e3234'  # Dark gray


class ConfigLoader:
    """Configuration loader with priority: env vars > user config > bundled default"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_path: Optional path to config file (for testing).
                        If None, uses standard priority: user config > bundled default
        """
        self._config_sources: Dict[str, str] = {}  # Track where each value came from

        # Load default config (bundled with package)
        default_parser = ConfigParser()
        default_parser.read(BUNDLED_CONFIG_PATH)

        # Load user config if exists (or custom path for testing)
        user_parser = ConfigParser()
        if config_path:
            user_parser.read(config_path)
            user_config_loaded = config_path.exists()
        else:
            user_parser.read(USER_CONFIG_PATH)
            user_config_loaded = USER_CONFIG_PATH.exists()

        # Load each config value with priority: env var > user config > default
        self.PIANOTEQ_DIR = self._get_config('PIANOTEQ_DIR', PTQ_SECTION, user_parser, default_parser, user_config_loaded)
        self.PIANOTEQ_BIN = self._get_config('PIANOTEQ_BIN', PTQ_SECTION, user_parser, default_parser, user_config_loaded)
        self.PIANOTEQ_DATA_DIR = self._get_config('PIANOTEQ_DATA_DIR', PTQ_SECTION, user_parser, default_parser, user_config_loaded)
        self.PIANOTEQ_MIDI_MAPPINGS_DIR = self._get_config('PIANOTEQ_MIDI_MAPPINGS_DIR', PTQ_SECTION, user_parser, default_parser, user_config_loaded)
        self.PIANOTEQ_PREFS_FILE = self._get_config('PIANOTEQ_PREFS_FILE', PTQ_SECTION, user_parser, default_parser, user_config_loaded)

        headless_str = self._get_config('PIANOTEQ_HEADLESS', PTQ_SECTION, user_parser, default_parser, user_config_loaded)
        self.PIANOTEQ_HEADLESS = headless_str.lower() == "true"

        self.MIDI_PORT_NAME = self._get_config('MIDI_PORT_NAME', MIDI_SECTION, user_parser, default_parser, user_config_loaded)
        self.MIDI_MAPPING_NAME = self._get_config('MIDI_MAPPING_NAME', MIDI_SECTION, user_parser, default_parser, user_config_loaded)

        startup_delay_str = self._get_config('MIDI_PIANOTEQ_STARTUP_DELAY', MIDI_SECTION, user_parser, default_parser, user_config_loaded)
        self.MIDI_PIANOTEQ_STARTUP_DELAY = int(startup_delay_str)

        self.SHUTDOWN_COMMAND = self._get_config('SHUTDOWN_COMMAND', SYSTEM_SECTION, user_parser, default_parser, user_config_loaded)

    def _get_config(self, key: str, section: str, user_parser: ConfigParser,
                   default_parser: ConfigParser, user_config_loaded: bool) -> str:
        """
        Get config value with priority: env var > user config > default.
        Also tracks the source of each value for debugging.
        """
        # Check environment variable first
        env_value = os.getenv(key)
        if env_value is not None:
            self._config_sources[key] = 'environment'
            return env_value

        # Check user config
        if user_config_loaded and user_parser.has_option(section, key):
            self._config_sources[key] = 'user_config'
            return user_parser.get(section, key)

        # Fall back to default
        self._config_sources[key] = 'bundled_default'
        return default_parser.get(section, key)

    def get_config_sources(self) -> Dict[str, str]:
        """Return a dict showing where each config value came from (for debugging)"""
        return self._config_sources.copy()

    @staticmethod
    def _validate_hex_color(color: str) -> bool:
        """Validate hex color format (#RRGGBB)"""
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    @staticmethod
    def _validate_instrument_entry(entry: dict, index: int) -> Optional[Dict[str, str]]:
        """
        Validate and normalize a single instrument entry.

        Args:
            entry: Raw instrument dict from JSON
            index: Index in array (for error messages)

        Returns:
            Validated dict with all required fields, or None if invalid
        """
        # Required fields
        if 'name' not in entry:
            logger.warning(f"Instrument at index {index} missing required field 'name', skipping")
            return None
        if 'preset_prefix' not in entry:
            logger.warning(f"Instrument '{entry['name']}' missing required field 'preset_prefix', skipping")
            return None

        # Optional color fields with defaults
        primary = entry.get('background_primary', DEFAULT_PRIMARY_COLOR)
        secondary = entry.get('background_secondary', DEFAULT_SECONDARY_COLOR)

        # Validate color formats
        if not ConfigLoader._validate_hex_color(primary):
            logger.warning(f"Instrument '{entry['name']}' has invalid background_primary '{primary}', using default")
            primary = DEFAULT_PRIMARY_COLOR
        if not ConfigLoader._validate_hex_color(secondary):
            logger.warning(f"Instrument '{entry['name']}' has invalid background_secondary '{secondary}', using default")
            secondary = DEFAULT_SECONDARY_COLOR

        return {
            'name': entry['name'],
            'preset_prefix': entry['preset_prefix'],
            'background_primary': primary,
            'background_secondary': secondary
        }

    @staticmethod
    def load_instruments() -> List[Instrument]:
        """
        Load instrument definitions from JSON file.

        Priority: user config (~/.config/pi_pianoteq/instruments.json) > bundled default

        The JSON should be an array of objects with these fields:
        - name (required): Display name of the instrument
        - preset_prefix (required): String prefix for matching Pianoteq presets
        - background_primary (optional): Hex color for primary backlight (#RRGGBB)
        - background_secondary (optional): Hex color for secondary backlight (#RRGGBB)

        Returns:
            List of validated Instrument objects
        """
        # Determine which file to load (user config takes priority)
        instruments_path = USER_INSTRUMENTS_PATH if USER_INSTRUMENTS_PATH.exists() else BUNDLED_INSTRUMENTS_PATH

        if instruments_path == USER_INSTRUMENTS_PATH:
            logger.info(f"Loading instruments from user config: {USER_INSTRUMENTS_PATH}")
        else:
            logger.debug(f"Loading instruments from bundled default: {BUNDLED_INSTRUMENTS_PATH}")

        try:
            with open(instruments_path) as f:
                instruments_json = json.load(f)

            if not isinstance(instruments_json, list):
                logger.error(f"Invalid instruments.json: expected array, got {type(instruments_json).__name__}")
                logger.warning("Falling back to bundled instruments")
                if instruments_path != BUNDLED_INSTRUMENTS_PATH:
                    with open(BUNDLED_INSTRUMENTS_PATH) as f:
                        instruments_json = json.load(f)
                else:
                    return []

            # Validate and normalize each entry
            validated_instruments = []
            for idx, entry in enumerate(instruments_json):
                if not isinstance(entry, dict):
                    logger.warning(f"Instrument at index {idx} is not an object, skipping")
                    continue

                validated = ConfigLoader._validate_instrument_entry(entry, idx)
                if validated:
                    validated_instruments.append(
                        Instrument(
                            validated['name'],
                            validated['preset_prefix'],
                            validated['background_primary'],
                            validated['background_secondary']
                        )
                    )

            if not validated_instruments:
                logger.warning("No valid instruments found in instruments.json")

            return validated_instruments

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse instruments.json: {e}")
            if instruments_path != BUNDLED_INSTRUMENTS_PATH:
                logger.warning("Falling back to bundled instruments")
                with open(BUNDLED_INSTRUMENTS_PATH) as f:
                    instruments_json = json.load(f)
                    return [
                        Instrument(i["name"], i["preset_prefix"], i["background_primary"], i["background_secondary"])
                        for i in instruments_json
                    ]
            return []
        except Exception as e:
            logger.error(f"Failed to load instruments: {e}")
            return []

    @staticmethod
    def init_user_config() -> Tuple[bool, str]:
        """
        Copy default config to user config directory.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if USER_CONFIG_PATH.exists():
            return False, f"Config already exists at {USER_CONFIG_PATH}"

        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(BUNDLED_CONFIG_PATH, USER_CONFIG_PATH)
        return True, f"Created config at {USER_CONFIG_PATH}"

    @staticmethod
    def init_user_instruments() -> Tuple[bool, str]:
        """
        Copy bundled instruments.json to user config directory as a template.

        This allows users to customize which instruments appear in the interface
        based on which Pianoteq instruments they have purchased.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if USER_INSTRUMENTS_PATH.exists():
            return False, f"Instruments config already exists at {USER_INSTRUMENTS_PATH}"

        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(BUNDLED_INSTRUMENTS_PATH, USER_INSTRUMENTS_PATH)
        return True, f"Created instruments config at {USER_INSTRUMENTS_PATH}"


# Create singleton instance for backward compatibility
# Code can still use Config.PIANOTEQ_DIR etc.
Config = ConfigLoader()
