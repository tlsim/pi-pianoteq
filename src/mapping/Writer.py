from mapping.mapping import Mapping
from constants import PIANOTEQ_MIDI_MAPPINGS_DIR
from os.path import expanduser


class Writer:
    def __init__(self, mapping: Mapping):
        self.mapping = mapping

    def write(self, name: str):
        mapping_dir = expanduser(PIANOTEQ_MIDI_MAPPINGS_DIR)
        with open(f'{mapping_dir}/{name}.ptm', 'wb') as outfile:
            outfile.write(self.mapping.build())
