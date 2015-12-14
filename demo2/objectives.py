
# import compilers and objectives
from bs import compilers, objectives

f_compiler = compilers.get_compiler('f90')
fortran_hello = objectives.Object('hello_world.f90')
f_compiler.compile(fortran_hello)

# the objective here is to create an executable
hello = objectives.Executable('hello_world',
        fortran_hello,
        'hello_world.c')
# so... this needs to be fixed. this is now system dependent!!!
hello.link_shared('gfortran')

# select the compiler we'd like to use
c_compiler = compilers.get_compiler('c')

# compile the objective using said compiler
c_compiler.compile(hello)

