import json
import logging
import os
import re
import shutil
from configparser import ConfigParser
from os import path
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset

logger = logging.getLogger(__name__)

CONFIG_FILE = 'pi_pianoteq.conf'
PTQ_SECTION = 'Pianoteq'
MIDI_SECTION = 'Midi'
SYSTEM_SECTION = 'System'

# Config file locations (in priority order: user config > bundled default)
USER_CONFIG_DIR = Path.home() / '.config' / 'pi_pianoteq'
USER_CONFIG_PATH = USER_CONFIG_DIR / CONFIG_FILE
BUNDLED_CONFIG_PATH = Path(__file__).parent / CONFIG_FILE


# Color category mappings - preserves all existing instrument colors
# Each category maps to (primary, secondary) hex color pairs
COLOR_CATEGORIES = {
    'piano': ('#040404', '#2e3234'),              # Modern grand/upright pianos
    'electric-tines': ('#af2523', '#1b1b1b'),     # Vintage Tines/Reeds
    'electric-keys': ('#cc481c', '#ea673b'),      # Clavinet, Pianet, Electra
    'vibraphone': ('#735534', '#a68454'),         # Vibraphone
    'percussion-mallet': ('#a67247', '#bf814e'),  # Celesta, Glockenspiel, Toy Piano, Kalimba
    'percussion-wood': ('#732e1f', '#959998'),    # Marimba, Xylophone
    'percussion-metal': ('#382d2b', '#6c2f1a'),   # Steel Drum, Spacedrum, Hand Pan, Tank Drum
    'harpsichord': ('#251310', '#4d281b'),        # Harpsichord
    'harp': ('#743620', '#b95d36'),               # Concert Harp
    'historical': ('#33150f', '#73422e'),         # Historical pianos
}

# Default category and colors if not specified
DEFAULT_CATEGORY = 'piano'
DEFAULT_PRIMARY_COLOR = '#040404'    # Nearly black but visible
DEFAULT_SECONDARY_COLOR = '#2e3234'  # Dark gray


