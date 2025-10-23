import json
import os
import shutil
from configparser import ConfigParser
from os import path
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pi_pianoteq.instrument.Instrument import Instrument

CONFIG_FILE = 'pi_pianoteq.conf'
INSTRUMENTS_FILE = 'instruments.json'
PTQ_SECTION = 'Pianoteq'
MIDI_SECTION = 'Midi'
SYSTEM_SECTION = 'System'

# Config file locations (in priority order: user config > bundled default)
USER_CONFIG_DIR = Path.home() / '.config' / 'pi_pianoteq'
USER_CONFIG_PATH = USER_CONFIG_DIR / CONFIG_FILE
BUNDLED_CONFIG_PATH = Path(__file__).parent / CONFIG_FILE


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
    def load_instruments() -> List[Instrument]:
        """Load instrument definitions from bundled JSON file"""
        with open(path.join(path.dirname(__file__), INSTRUMENTS_FILE)) as instruments:
            instruments_json = json.load(instruments)
            return [
                Instrument(i["name"], i["preset_prefix"], i["background_primary"], i["background_secondary"])
                for i in instruments_json
            ]

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


# Create singleton instance for backward compatibility
# Code can still use Config.PIANOTEQ_DIR etc.
Config = ConfigLoader()
