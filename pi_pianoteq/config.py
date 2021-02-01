import json
from configparser import ConfigParser
from os import path
from typing import List
from pi_pianoteq.instrument.Instrument import Instrument

CONFIG_FILE = 'pi_pianoteq.conf'
INSTRUMENTS_FILE = 'instruments.json'
PTQ_SECTION = 'Pianoteq'
MIDI_SECTION = 'Midi'
SYSTEM_SECTION = 'System'


class Config:
    parser = ConfigParser()
    parser.read(path.join(path.dirname(__file__), CONFIG_FILE))
    PIANOTEQ_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_DIR')
    PIANOTEQ_BIN = parser.get(PTQ_SECTION, 'PIANOTEQ_BIN')
    PIANOTEQ_DATA_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_DATA_DIR')
    PIANOTEQ_MIDI_MAPPINGS_DIR = parser.get(PTQ_SECTION, 'PIANOTEQ_MIDI_MAPPINGS_DIR')
    PIANOTEQ_PREFS_FILE = parser.get(PTQ_SECTION, 'PIANOTEQ_PREFS_FILE')
    PIANOTEQ_HEADLESS = parser.get(PTQ_SECTION, 'PIANOTEQ_HEADLESS') == "true"
    MIDI_PORT_NAME = parser.get(MIDI_SECTION, 'MIDI_PORT_NAME')
    MIDI_MAPPING_NAME = parser.get(MIDI_SECTION, 'MIDI_MAPPING_NAME')
    MIDI_PIANOTEQ_STARTUP_DELAY = int(parser.get(MIDI_SECTION, 'MIDI_PIANOTEQ_STARTUP_DELAY'))
    SHUTDOWN_COMMAND = parser.get(SYSTEM_SECTION, 'SHUTDOWN_COMMAND')

    @staticmethod
    def load_instruments() -> List[Instrument]:
        with open(path.join(path.dirname(__file__), INSTRUMENTS_FILE)) as instruments:
            instruments_json = json.load(instruments)
            return [
                Instrument(i["name"], i["preset_prefix"], i["background_primary"], i["background_secondary"])
                for i in instruments_json
            ]
