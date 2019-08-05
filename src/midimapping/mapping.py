from struct import *
import binascii

HEADER_CONSTANT = bytes.fromhex('19a3 e038')

NOTES_CHANNEL = -1

RESULT = HEADER_CONSTANT + pack('<l', NOTES_CHANNEL)
# TODO: What do the mappings look like on ARM?

READABLE = binascii.hexlify(RESULT)

if __name__ == '__main__':
    print(NOTES_CHANNEL)
    print(RESULT)
    print(READABLE)
