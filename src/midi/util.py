from typing import Iterator, Tuple


def program_numbers_by_channel(from_channel: int = 0) -> Iterator[Tuple[int, int]]:
    program_number = 0
    channel_number = from_channel
    while channel_number < 16:
        while program_number < 128:
            yield (channel_number, program_number)
            program_number += 1
        program_number = 0
        channel_number += 1
