
import os
import subprocess

from . import config
from . import objectives


LIST = False
LIST_ALL = False
FLATTEN = False
GRAPH = False
DEBUG = False
CLEAN = False

def get_compiler():
    if DEBUG:
        return DebugCompiler()
    else:
        return Compiler()


class Compiler(object):

    cmd = config.ConfigItem('--compiler-cmd', None, 'compiler commane, such as `gcc`, `cl`, `ifort`, etc.')

    inc_path = config.ConfigItem('--include-path', [], 'include paths')

    lib_path = config.ConfigItem('--library-path', [], 'library paths')

    options = config.ConfigItem('--compiler-options', [], 'compiler options for "release" mode')

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
            full_cmd = [self.cmd.value] + self.options.value
            for ip in self.inc_path.value:
                full_cmd.append('-I{}'.format(ip))
            for lp in self.lib_path.value:
                full_cmd.append('-L{}'.format(lp))

            for item in objective.flattened_dependencies():
                if item.needs_updating:
                    output_dir = os.path.dirname(item.output)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    specific_command = full_cmd + item.compile_args
                    print('{}'.format(' '.join(specific_command)))
                    subprocess.check_call(full_cmd + item.compile_args)



class DebugCompiler(Compiler):
    
    options = config.ConfigItem('--compiler-debug-options', [], 'compiler options for debug mode')


