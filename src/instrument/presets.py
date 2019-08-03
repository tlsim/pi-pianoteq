import subprocess

from typing import List
from instrument.Instrument import Instrument
from constants import UNKNOWN_INSTRUMENT, PIANOTEQ_BIN, PIANOTEQ_DIR


def get_presets() -> List[str]:
    pianoteq_proc = subprocess.Popen([PIANOTEQ_BIN, '--list-presets'],
                                     cwd=PIANOTEQ_DIR,
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
    output, error = pianoteq_proc.communicate()
    return output.splitlines()


def get_instruments() -> List[str]:
    with open('instruments') as instruments:
        return instruments.read().splitlines()


def group_preset_by_instrument(presets: List[str], instrument_names: List[str]) -> List[Instrument]:
    instruments = {name: Instrument(name) for name in instrument_names}
    unknown_instrument = Instrument(UNKNOWN_INSTRUMENT)
    for preset in presets:
        instrument = next((i for i in instrument_names if preset.find(i) == 0), None)
        if instrument is not None:
            instruments[instrument].add_preset(preset)
        else:
            unknown_instrument.add_preset(preset)
    grouped = [i for i in instruments.values()]
    if len(unknown_instrument.presets) > 0:
        grouped += [unknown_instrument]
    return grouped


if __name__ == '__main__':
    found_instruments = group_preset_by_instrument(get_presets(), get_instruments())
    for instrument in found_instruments:
        print('Instrument:', instrument.name)
        print('Presets: ')
        for p in instrument.presets:
            print(p)
