from midimapping.mapping import Mapping, Writer, ProgramChangeLoadPresetRow
from instrument.library import Library, get_instruments, get_presets


def main():
    library = Library(get_presets(), get_instruments())
    mapping = Mapping()
    for instrument in library.get_known_instruments():
        for preset in instrument.presets:
            if preset.has_midi_params():
                preset_row = ProgramChangeLoadPresetRow(preset.name, preset.midi_program_number, preset.midi_channel)
                mapping.add_row(preset_row)
    writer = Writer(mapping)
    writer.write('full_mapping')


if __name__ == "__main__":
    main()
