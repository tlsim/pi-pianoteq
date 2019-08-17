from mapping.mapping import Mapping, Writer, ProgramChangeLoadPresetRow
from instrument.library import Library, get_instruments, get_presets
from rtmidi import MidiOut
from midi.ProgramChange import ProgramChange
from time import sleep

import constants


def main():
    library = Library(get_presets(), get_instruments())
    mapping = Mapping()
    for instrument in library.get_known_instruments():
        for preset in instrument.presets:
            if preset.has_midi_params():
                ptq_program = preset.midi_program_number + 1
                ptq_channel = preset.midi_channel + 1
                preset_row = ProgramChangeLoadPresetRow(preset.name, ptq_program, ptq_channel)
                mapping.add_row(preset_row)
    writer = Writer(mapping)
    writer.write('full_mapping')

    # TODO: Start PTQ with the created mapping loaded
    sleep(10)
    print("Will switch presets every 5 seconds")

    midiout = MidiOut()
    midiout.open_virtual_port(constants.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    for instrument in library.get_known_instruments():
        preset = instrument.presets[0]
        sleep(5)
        program_change.set_preset(preset)


if __name__ == "__main__":
    main()
