import subprocess

PIANOTEQ_DIR = '/home/tom/pianoteq/Pianoteq 6 STAGE/amd64'
PIANOTEQ_BIN = './Pianoteq 6 STAGE'

pianoteq_proc = subprocess.Popen([PIANOTEQ_BIN, '--list-presets'], cwd=PIANOTEQ_DIR, stdout=subprocess.PIPE, universal_newlines=True)
output, error = pianoteq_proc.communicate()
print(output.splitlines())

# Group by instrument / Find instrument prefix:
# Sequential longest common prefix with constraints:
# prefix means a substring that starts at start of preset name
# prefix must end with an alphabetic character preceding a single space,
# suffix must be longer than single character after the space
# Sequential means new prefix if zero chars match current prefix
# (i.e expect can do this iteratively, the output is already grouped)
