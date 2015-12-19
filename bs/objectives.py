
import os
import glob
import subprocess

from bs import config
from bs import logger


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
            if isinstance(dep, str):
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
            if isinstance(dep, LinkedObject):
                # _Library dependencies are built into the library, so they wouldn't need to be built again
                continue
            flat.extend(dep.flattened_dependencies())
        flat.append(self)
        return flat


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
        if isinstance(source, Source):
            source_path = source.output
            source_object = source
        else:
            source_path = source
            source_object = Source(source)
        _Objective.__init__(self, os.path.basename(source_path))
        _CompiledMixin.__init__(self)
        self.append(source_object)
        self.output = os.path.join(self.DIR.value, source_path + self.EXT.value)


class SwigSource(Source):

    def __init__(self, interface_file, *dependencies):
        _Objective.__init__(self, interface_file, *dependencies)
        self.interface_file = interface_file
        if interface_file[-2:] != '.i':
            logger.warning('{} should be initialized with an interface file as the first argument; expected it to end '
                'with `.i`')
        self.args = []
        self.cpp = False
        self.target_language = None

    @property
    def needs_updating(self):
        my_mod_time = self.mtime
        return any(my_mod_time <= dep[0].mtime for dep in self)

    @property
    def name(self):
        output = os.path.splitext(self.interface_file)[0] + '_wrap.c'
        if self.cpp:
            output += 'xx'
        return output

    @name.setter
    def name(self, val):
        pass

    @property
    def output(self):
        output = os.path.splitext(self.interface_file)[0] + '_wrap.c'
        if self.cpp:
            output += 'xx'
        return output

    @output.setter
    def output(self, val):
        pass

    @property
    def header(self):
        return os.path.splitext(self.interface_file)[0] + '_wrap.h'

    def create(self):
        if self.needs_updating:
            if self.target_language is None:
                logger.error('You must specify a target language for a SwigSource\n'
                        'This can be done in the `{}` file by setting the SwigSource.target_language attribute',
                        OBJECTIVES_FILE)
            cmd = ['swig', '-{}'.format(self.target_language)]
            if self.cpp:
                cmd.append('-c++')
            cmd.extend(['-o', self.name])
            cmd.extend(['-oh', self.header])
            cmd.extend(self.args)
            cmd.append(self.interface_file)
            subprocess.check_call(cmd)


class LinkedObject(_Objective, _CompiledMixin):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')
    
    def __init__(self, name, *dependencies):
        _Objective.__init__(self, name, *dependencies)
        _CompiledMixin.__init__(self)
        self.output = os.path.join(self.DIR.value, self.name + self.EXT.value)


class SharedLibrary(LinkedObject):

    EXT = config.ConfigItem('--shared-library-ext', '.so', 'shared object extension')


class StaticLibrary(LinkedObject):

    EXT = config.ConfigItem('--static-library-ext', '.a', 'static library extension')


class Executable(LinkedObject):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')

    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

