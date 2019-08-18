import subprocess
from constants import PIANOTEQ_DIR, PIANOTEQ_BIN
from os.path import expanduser
from typing import List


class Pianoteq:
    def __init__(self, mapping_name: str):
        self.headless = False
        self.mapping_name = mapping_name
        self.directory = expanduser(PIANOTEQ_DIR)
        self.executable = PIANOTEQ_BIN
        self.process = None

    def get_presets(self) -> List[str]:
        pianoteq_proc = subprocess.run([self.executable, '--list-presets'],
                                       cwd=self.directory,
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return output.splitlines()

    def get_version(self) -> str:
        pianoteq_proc = subprocess.run([self.executable, '--version'],
                                       cwd=expanduser(PIANOTEQ_DIR),
                                       capture_output=True,
                                       text=True)
        pianoteq_proc.check_returncode()
        output = pianoteq_proc.stdout
        return " ".join(output.splitlines())

    def start(self):
        args = [self.executable, '--midimapping', self.mapping_name]
        if self.headless:
            args.append(['--headless'])
        self.process = subprocess.Popen(args,
                                        cwd=expanduser(PIANOTEQ_DIR),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def terminate(self):
        self.process.terminate()
