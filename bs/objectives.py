
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

    def __init__(self, name, *dependencies):
        self.name = name
        self.output = None
        list.__init__(self)
        # if isinstance(dependencies, basestring):
        #     self.append(dependencies)
        # else:
        for dep in dependencies:
            if isinstance(dep, basestring):
                self.append(Object(dep))
            elif isinstance(dep, list) and not isinstance(dep, _Objective): # an objective is a list...
                raise Exception('Cannot initialize an objective with list object,\n'
                        'maybe you forgot to use * to convert a list to *args?')
            else:
                self.append(dep)
        global instances
        instances.append(self)

    def __repr__(self):
        return '<{} {} -- {}{}>'.format(self.__class__.__name__,
                self.name,
                self.output,
                ' (out of date)' if self.needs_updating else '')

    @property
    def mtime(self):
        try:
            return os.path.getmtime(self.output)
        except:
            # the file does not exist (yet?)
            return -1

    @property
    def needs_updating(self):
        my_mod_time = self.mtime
        return any(my_mod_time <= dep.mtime for dep in self)

    def make(self):
        raise NotImplementedError

    def save(self, stream):
        stream.write("{0} = {1}('{0}',\n".format(self.name, self.__class__.__name__))
        indent = ' ' * (3 + len(self.name) + len(self.__class__.__name__))
        for dep in self:
            stream.write("{} '{}',\n".format(indent, dep))
        stream.write("{})\n\n".format(indent))

    def flattened_dependencies(self):
        '''This flattens until it reaches a library; theoretically a library would already be built'''
        flat = []
        for dep in self:
            if isinstance(dep, _Library):
                # _Library dependencies are built into the library, so they wouldn't need to be built again
                continue
            flat.extend(dep.flattened_dependencies())
        flat.append(self)
        return flat

    @property
    def compile_args(self):
        raise NotImplementedError


class Source(_Objective):
    
    def __init__(self, source):
        _Objective.__init__(self, source)
        self.output = source


class _CompiledMixin(object):

    def __init__(self):
        self.links = []

    def link_shared(self, libname):
        # self.links.extend(['-shared', '-l' + libname])
        self.links.append('-l' + libname)

    def link_static(self, libname):
        self.links.extend(['-static', '-l' + libname])
        # self.links.append('-l' + libname + StaticLibrary.EXT.value)


class Object(_Objective, _CompiledMixin):


    DIR = config.ConfigItem('--object-dir', './obj/', 'directory to generate object files')

    EXT = config.ConfigItem('--object-ext', '.obj', 'object file extension')

    def __init__(self, source):
        _Objective.__init__(self, os.path.basename(source))
        _CompiledMixin.__init__(self)
        self.append(Source(source))
        self.output = os.path.join(self.DIR.value, source + self.EXT.value)

    @property
    def compile_args(self):
        return ['-c', self[0].name] + self.links + ['-o', self.output]


class _Library(_Objective, _CompiledMixin):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')
    
    def __init__(self, name, *dependencies):
        _Objective.__init__(self, name, *dependencies)
        _CompiledMixin.__init__(self)
        self.output = os.path.join(self.DIR.value, self.name + self.EXT.value)


class SharedLibrary(_Library):

    EXT = config.ConfigItem('--shared-library-ext', '.so', 'shared object extension')

    @property
    def compile_args(self):
        args = []
        for dep in self:
            args.append(dep.output)
        args += self.links
        return args + ['-shared', '-o', self.output]


class StaticLibrary(_Library):

    EXT = config.ConfigItem('--static-library-ext', '.a', 'static library extension')


class Executable(_Library):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')

    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

    @property
    def compile_args(self):
        args = ['-static']
        for dep in self:
            args.append(dep.output)
        args += self.links
        return args + ['-o', self.output]

