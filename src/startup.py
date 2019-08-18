from mapping.mapping import Mapping, ProgramChangeLoadPresetRow
from mapping.Writer import Writer
from instrument.library import Library, get_instruments
from process.Pianoteq import Pianoteq
from rtmidi import MidiOut
from midi.ProgramChange import ProgramChange
from time import sleep

import constants


def main():
    mapping_name = 'full_mapping_aug18'
    pianoteq = Pianoteq(mapping_name)

    library = Library(pianoteq.get_presets(), get_instruments())
    mapping = Mapping()
    for instrument in library.get_known_instruments():
        for preset in instrument.presets:
            if preset.has_midi_params():
                ptq_program = preset.midi_program_number + 1
                ptq_channel = preset.midi_channel + 1
                preset_row = ProgramChangeLoadPresetRow(preset.name, ptq_program, ptq_channel)
                mapping.add_row(preset_row)
    writer = Writer(mapping)
    writer.write(mapping_name)

    print(pianoteq.get_version())
    pianoteq.start()
    print("Will switch presets every 2 seconds")

    midiout = MidiOut()
    midiout.open_virtual_port(constants.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    for instrument in library.get_known_instruments():
        preset = instrument.presets[0]
        sleep(2)
        program_change.set_preset(preset)

    pianoteq.terminate()


if __name__ == "__main__":
    main()
