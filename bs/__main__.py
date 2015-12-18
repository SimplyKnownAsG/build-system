
import argparse
import sys

# these imports are necessary in order to get the configurations set up
from bs import objectives
from bs import compilers_and_linkers
from bs import builders
from bs import actions
from bs import config
from bs import logger

command = sys.argv[1] if len(sys.argv) >= 2 else 'build'

# load the current user configuration
config.load()

# actions:
#  config
#  add (library|executable|thing)
#  init -- covered by config
#  start

acts = dict()
for act_class in [actions.Config, actions.Build, actions.AddObjective, actions.Clean, actions.Demo]:
    action = act_class()
    if action.name in acts:
        logger.internal_error('an action with the name `{}` already exists.\n'
                'Both `{}` and `{}` have the same command name, one needs to be changed or removed',
                acts[action.name].__class__, action_class)
    acts[action.name] = action
for action in  builders.get_actions() + compilers_and_linkers.get_actions():
    if action.name in acts:
        logger.internal_error('an action with the name `{}` already exists.\n'
                'Both `{}` and `{}` have the same command name, one needs to be changed or removed',
                acts[action.name].__class__, action_class)
    acts[action.name] = action


try:
    action = acts[command]
except KeyError:
    print('error: did not recognize action `{}`, available options are:'.format(command))
    for action in acts.values():
        print('  {:<15} {}'.format(action.name, action.description))
    exit(1)

parser = argparse.ArgumentParser(prog=action.name, description=action.description)
action.add_arguments(parser)
args, unknowns = parser.parse_known_args(sys.argv[2:])
action.invoke(args)

