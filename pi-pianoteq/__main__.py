from mapping.MappingBuilder import MappingBuilder
from mapping.Writer import Writer
from instrument.Library import Library, get_instruments
from process.Pianoteq import Pianoteq
from rtmidi import MidiOut
from midi.ProgramChange import ProgramChange
from lib.ClientLib import ClientLib
from client.cli.CliClient import CliClient

import constants


def main():
    pianoteq = Pianoteq()
    library = Library(pianoteq.get_presets(), get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

    print(pianoteq.get_version())
    pianoteq.start()

    midiout = MidiOut()
    midiout.open_virtual_port(constants.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    client_lib = ClientLib(library, program_change)
    client = CliClient(client_lib)

    # program_change.set_preset(library.get_current_preset())
    client.start()
    pianoteq.terminate()


if __name__ == '__main__':
    main()
