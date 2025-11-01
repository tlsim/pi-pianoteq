from rtmidi import MidiOut

from pi_pianoteq.instrument import Preset
from pi_pianoteq.midi.MidiException import MidiException

CHANNEL_VOICE_PC_STATUS = 0xC0


class ProgramChange:
    def __init__(self, midiout: MidiOut):
        self.midiout = midiout

    def set_preset(self, preset: Preset):
        if preset.has_midi_params():
            try:
                channel_byte = CHANNEL_VOICE_PC_STATUS + preset.midi_channel
                message = [channel_byte, preset.midi_program_number]
                self.midiout.send_message(message)
            except ValueError:
                raise MidiException(f'Failed to set preset ${preset.name}. Invalid MIDI Program Change message')
        else:
            raise MidiException(f'Failed to set preset ${preset.name}. No MIDI mapping exists for preset')

