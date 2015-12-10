
import argparse

# these imports are necessary in order to get the configurations set up
from . import targets
from . import compilers

from . import config

parser = argparse.ArgumentParser(prog='custom build tool')
parser.add_argument('--dump-config', '-D', # -d will be used for debug
        help='dump config settings and exit',
        action='store_true')
config.add_command_line_args(parser)
config.load()
args, unknowns = parser.parse_known_args()

config.save()
if args.dump_config:
    config.print_config()
    exit()

