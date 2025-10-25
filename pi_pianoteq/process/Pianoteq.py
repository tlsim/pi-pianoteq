import subprocess
from os.path import expanduser
from typing import List

from pi_pianoteq.config import Config


class Pianoteq:
    def __init__(self):
        self.headless = Config.PIANOTEQ_HEADLESS
        self.mapping_name = Config.MIDI_MAPPING_NAME
        self.executable = expanduser(Config.PIANOTEQ_DIR) + Config.PIANOTEQ_BIN
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
            args.append('--headless')
        args.extend(['--serve', ''])  # Enable JSON-RPC API on localhost:8081 (empty string = default)
        self.process = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def terminate(self):
        if self.process.returncode is not None:
            self.process.terminate()
