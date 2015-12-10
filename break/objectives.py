
import os
import glob
import subprocess

from . import config


instances = []

OBJECTIVES_FILE = 'objectives.py'

def save():
    with open(OBJECTIVES_FILE, 'a') as o_stream:
        instances[0].save(o_stream)

class _Objective(list):

    def __init__(self, *dependencies):
        list.__init__(self)
        self.extend(*dependencies)
        global instances
        instances.append(self)

    def mtime(self):
        return NotImplementedError

    def make(self):
        raise NotImplementedError

    def save(self, stream):
        stream.write("{0} = {1}('{0}',\n".format(self.name, self.__class__.__name__))
        indent = ' ' * (3 + len(self.name) + len(self.__class__.__name__))
        for dep in self:
            stream.write("{} '{}',\n".format(indent, dep))
        stream.write("{})\n\n".format(indent))


class Object(_Objective):

    DIR = config.ConfigItem('--object-dir', './obj/', 'directory to generate object files')
    EXT = config.ConfigItem('--object-ext', '.obj', 'object file extension')

    def __init__(self, source):
        self.source = source


class _Library(_Objective):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')
    
    def __init__(self, name, *dependencies):
        self.name = name
        _Objective.__init__(self, *dependencies)


class Executable(_Library):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')
    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

    pass


class SharedLibrary(_Library):

    pass


class StaticLibrary(_Library):

    pass


