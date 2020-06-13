from rtmidi import MidiOut

from pi_pianoteq.config import Config
from pi_pianoteq.instrument.Library import Library
from pi_pianoteq.instrument.Selector import Selector
from pi_pianoteq.lib.ClientLib import ClientLib
from pi_pianoteq.mapping.MappingBuilder import MappingBuilder
from pi_pianoteq.mapping.Writer import Writer
from pi_pianoteq.midi.ProgramChange import ProgramChange
from pi_pianoteq.process.Pianoteq import Pianoteq
from pi_pianoteq.client.gfxhat.GfxhatClient import GfxhatClient


def main():
    pianoteq = Pianoteq()
    library = Library(pianoteq.get_presets(), Config.load_instruments())
    selector = Selector(library.get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

    print(pianoteq.get_version())

    pianoteq.start()

    midiout = MidiOut()
    midiout.open_virtual_port(Config.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    client_lib = ClientLib(library, selector, program_change)
    client = GfxhatClient(client_lib)

    client.start()
    pianoteq.terminate()


if __name__ == '__main__':
    main()
