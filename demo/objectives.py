
# import compilers and objectives
from bs import compilers, objectives

# the objective here is to create an executable
hello = objectives.Executable('hello_world',
        'hello_world.c')

# select the compiler we'd like to use
c_compiler = compilers.get_compiler('c')

# compile the objective using said compiler
c_compiler.compile(hello)

