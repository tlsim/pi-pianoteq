from struct import pack
from typing import Optional, List
from functools import reduce

HEADER_CONST = bytes.fromhex('19a3 e038')
MAPPING_CONST = bytes.fromhex('0300 0000')
ROW_CONST = bytes.fromhex('0100 0000')
NOTES_CHANNEL_ANY = -1
NOTES_TRANSPOSITION_ZERO = 0
MIDI_DIALECT_AUTO = 3
ENCODING = 'utf-8'

# TODO: What do the mappings look like on ARM?


class Mapping:
    def __init__(self):
        self.rows: List[Row] = []

    def add_row(self, row):
        self.rows.append(row)

    def build(self) -> bytes:
        mapping = MAPPING_CONST + \
                  pack_c_long(NOTES_CHANNEL_ANY) + \
                  pack_c_long(NOTES_TRANSPOSITION_ZERO) + \
                  pack_c_long(MIDI_DIALECT_AUTO) + \
                  pack_c_long(len(self.rows)) + \
                  reduce(lambda x, y: x + y.build(), self.rows, b'')

        return HEADER_CONST + pack_size(mapping) + mapping


class Row:
    def __init__(self, map_from: str, map_to: str):
        self.map_from = map_from
        self.map_to = map_to

    def build(self) -> bytes:
        map_from_bytes = bytes(self.map_from, ENCODING)
        map_to_bytes = bytes(self.map_to, ENCODING)
        return ROW_CONST + \
            pack_size(map_from_bytes) + \
            map_from_bytes + \
            pack_size(map_to_bytes) + \
            map_to_bytes


def pack_c_long(i: int) -> bytes:
    return pack('<l', i)


def pack_size(in_bytes: bytes) -> bytes:
    return pack_c_long(len(in_bytes))


def map_from_pc(controller: int, channel: Optional[int] = None) -> str:
    if channel is not None:
        return f'Program Change {controller} / Channel{channel}'
    else:
        return f'Program Change {controller}'


def map_to_load_preset(preset: str):
    return f'{{LoadPreset|28||{preset}|0}}'


if __name__ == '__main__':
    test_row = Row(map_from_pc(10, 5), map_to_load_preset('Toy Piano Original'))
    test_row_2 = Row(map_from_pc(11), map_to_load_preset('MKI Bark'))
    test_mapping = Mapping()
    test_mapping.add_row(test_row)
    test_mapping.add_row(test_row_2)
    output = test_mapping.build()
    with open('test_write_mapping.ptm', 'wb') as outfile:
        outfile.write(output)
