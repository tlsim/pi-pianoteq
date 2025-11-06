from functools import reduce
from struct import pack
from typing import Optional, List

HEADER_CONST = bytes.fromhex('19a3 e038')
MAPPING_CONST = bytes.fromhex('0300 0000')
ROW_CONST = bytes.fromhex('0100 0000')
NOTES_CHANNEL_ANY = -1
NOTES_TRANSPOSITION_ZERO = 0
MIDI_DIALECT_AUTO = 3
ENCODING = 'utf-8'


class Mapping:
    def __init__(self):
        self.rows: List[Row] = []

    def add_row(self, row):
        self.rows.append(row)

    def get_bytes(self) -> bytes:
        mapping = MAPPING_CONST + \
                  pack_c_long(NOTES_CHANNEL_ANY) + \
                  pack_c_long(NOTES_TRANSPOSITION_ZERO) + \
                  pack_c_long(MIDI_DIALECT_AUTO) + \
                  pack_c_long(len(self.rows)) + \
                  reduce(lambda x, y: x + y.get_bytes(), self.rows, b'')

        return HEADER_CONST + pack_size(mapping) + mapping


class Row:
    def __init__(self, map_from: str, map_to: str):
        self.map_from = map_from
        self.map_to = map_to

    def get_bytes(self) -> bytes:
        map_from_bytes = bytes(self.map_from, ENCODING)
        map_to_bytes = bytes(self.map_to, ENCODING)
        return ROW_CONST + \
            pack_size(map_from_bytes) + \
            map_from_bytes + \
            pack_size(map_to_bytes) + \
            map_to_bytes


class ProgramChangeLoadPresetRow(Row):
    def __init__(self, preset: str, program: int, channel: Optional[int] = None):
        map_from = map_from_program_change(program, channel)
        map_to = map_to_load_preset(preset)
        super().__init__(map_from, map_to)


def pack_c_long(i: int) -> bytes:
    return pack('<l', i)


def pack_size(in_bytes: bytes) -> bytes:
    return pack_c_long(len(in_bytes))


def map_from_program_change(program: int, channel: Optional[int] = None) -> str:
    if channel is not None:
        return f'Program Change {program} / Channel{channel}'
    else:
        return f'Program Change {program}'


def map_to_load_preset(preset: str) -> str:
    return f'{{LoadPreset|28||{preset}|0}}'
