# Welcome to the demo!

This is the obligatory Hello World! example.

When starting the demo, the folder should contain

```
hello_world.c
objectives.py
```

and that is it.

# BS files
BS uses two files for determining how to build your project.

This will provide little information about those files.

## `objectives.py`
The first file is `objectives.py`. BS uses the term objectives in place of targets.

`objectives.py` contains Python code, **is system (OS) independent**, and describes what you want BS to do.

This is (or should be) the same as the `objectives.py` in this example. 

```python
# import compilers and objectives
from bs import compilers, objectives

# the objective here is to create an executable
hello = objectives.Executable('hello_world',
        'hello_world.c')

# select the compiler we'd like to use
c_compiler = compilers.get_compiler('c')

# compile the objective using said compiler
c_compiler.compile(hello)
```

## `.build-system.yaml`
The second file is `.build-system.yaml`.

`.build-system.yaml` contains settings, information about compilers, and **is system (OS) dependent**.

This is (or should be) the same as the `.build-system.yaml` in this example. It uses `gcc`, but that is only because I
operate under the assumption that most people have `gcc` available at least with Cygwin or MinGW.

```yaml
# build-system generated configuration file
# feel free to update values here, it could be fun!
# if things break, then you are doing great!
compilers:
  c:
    command: gcc
    function: c
    include_path: []
    library_path: []
    options:
    - -O2
```

The `.build-system.yaml` file shows that there is a compiler with the function "c" (i.e. it is compiler for C code), and
that the command for this compiler is gcc.

# Using BS
So, let's try running the example.

You'll need to open your terminal and navigate to the demo folder.

I use aliases for everything (`export bs=python -m bs`, or `doskey bs=python -m bs $*`).

`build-system\demo $ bs build`

should output:

```
gcc -O2 -c hello_world.c -o ./obj/hello_world.c.obj
gcc -O2 -static ./obj/hello_world.c.obj -o ./bin/hello_world.exe
```

