import json
from configparser import ConfigParser
from os import path
from typing import List

CONFIG_FILE = 'pi_pianoteq.conf'
INSTRUMENTS_FILE = 'instruments.json'
PTQ_SECTION = 'Pianoteq'
MIDI_SECTION = 'Midi'
INSTRUMENT_SECTION = 'Instrument'


class Config:
    parser = ConfigParser()
    parser.read(path.join(path.dirname(__file__), CONFIG_FILE))
    PIANOTEQ_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_DIR')
    PIANOTEQ_BIN = parser.get(PTQ_SECTION, 'PIANOTEQ_BIN')
    PIANOTEQ_DATA_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_DATA_DIR')
    PIANOTEQ_MIDI_MAPPINGS_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_MIDI_MAPPINGS_DIR')
    PIANOTEQ_PREFS_FILE = parser.get(PTQ_SECTION, 'PIANOTEQ_PREFS_FILE')
    MIDI_PORT_NAME = parser.get(MIDI_SECTION, 'MIDI_PORT_NAME')
    MIDI_MAPPING_NAME = parser.get(MIDI_SECTION, 'MIDI_MAPPING_NAME')
    UNKNOWN_INSTRUMENT = parser.get(INSTRUMENT_SECTION, 'UNKNOWN_INSTRUMENT')

    @staticmethod
    def load_instrument_config() -> List[str]:
        with open(path.join(path.dirname(__file__), INSTRUMENTS_FILE)) as instruments:
            instruments_json = json.load(instruments)
            return [instrument["preset_prefix"] for instrument in instruments_json]
