
import os
import glob
import subprocess

import bs
from bs import config
from bs import logger


instances = []


class _Target(object):

    def __init__(self, name, *dependencies):
        self.name = name
        self._output = None
        self._children = []
        # if isinstance(dependencies, basestring):
        #     self.append(dependencies)
        # else:
        for dep in dependencies:
            if isinstance(dep, str):
                self.append(Object(dep))
            elif isinstance(dep, list) and not isinstance(dep, _Target): # an objective is a list...
                raise Exception('Cannot initialize an objective with list object,\n'
                        'maybe you forgot to use * to convert a list to *args?')
            else:
                self.append(dep)
        global instances
        instances.append(self)

    @property
    def output(self):
        return self._output

    def __repr__(self):
        return '<{} {} -- {}{}>'.format(self.__class__.__name__,
                self.name,
                self.output,
                ' (out of date)' if self.needs_updating else '')

    def __eq__(self, other):
        return self.name == other.name and self.output == other.output and list(self) == list(other)

    def __iter__(self):
        return iter(self._children)

    def append(self, item):
        if not isinstance(item, _Target):
            raise NotImplementedError('Cannot add a dependency on {} because it is not a subclass of _Target'
                    .format(item))
        self._children.append(item)

    @property
    def mtime(self):
        return bs.get_mtime(self.output)

    @property
    def needs_updating(self):
        my_mtime = self.mtime
        return any(my_mtime <= dep.mtime for dep in self)

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


class Source(_Target):
    
    def __init__(self, source):
        _Target.__init__(self, source)
        self._output = source


class _CompiledMixin(object):

    def __init__(self):
        self.links = []

    def link_shared(self, libname):
        # self.links.extend(['-shared', '-l' + libname])
        self.links.append('-l' + libname)

    def link_static(self, libname):
        self.links.extend(['-static', '-l' + libname])
        # self.links.append('-l' + libname + StaticLibrary.EXT.value)


class Object(_Target, _CompiledMixin):


    DIR = config.ConfigItem('--object-dir', './obj/', 'directory to generate object files')

    EXT = config.ConfigItem('--object-ext', '.obj', 'object file extension')

    def __init__(self, source):
        if isinstance(source, Source):
            source_path = source.output
            source_object = source
        else:
            source_path = source
            source_object = Source(source)
        _Target.__init__(self, os.path.basename(source_path))
        _CompiledMixin.__init__(self)
        self.append(source_object)
        self._output = source_object.output

    @property
    def output(self):
        return os.path.join(self.DIR.value, self._output + self.EXT.value)


class SwigSource(Source):

    def __init__(self, interface_file, *dependencies):
        _Target.__init__(self, interface_file, *dependencies)
        self.interface_file = interface_file
        if interface_file[-2:] != '.i':
            logger.warning('{} should be initialized with an interface file as the first argument; expected it to end '
                'with `.i`')
        self.args = []
        self.cpp = False
        self.target_language = None

    @property
    def needs_updating(self):
        my_mtime = self.mtime
        # the dependencies of a SWIG source, are the sources of the object files. Since
        # the dependencies are converted to Object(s), we need to grab their 1st dependency
        # which is the actual source file.
        result = any(my_mtime <= dep[0].mtime for dep in self)
        # also need to consider the interface file
        result |= my_mtime <= os.path.getmtime(self.interface_file)
        # yes, I realize this could have been done in one line
        return result

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
        from bs import compilers_and_linkers
        if compilers_and_linkers.CLEAN:
            for ff in [self.header, self.output]:
                if os.path.exists(ff):
                    print('removing {}'.format(ff))
                    os.remove(ff)
        elif self.needs_updating:
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
            print(' '.join(cmd))
            try:
                subprocess.check_call(cmd)
            except CalledProcessError:
                logger.error('subprocess call failed')

    def flattened_dependencies(self):
        return [self]


class LinkedObject(_Target, _CompiledMixin):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')
    
    def __init__(self, name, *dependencies):
        _Target.__init__(self, name, *dependencies)
        _CompiledMixin.__init__(self)
        self.output = os.path.join(self.DIR.value, self.name + self.EXT.value)


class SharedLibrary(LinkedObject):

    EXT = config.ConfigItem('--shared-library-ext', '.so', 'shared object extension')


class StaticLibrary(LinkedObject):

    EXT = config.ConfigItem('--static-library-ext', '.a', 'static library extension')


class Executable(LinkedObject):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')

    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

