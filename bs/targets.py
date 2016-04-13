
import os
import glob
import subprocess
import re

import bs
from bs import config
from bs import logger


instances = []


class _Target(object):

    def __init__(self):
        self._children = []
        global instances
        instances.append(self)

    @property
    def name(self):
        raise NotImplementedError('must be overridden in a subclass')

    @property
    def path(self):
        raise NotImplementedError('must be overridden in a subclass')

    def __repr__(self):
        return '<{} {} -- {}{}>'.format(self.__class__.__name__,
                self.name,
                self.path,
                ' (out of date)' if self.needs_updating else '')

    def __eq__(self, other):
        return self.name == other.name and self.path == other.path and list(self) == list(other)

    def __iter__(self):
        return iter(self._children)

    def __len__(self):
        return len(self._children)

    def __getitem__(self, index):
        return self._children[index]

    def append(self, item):
        if not isinstance(item, _Target):
            raise TypeError('Cannot add a dependency on {} because it is not a subclass of _Target'
                    .format(item))
        self._children.append(item)

    @property
    def mtime(self):
        return bs.get_mtime(self.path)

    @property
    def needs_updating(self):
        my_mtime = self.mtime
        return any(my_mtime <= dep.mtime for dep in self)

    def flattened_dependencies(self):
        '''This flattens until it reaches a library; theoretically a library would already be built'''
        flat = []
        for dep in self:
            if isinstance(dep, _LinkedObject):
                # _Library dependencies are built into the library, so they wouldn't need to be built again
                continue
            flat.extend(dep.flattened_dependencies())
        flat.append(self)
        return flat


class Source(_Target):
    
    def __init__(self, source):
        _Target.__init__(self)
        self._path = source

    @property
    def name(self):
        return self.path

    @property
    def path(self):
        return self._path

    def find_dependencies(self):
        for fname in bs.find_dependencies(self.path):
            self.append(Source(fname))


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
        if not isinstance(source, Source):
            raise Exception('Cannot create an Object with non-Souce input')
        _Target.__init__(self)
        _CompiledMixin.__init__(self)
        self.append(source)

    @property
    def path(self):
        return os.path.join(self.DIR.value, self[0].path + self.EXT.value)

    @property
    def name(self):
        return self.path


class SwigSource(Source):

    def __init__(self, interface_file):
        _Target.__init__(self)
        if interface_file[-2:] != '.i':
            logger.warning('{} should be initialized with an interface file as the first argument; expected it to end '
                'with `.i`')
        self.args = []
        self.cpp = False
        self.target_language = None
        self.append(bs.Source(interface_file))
        for dep_path in bs.find_dependencies(interface_file):
            self.append(Source(dep_path))

    @property
    def mtime(self):
        return min(bs.get_mtime(self.path), bs.get_mtime(self.header))

    @property
    def name(self):
        return os.path.splitext(self[0].path)[0]

    @property
    def path(self):
        path = self.name + '_wrap.c'
        if self.cpp:
            path += 'xx'
        return path

    @property
    def header(self):
        path = self.name + '_wrap.h'
        if self.cpp:
            path += 'xx'
        return path

    def create(self):
        from bs import compilers_and_linkers
        if compilers_and_linkers.CLEAN:
            for ff in [self.header, self.path]:
                if os.path.exists(ff):
                    print('removing {}'.format(ff))
                    os.remove(ff)
        elif self.needs_updating:
            if self.target_language is None:
                logger.error('You must specify a target language for a SwigSource\n'
                        'This can be done in the `{}` file by setting the SwigSource.target_language attribute',
                        bs.TARGETS_FILE)
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
            except subprocess.CalledProcessError:
                logger.error('subprocess call failed')


class _LinkedObject(_Target, _CompiledMixin):

    DIR = config.ConfigItem('--lib-dir', './bin/', 'directory to generate libraries')
    
    def __init__(self, name, *dependencies):
        _Target.__init__(self)
        _CompiledMixin.__init__(self)
        self._name = name
        if isinstance(dependencies, basestring):
            dependencies = [dependencies]
        elif len(dependencies) == 1 and isinstance(dependencies, (list, tuple)):
            dependencies = dependencies[0]
        for dep in dependencies:
            if isinstance(dep, _Target):
                self.append(dep)
            elif isinstance(dep, basestring):
                self.append(Source(dep))

    @property
    def path(self):
        return os.path.join(self.DIR.value, self.name + self.EXT.value)

    @property
    def name(self):
        return self._name


class SharedLibrary(_LinkedObject):

    EXT = config.ConfigItem('--shared-library-ext', '.so', 'shared object extension')


class StaticLibrary(_LinkedObject):

    EXT = config.ConfigItem('--static-library-ext', '.a', 'static library extension')


class Executable(_LinkedObject):

    DIR = config.ConfigItem('--exec-dir', './bin/', 'directory to generate libraries')

    EXT = config.ConfigItem('--exec-ext', '.exe', 'executable file extension')

