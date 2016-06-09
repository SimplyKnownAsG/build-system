from __future__ import absolute_import

import inspect
import os
import shutil

import bs
from bs import config
from bs import logger


class Action(object):

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def add_arguments(self, parser):
        pass

    def invoke(self, args):
        raise NotImplementedError


class Demo(Action):

    def __init__(self):
        Action.__init__(self,
                'demo',
                'Copy the demos into the current directory')

    def invoke(self, args):
        demo_root = os.path.join(os.path.dirname(__file__), 'demos')
        # shutil.copytree(demo_root, '.')
        for base, dirs, files in os.walk(demo_root):
            for ff in files:
                src = os.path.join(base, ff)
                dest = os.path.join(base.replace(demo_root, '.'), ff)
                if not os.path.exists(os.path.dirname(dest)):
                    os.makedirs(os.path.dirname(dest))
                logger.info('  copy {} -> {}'.format(src, dest))
                shutil.copy(src, dest)



class Config(Action):

    def __init__(self):
        Action.__init__(self,
                'config',
                'Edit or intiialize the local configration')

    def add_arguments(self, parser):
        parser.add_argument('--list', '-l',
                help='list the current configuration and exit',
                action='store_true')
        config.add_command_line_args(parser)

    def invoke(self, args):
        if args.list:
            config.logger.info_config()
            exit(0)
        config.save()


class AddObjective(Action):

    def __init__(self):
        Action.__init__(self,
                'add',
                'add an objective, really just adds some scaffolding; '
                'you will probably need to update the objectives file')
        self.objectives = {m[0].lower():m[1] for m in inspect.getmembers(bs, inspect.isclass)
                if not m[0].startswith('_')}

    def add_arguments(self, parser):
        parser.add_argument('objective_type',
                help='type of the objective',
                type=str,
                choices=list(self.objectives.keys()))
        parser.add_argument('name',
                help='name of the objective',
                type=str)
        parser.add_argument('sources',
                nargs='+',
                type=str,
                help='sources for the objective')


    def invoke(self, args):
        o = self.objectives[args.objective_type](args.name, args.sources)
        targets.save()


class Build(Action):

    def __init__(self):
        Action.__init__(self,
                'build',
                'build whatever build-system knows about')

    def add_arguments(self, parser):
        parser.add_argument('--flatten', '-F',
                help='Also list flattened objectives (ignores the absence of --all)',
                action='store_true')
        parser.add_argument('--list', '-l',
                help='list known objectives, excluding object files, and exit',
                action='store_true')
        parser.add_argument('--graph', '-g',
                help='graph known objectives, excluding object files, and exit',
                action='store_true')
        parser.add_argument('--all', '-a',
                help='modifies the behavior of list and graph to include all objectives',
                action='store_true')
        parser.add_argument('--debug', '-d',
                help='use the debug compiler (and configuration)',
                action='store_true')

    def invoke(self, args):
        # import here to prevent recursive import error
        from bs import compilers_and_linkers
        compilers_and_linkers.LIST = args.list
        compilers_and_linkers.GRAPH = args.graph
        compilers_and_linkers.LIST_ALL = args.all
        compilers_and_linkers.FLATTEN = args.flatten
        exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


class Clean(Action):

    def __init__(self):
        Action.__init__(self,
                'clean',
                'clean all generated files')

    def add_arguments(self, parser):
        pass

    def invoke(self, args):
        # import here to prevent recursive import error
        from bs import compilers_and_linkers
        compilers_and_linkers.CLEAN = True
        exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


