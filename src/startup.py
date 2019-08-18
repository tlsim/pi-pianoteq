from mapping.MappingBuilder import MappingBuilder
from mapping.Writer import Writer
from instrument.library import Library, get_instruments
from process.Pianoteq import Pianoteq
from rtmidi import MidiOut
from midi.ProgramChange import ProgramChange
from time import sleep

import constants


def main():
    pianoteq = Pianoteq()
    library = Library(pianoteq.get_presets(), get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

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
