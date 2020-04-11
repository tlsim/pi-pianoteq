from rtmidi import MidiOut

from pi_pianoteq.constants import MIDI_PORT_NAME
from pi_pianoteq.client.cli.CliClient import CliClient
from pi_pianoteq.instrument.Library import Library, get_instruments
from pi_pianoteq.lib.ClientLib import ClientLib
from pi_pianoteq.mapping.MappingBuilder import MappingBuilder
from pi_pianoteq.mapping.Writer import Writer
from pi_pianoteq.midi.ProgramChange import ProgramChange
from pi_pianoteq.process.Pianoteq import Pianoteq


def main():
    pianoteq = Pianoteq()
    library = Library(pianoteq.get_presets(), get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

    print(pianoteq.get_version())
    pianoteq.start()

    midiout = MidiOut()
    midiout.open_virtual_port(MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    client_lib = ClientLib(library, program_change)
    client = CliClient(client_lib)

    # program_change.set_preset(library.get_current_preset())
    client.start()
    pianoteq.terminate()


if __name__ == '__main__':
    main()
