import subprocess
from os.path import expanduser
from typing import List

from pi_pianoteq.constants import PIANOTEQ_DIR, PIANOTEQ_BIN, MIDI_MAPPING_NAME


class Pianoteq:
    def __init__(self):
        self.headless = False
        self.mapping_name = MIDI_MAPPING_NAME
        self.executable = expanduser(PIANOTEQ_DIR) + PIANOTEQ_BIN
        self.process = None

    def get_presets(self) -> List[str]:
        pianoteq_proc = subprocess.run([self.executable, '--list-presets'],
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return output.splitlines()

    def get_version(self) -> str:
        pianoteq_proc = subprocess.run([self.executable, '--version'],
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return ' '.join(output.splitlines())

    def start(self):
        args = [self.executable, '--midimapping', self.mapping_name]
        if self.headless:
            args.append(['--headless'])
        self.process = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def terminate(self):
        self.process.terminate()
