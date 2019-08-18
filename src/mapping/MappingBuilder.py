from mapping.mapping import Mapping, ProgramChangeLoadPresetRow
from instrument.library import Library


class MappingBuilder:
    def __init__(self, library: Library):
        self.mapping = Mapping()
        self.library = library

    def build_program_change_rows(self):
        for instrument in self.library.get_known_instruments():
            for preset in instrument.presets:
                if preset.has_midi_params():
                    ptq_program = preset.midi_program_number + 1
                    ptq_channel = preset.midi_channel + 1
                    preset_row = ProgramChangeLoadPresetRow(preset.name, ptq_program, ptq_channel)
                    self.mapping.add_row(preset_row)

    def build(self) -> Mapping:
        self.build_program_change_rows()
        return self.mapping
