from os.path import expanduser
from pathlib import Path

from pi_pianoteq.config import Config
from pi_pianoteq.mapping.mapping import Mapping


class Writer:
    def __init__(self, mapping: Mapping):
        self.mapping = mapping

    def write(self):
        mapping_dir = expanduser(Config.PIANOTEQ_MIDI_MAPPINGS_DIR)
        Path(mapping_dir).mkdir(parents=False, exist_ok=True)
        with open(f'{mapping_dir}/{Config.MIDI_MAPPING_NAME}.ptm', 'wb') as outfile:
            outfile.write(self.mapping.get_bytes())
