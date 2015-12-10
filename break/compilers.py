
from . import config

class Compiler(object):

    def __init__(self, command, *options):
        self.command = command
        self.options = list(options) or []

    def compile(self, source_path, out_path):
        full_command = [self.command] + self.options + [source_path, '-o', out_path]
        subprocess.check_call(full_command)

