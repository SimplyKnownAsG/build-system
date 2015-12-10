
import os
import glob
import subprocess

from . import config


class Target(list):

    def __init__(self, *depenencies):
        list.__init__(self, *dependencies)

    def time(self):
        return NotImplementedError

    def make(self):
        raise NotImplementedError


class Object(Target):

    DIR = config.ConfigItem('--object-dir', './obj/', 'directory to generate object files')
    EXT = config.ConfigItem('--object-ext', '.obj', 'object file extension')

    def __init__(self, source):
        self.source = source


class Library(Target):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')

    pass


class Executable(Target):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')
    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

    pass


class SharedLibrary(Library):

    pass


class StaticLibrary(Library):

    pass


