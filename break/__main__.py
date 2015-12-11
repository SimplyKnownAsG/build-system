
import argparse

# these imports are necessary in order to get the configurations set up
from . import objectives
from . import compilers

from . import actions
from . import config

parser = argparse.ArgumentParser(prog='custom build tool')
parser.add_argument('action',
        help='action to perform',
        nargs='?',
        default='build')

# load the current user configuration
config.load()
args, unknowns = parser.parse_known_args()

# actions:
#  config
#  add (library|executable|thing)
#  init -- covered by config
#  start

acts = {act.name: act for act in [actions.Config(), actions.Build(), actions.AddObjective(), actions.Clean()]}

try:
    action = acts[args.action]
except KeyError:
    print 'error: did not recognize action `{}`, available options are:'.format(args.action)
    for action in acts.values():
        print '  {:<15} {}'.format(action.name, action.description)
    exit(1)

parser = argparse.ArgumentParser(prog=action.name, description=action.description)
action.add_arguments(parser)
args, unknowns = parser.parse_known_args(unknowns)
action.invoke(args)