def map_instrument_to_category(instr_name: str, preset_class: str) -> str:
    """
    Map Pianoteq API instrument name + class to color category.

    Preserves all 37 existing instrument colors via hardcoded mappings.
    Uses smart heuristics for new instruments not in the original config.

    Args:
        instr_name: Instrument name from API 'instr' field
        preset_class: Instrument class from API 'class' field

    Returns:
        Color category name (one of COLOR_CATEGORIES keys)
    """
    # Preserve all 37 original instrument→category mappings
    KNOWN_INSTRUMENTS = {
        'Grand C. Bechstein DG': 'piano',
        'Grand Ant. Petrof': 'piano',
        'Grand Steingraeber': 'piano',
        'Grand Grotrian': 'piano',
        'Grand Blüthner': 'piano',
        'Grand YC5': 'piano',
        'Grand K2': 'piano',
        'Upright U4': 'piano',
        'Vintage Tines MKI': 'electric-tines',
        'Vintage Tines MKII': 'electric-tines',
        'Vintage Reeds': 'electric-tines',
        'Clavinet D6': 'electric-keys',
        'Pianet N': 'electric-keys',
        'Pianet T': 'electric-keys',
        'Electra-Piano': 'electric-keys',
        'Vibraphone V-B': 'vibraphone',
        'Vibraphone V-M': 'vibraphone',
        'Celesta': 'percussion-mallet',
        'Glockenspiel': 'percussion-mallet',
        'Toy Piano': 'percussion-mallet',
        'Kalimba': 'percussion-mallet',
        'Marimba': 'percussion-wood',
        'Xylophone': 'percussion-wood',
        'Steel Drum': 'percussion-metal',
        'Spacedrum': 'percussion-metal',
        'Hand Pan': 'percussion-metal',
        'Tank Drum': 'percussion-metal',
        'H. Ruckers II Harpsichord': 'harpsichord',
        'Concert Harp': 'harp',
        'J. Dohnal (1795)': 'historical',
        'I. Besendorfer (1829)': 'historical',
        'S. Erard (1849)': 'historical',
        'J.B. Streicher (1852)': 'historical',
        'J. Broadwood (1796)': 'historical',
        'I. Pleyel (1835)': 'historical',
        'J. Frenzel (1841)': 'historical',
        'C. Bechstein (1899)': 'historical',
    }

    # Check if this is a known instrument (preserves original colors)
    if instr_name in KNOWN_INSTRUMENTS:
        return KNOWN_INSTRUMENTS[instr_name]

    # Smart detection for new instruments based on API class + name
    name_lower = instr_name.lower()

    if preset_class == "Acoustic Piano":
        return "piano"

    elif preset_class == "Historical Piano":
        return "historical"

    elif preset_class == "Electric Piano":
        # Distinguish Tines from Keys based on instrument name
        if any(kw in name_lower for kw in ['tines', 'rhodes', 'reeds', 'wurlitzer']):
            return "electric-tines"
        else:
            return "electric-keys"

    elif preset_class == "Chromatic Percussion":
        # Smart detection based on instrument name
        if 'vibraphone' in name_lower or 'vibes' in name_lower:
            return "vibraphone"
        elif any(kw in name_lower for kw in ['marimba', 'xylophone']):
            return "percussion-wood"
        else:
            return "percussion-mallet"

    elif preset_class == "Steelpan":
        return "percussion-metal"

    elif preset_class == "Piano Predecessor":
        if 'harpsichord' in name_lower:
            return "harpsichord"
        elif 'harp' in name_lower:
            return "harp"
        else:
            return "historical"

    # Safe default for unknown types
    return "piano"


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
    def discover_instruments_from_api(jsonrpc_client, include_demo: bool = False, skip_fallback: bool = False) -> List[Instrument]:
        """
        Discover instruments from Pianoteq JSON-RPC API.

        Groups presets by instrument and assigns colors based on type.
        Calculates display names based on longest common word prefix.
        """
        from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpcError
        from pi_pianoteq.instrument.preset import find_longest_common_word_prefix, calculate_display_name

        try:
            presets = jsonrpc_client.get_presets()
        except PianoteqJsonRpcError as e:
            logger.error(f"Failed to fetch presets from Pianoteq API: {e}")
            logger.error("Make sure Pianoteq is running with --serve flag")
            return []

        # First pass: group preset names by instrument and create Instrument objects
        instruments_dict = {}  # {instr_name: Instrument}
        preset_names_by_instrument = {}  # {instr_name: [preset_names]}
        preset_order = []  # Track order for maintaining API sorting

        for preset_data in presets:
            instr_name = preset_data['instr']
            license_status = preset_data.get('license_status', 'unknown')

            # Filter: only include licensed instruments (license_status == "ok")
            # Demos (license_status == "demo") have limited functionality
            if not include_demo and license_status != 'ok':
                continue

            if instr_name not in instruments_dict:
                category = map_instrument_to_category(instr_name, preset_data['class'])
                primary, secondary = COLOR_CATEGORIES[category]

                instrument = Instrument(
                    name=instr_name,
                    preset_prefix=instr_name,
                    bg_primary=primary,
                    bg_secondary=secondary
                )
                instruments_dict[instr_name] = instrument
                preset_names_by_instrument[instr_name] = []
                preset_order.append(instr_name)

            preset_names_by_instrument[instr_name].append(preset_data['name'])

        # Second pass: calculate common prefix for each instrument and create Preset objects
        for instr_name in preset_order:
            preset_names = preset_names_by_instrument[instr_name]
            common_prefix = find_longest_common_word_prefix(preset_names)

            for preset_name in preset_names:
                display_name = calculate_display_name(preset_name, common_prefix)
                preset = Preset(preset_name, display_name=display_name)
                instruments_dict[instr_name].add_preset(preset)

        result = [instruments_dict[name] for name in preset_order]
        logger.info(f"Discovered {len(result)} instruments from Pianoteq API")

        # Fallback to demos if no licensed instruments found
        if not result and not include_demo and not skip_fallback:
            logger.info("No licensed instruments found, including demo instruments")
            return ConfigLoader.discover_instruments_from_api(jsonrpc_client, include_demo=True, skip_fallback=True)

        return result

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
