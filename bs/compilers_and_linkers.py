
import os
import subprocess
import traceback

import yaml

from bs import actions
from bs import config
from bs import objectives
from bs import logger

compilers = {}
linkers = {}

LIST = False
LIST_ALL = False
FLATTEN = False
GRAPH = False
DEBUG = False
CLEAN = False

class CMDThing(object):

    def __init__(self, function, command):
        self.function = function
        self.command = command
        self.options = []
        self.paths = []
        self.path_switch = ''
        self.output_switch = ''
        self.instances[function] = self

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.cmd)

    def run(self, objective):
        if LIST:
            print(objective)
            for item in objective:
                if LIST_ALL or not isinstance(item, objectives.Object):
                    print('    {}'.format(item))
        if GRAPH:
            raise NotImplementedError
        if FLATTEN:
            print('') # new line for separation
            print('    flattened dependencies -- also lists sources')
            print('    ----------------------')
            for item in objective.flattened_dependencies():
                print('    {}'.format(item))

        if CLEAN:
            for item in objective.flattened_dependencies():
                if not isinstance(item, objectives.Source) and os.path.exists(item.output):
                    print('removing {}'.format(item.output))
                    os.remove(item.output)
            return

        if not LIST and not GRAPH and not FLATTEN:
            full_cmd = [self.command] + self.options
            for pp in self.paths:
                full_cmd.append('{}{}'.format(self.path_switch, ip))

            for item in objective.flattened_dependencies():
                if item.needs_updating:
                    output_dir = os.path.dirname(item.output)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    specific_command = list(full_cmd)
                    for dep in item:
                        specific_command.append(dep.output)
                    print('{}'.format(' '.join(specific_command)))
                    subprocess.check_call(specific_command)


class Compiler(CMDThing):

    instances = compilers


class Linker(CMDThing):

    instances = linkers


class _CmdAction(actions.Action):

    def __init__(self, cmd_type, command, description):
        actions.Action.__init__(self, command, description)
        self.cmd_type = cmd_type
        self.cmd_type_name = cmd_type.__name__.lower()
    
    def create_cmd(self, function, command):
        global compilers, linkers
        if function in self.cmd_type.instances:
            logger.error('Cannot add a {0} with the function `{1}` because one already exists.\n'
                    'Maybe you meant to use `modify-{0}`?',
                    self.cmd_type_name, args.function)
        return self.cmd_type(function, command)

    def get_cmd(self):
        pass


class Add(_CmdAction):

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the {}, e.g. c++, Fortran, C#. If you need to add multiple '
                     'compilers for the same function, you might index them by number, or something '
                     'like that. Specific compilers can be obtained in the `objectives.py` file by '
                     'using `compilers.get_compiler(\'<function>\''.format(self.cmd_type_name))
        parser.add_argument('command',
                help='{} command, e.g. gcc, cl, ifort. This should be a single word without '
                    'spaces'.format(self.cmd_type_name))
        self._add_shared_arguments(parser)

    def add_help(self):
        return 'A new {0} can be added using the `add-{0}` command'.format(self.cmd_type_name)

    def _add_shared_arguments(self, parser):
        parser.add_argument('--paths', '-p',
                type=str,
                default=[],
                nargs='*',
                help='include paths')
        parser.add_argument('--options',
                default=[],
                nargs='*',
                help='{} options. This one is fairly annoying. In order to provide arguments that '
                    'start with a `-`. place an escaped space before the argument. For example, in *nix '
                    'systems, `\\ -O2`. On windows this would translate to, `^ -O2`.'
                    .format(self.cmd_type_name))

    def invoke(self, args):
        cmd = self.create_cmd(args.function, args.command)
        self._apply_options(cmd, args)
        config.save()

    def _apply_options(self, cmd, args):
        if args.paths:
            cmd.paths = args.paths
        if args.options:
            cmd.options = [co.strip() for co in args.options]


class Modify(Add):

    def add_arguments(self, parser):
        self._add_shared_arguments(parser)
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. The function needs to be the same as '
                     'whatever was used to add the compiler.')
        parser.add_argument('--command',
                default=None,
                help='{} command, such as `gcc`, `ld`, `cl`, `link`, `ifort`, etc.'.format(self.cmd_type_name))

    def invoke(self, args):
        global instances
        try:
            compiler = instances[self.cmd_type_name][args.function]
        except KeyError:
            logger.error('Cannot find a {0} by the function `{1}`\n'
                'The available {0}s are:\n  {}\n'
                'Maybe you entered a {0} command instead of a function.\n{}',
                self.cmd_type_name,
                function,
                '\n  '.join(str(compiler) for compiler in instances.get(self.cmd_type_name, {}).values()),
                self.add_help())
        self._apply_options(compiler, args)
        config.save()


class Remove(actions.Action):

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. The function needs to be the same as '
                     'whatever was used to add the compiler.')


def get_actions():
    return [Add(Compiler, 'add-compiler', 'Add a compiler'),
            Modify(Compiler, 'modify-compiler', 'Modify an existing compiler'),
            Remove('remove-compiler', 'Remove an existing compiler'),
            Add(Linker, 'add-linker', 'Add a linker'),
            Modify(Linker, 'modify-linker', 'Modify an existing linker'),
            Remove('remove-linker', 'Remove an existing linker'),
            ]


def save(stream):
    '''Save the compilers info into a YAML stream'''
    global compilers, linkers
    # Convert everything into a dictionay so that it is not saved as weird YAML/python objects
    for cmd_type_name, cmds in [('compilers', compilers.values()), ('linkers', linkers.values())]:
        data = dict()
        for cmd in cmds:
            data[cmd.function] = cmd.__dict__
        if data:
            stream.write(yaml.dump({ cmd_type_name : data }, default_flow_style=False))


def load(config_dict):
    '''Loads the compilers from a dict, which was read from a YAML stream.'''
    global instances
    if 'compilers' not in config_dict:
        logger.warning('No compilers defined in configuration.')
    else:
        comps = config_dict['compilers']
        for comp_name, comp_params in comps.items():
            compiler = Compiler(comp_params['function'], comp_params['command'])
            compiler.__dict__.update(comp_params)
    if 'linkers' not in config_dict:
        logger.warning('No linkers defined in configuration.')
    else:
        comps = config_dict['linkers']
        for comp_name, comp_params in comps.items():
            linker = Linker(comp_params['function'], comp_params['command'])
            linker.__dict__.update(comp_params)

