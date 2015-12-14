
import os
import subprocess
import traceback

import yaml

from bs import actions
from bs import config
from bs import objectives
from bs import logger

instances = {}
'''Instances of compiler objects'''

LIST = False
LIST_ALL = False
FLATTEN = False
GRAPH = False
DEBUG = False
CLEAN = False

def get_compiler(function):
    try:
        return instances[function]
    except KeyError:
        logger.trace(-3, -2)
        logger.error('There is no compiler with the function name `{}`.\n'
                'The available compilers are:\n  {}\n{}',
                function, '\n  '.join(str(compiler) for compiler in instances.values()), Add.help)



class Add(actions.Action):

    help = 'New compiler functions can be added using `add-compiler <function> <command>`'

    def __init__(self):
        actions.Action.__init__(self,
                'add-compiler',
                'Add a compiler')

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. If you need to add multiple '
                     'compilers for the same function, you might index them by number, or something '
                     'like that. Specific compilers can be obtained in the `objectives.py` file by '
                     'using `compilers.get_compiler(\'<function>\'')
        parser.add_argument('command',
                help='compiler command, e.g. gcc, cl, ifort. This should be a single word without spaces')
        self._add_shared_arguments(parser)

    def _add_shared_arguments(self, parser):
        parser.add_argument('--include-path', '-I',
                type=str,
                default=[],
                nargs='*',
                help='include paths')
        parser.add_argument('--library-path', '-L',
                type=str,
                default=[],
                nargs='*',
                help='library paths')
        parser.add_argument('--options',
                default=[],
                nargs='*',
                help='compiler options. This one is farily annoying. In order to provide arguments that '
                    'start with a `-`. plcae an escaped space before the argument. For example, in *nix '
                    'systems, `\\ -O2`. On windows this would translate to, `^ -O2`.')

    def invoke(self, args):
        global instances
        if args.function in instances:
            logger.error('Cannot add a compiler with the function `{}` because one already exists.\n'
                    'Maybe you meant to use `modify-compiler`?',
                    args.function)
        compiler = Compiler(args.function, args.command)
        self._apply_options(compiler, args)
        config.save()

    def _apply_options(self, compiler, args):
        if args.include_path:
            compiler.include_path = args.include_path
        if args.library_path:
            compiler.library_path = args.library_path
        if args.options:
            compiler.options = [co.strip() for co in args.options]


class Modify(Add):

    def __init__(self):
        Add.__init__(self)
        self.name = 'modify-compiler'
        self.description = 'Modify a compiler'

    def add_arguments(self, parser):
        self._add_shared_arguments(parser)
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. The function needs to be the same as '
                     'whatever was used to add the compiler.')
        parser.add_argument('--command',
                default=None,
                help='compiler command, such as `gcc`, `cl`, `ifort`, etc.')

    def invoke(self, args):
        global instances
        try:
            compiler = instances[args.function]
        except KeyError:
            logger.error('Cannot find a compiler by the function `{}`\n'
                'The available compilers are:\n  {}\n'
                'Maybe you entered a compiler command instead of a function.\n{}',
                function, '\n  '.join(str(compiler) for compiler in instances.values()), Add.help)
        self._apply_options(compiler, args)
        config.save()


class Remove(actions.Action):

    def __init__(self):
        actions.Action.__init__(self,
                'remove-compiler',
                'Remove a compiler')

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. The function needs to be the same as '
                     'whatever was used to add the compiler.')


def save(stream):
    '''Save the compilers info into a YAML stream'''
    global instances
    # Convert everything into a dictionay so that it is not saved as weird YAML/python objects
    data = dict()
    for compiler in instances.values():
        data[compiler.function] = compiler.__dict__

    # add one more layer, so it can be easily loaded
    data = {'compilers': data}
    stream.write(yaml.dump(data, default_flow_style=False))


def load(config_dict):
    '''Loads the compilers from a dict, which was read from a YAML stream.
    
    This is the reverse of the dump method.
    '''
    global instances
    if 'compilers' not in config_dict:
        logger.warning('No compilers defined in configuration.\n{}', Add.help)
        return
    comps = config_dict['compilers']
    for comp_name, comp_params in comps.items():
        compiler = Compiler(comp_params['function'], comp_params['command'])
        compiler.__dict__.update(comp_params)


class Compiler(object):

    def __init__(self, function, command):
        self.function = function
        self.command = command
        self.options = []
        self.include_path = []
        self.library_path = []
        global instances
        instances[function] = self

    def __repr__(self):
        return '<Compiler function=`{}` command=`{}`>'.format(self.function, self.command)

    def compile(self, objective):
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
            for ip in self.include_path:
                full_cmd.append('-I{}'.format(ip))
            for lp in self.library_path:
                full_cmd.append('-L{}'.format(lp))

            for item in objective.flattened_dependencies():
                if item.needs_updating:
                    output_dir = os.path.dirname(item.output)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    specific_command = full_cmd + item.compile_args
                    # if isinstance(item, objectives.Object):
                    #     specific_command = full_cmd + item.compile_args
                    # else:
                    #     specific_command = [self.command] + item.compile_args
                    print('{}'.format(' '.join(specific_command)))
                    subprocess.check_call(specific_command)


class DebugCompiler(Compiler):
    
    options = config.ConfigItem('--compiler-debug-options', [], 'compiler options for debug mode')


