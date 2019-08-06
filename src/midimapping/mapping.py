from struct import *
from typing import Optional

HEADER_CONST = [bytes.fromhex('19a3 e038'), bytes.fromhex('0000 0300')]
ROW_CONST = bytes.fromhex('0100 0000')
NOTES_CHANNEL = -1
NOTES_TRANSPOSITION = 0
MIDI_DIALECT = 0
SIZE_TEMP = bytes.fromhex('7d01 0000')  # TODO
ROWS_TEMP = bytes.fromhex('0500 0000')  # TODO


def pack_c_long(i: int) -> bytes:
    return pack('<l', i)


def pack_size(in_bytes: bytes) -> bytes:
    return pack_c_long(len(in_bytes))  # TODO


def map_from_pc(controller: int, channel: Optional[int] = None) -> str:
    if channel is not None:
        return f'Program Change {controller} / Channel{channel}'
    else:
        return f'Program Change {controller}'


def map_to_load_preset(preset: str):
    return f'{{LoadPreset|28||{preset}|0}}'


def create_row(map_from: str, map_to: str) -> bytes:
    map_from_bytes = bytes(map_from, 'utf-8')  # TODO
    map_to_bytes = bytes(map_to, 'utf-8')
    return ROW_CONST + \
        pack_size(map_from_bytes) + \
        map_from_bytes + \
        pack_size(map_to_bytes) + \
        map_to_bytes


RESULT = HEADER_CONST[0] + \
         SIZE_TEMP + \
         HEADER_CONST[1] + \
         pack_c_long(NOTES_CHANNEL) + \
         pack_c_long(NOTES_TRANSPOSITION) + \
         pack_c_long(MIDI_DIALECT) + \
         ROWS_TEMP + \
         create_row(map_from_pc(10, 5), map_to_load_preset('Tiny Piano'))

# TODO: What do the mappings look like on ARM?
READABLE = RESULT.hex()

if __name__ == '__main__':
    print(RESULT)
    print(READABLE)
