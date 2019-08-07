from struct import *
from typing import Optional

HEADER_CONST = bytes.fromhex('19a3 e038')
MAPPING_CONST = bytes.fromhex('0300 0000')
ROW_CONST = bytes.fromhex('0100 0000')
NOTES_CHANNEL = -1
NOTES_TRANSPOSITION = 0
MIDI_DIALECT = 0
ROWS_TEMP = bytes.fromhex('0100 0000')  # TODO
ENCODING = 'utf-8'

# TODO: What do the mappings look like on ARM?


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


def create_row(map_from: str, map_to: str) -> bytes:
    map_from_bytes = bytes(map_from, ENCODING)
    map_to_bytes = bytes(map_to, ENCODING)
    return ROW_CONST + \
        pack_size(map_from_bytes) + \
        map_from_bytes + \
        pack_size(map_to_bytes) + \
        map_to_bytes


def build() -> bytes:
    mapping = MAPPING_CONST + \
        pack_c_long(NOTES_CHANNEL) + \
        pack_c_long(NOTES_TRANSPOSITION) + \
        pack_c_long(MIDI_DIALECT) + \
        ROWS_TEMP + \
        create_row(map_from_pc(10, 5), map_to_load_preset('Toy Piano Original'))

    return HEADER_CONST + pack_size(mapping) + mapping


if __name__ == '__main__':
    output = build()
    print(output)
    print(output.hex())
    with open('test_write_mapping.ptm', 'wb') as outfile:
        outfile.write(output)
