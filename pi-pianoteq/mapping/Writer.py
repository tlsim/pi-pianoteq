from mapping.mapping import Mapping
from constants import PIANOTEQ_MIDI_MAPPINGS_DIR, MIDI_MAPPING_NAME
from os.path import expanduser
from pathlib import Path


class Writer:
    def __init__(self, mapping: Mapping):
        self.mapping = mapping

    def write(self):
        mapping_dir = expanduser(PIANOTEQ_MIDI_MAPPINGS_DIR)
        Path(mapping_dir).mkdir(parents=False, exist_ok=True)
        with open(f'{mapping_dir}/{MIDI_MAPPING_NAME}.ptm', 'wb') as outfile:
            outfile.write(self.mapping.get_bytes())
