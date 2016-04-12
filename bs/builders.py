from __future__ import absolute_import

import os
import subprocess
import traceback

import yaml

import bs
from bs import actions
from bs import config
from bs import logger

instances = {}
'''Instances of builder objects'''


def get_builder(function):
    try:
        return instances[function]
    except KeyError:
        logger.error('Could not find a builder with the function `{}`.\n'
                'Available builders are:\n  {}\n' + Add.help,
                function, '\n  '.join(str(builder) for builder in instances.values()))


class Builder(object):

    def __init__(self, function):
        self.function = function
        self.linker = None
        self.compiler = None
        global instances
        instances[function] = self

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.function)

    def build(self, objective):

        for item in objective.flattened_dependencies():
            if isinstance(item, bs.Object):
                self.compiler.run(item)
            elif isinstance(item, bs.LinkedObject):
                self.linker.run(item)


class Add(actions.Action):

    help = 'New builders can be added using the `add-builder` command'

    def __init__(self):
        actions.Action.__init__(self, 'add-builder',
                'Add a new builder to be used in the objectives.py file as `builders.get_builder(<function-name>)`')

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the builder')

    def invoke(self, args):
        builder = Builder(args.function)
        config.save()


class Remove(actions.Action):

    def __init__(self):
        actions.Action.__init__(self, 'remove-builder',
                'Remove an existing builder by function name.')

    def add_arguments(self, parser):
        parser.add_argument('function',
                help='function of the compiler, e.g. c++, Fortran, C#. The function needs to be the same as '
                     'whatever was used to add the compiler.')


def get_actions():
    return [Add(), Remove()]


def save(stream):
    '''Save the compilers info into a YAML stream'''
    global instances
    # Convert everything into a dictionay so that it is not saved as weird YAML/python objects
    if instances:
        data = dict()
        for function, builder in instances.items():
            data[function] = subdata = dict()
            if builder.linker:
                subdata['linker.function'] = builder.linker.function
            if builder.compiler:
                subdata['compiler.function'] = builder.compiler.function
        data = { 'builders' : data }
        stream.write(yaml.dump(data, default_flow_style=False))


def load(config_dict):
    '''Loads the compilers from a dict, which was read from a YAML stream.'''
    from bs import compilers_and_linkers
    global instances
    if 'builders' not in config_dict:
        logger.warning('No builders defined in configuration.\n{}', Add.help)
    else:
        for builder_function, builder_params in config_dict['builders'].items():
            builder = Builder(builder_function)
            
            builder.compiler = compilers_and_linkers.get_compiler(builder_params.get('compiler.function',
                builder_function))
            builder.linker = compilers_and_linkers.get_linker(builder_params.get('linker.function', builder_function))



