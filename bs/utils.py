import glob
import os
import re

def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except:
        # the file does not exist (yet?)
        return -1

def copy(source, destination):
    if os.path.exists(source):
        if get_mtime(destination) < get_mtime(source):
            print('copying {} -> {}'.format(source, destination))
            shutil.copy(source, destination)


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        dirname = os.path.dirname(fname)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        open(fname, 'a').close()


def clean(fname):
    try:
        os.remove(fname)
    except:
        pass # who cares?

    # now walk the tree to see if stuff is empty...
    dirname = os.path.dirname(fname)
    while dirname:
        if not os.path.exists(dirname):
            dirname = os.path.dirname(dirname)
            continue
        elif glob.glob(os.path.join(dirname, '*')):
            break
        try:
            os.rmdir(dirname)
        except:
            break # there was a hidden file we didn't see
        dirname = os.path.dirname(dirname)


swig_inc_pat = re.compile(r'^\s*%\s*include ["<](?P<fname>.+)[">]')

c_inc_pat = re.compile(r'^\s*#\s*include ["<](?P<fname>.+)[">]')
c_ext_pat = re.compile(r'\.(c|h|cpp|hpp|cc)$', re.IGNORECASE)

fortran_inc_pat = re.compile(r'^\s*use (?P<fname>[0-9a-zA-Z_]+)')
fortran_ext_pat = re.compile(r'\.(f|for|f[0-9]{2})$', re.IGNORECASE)

def find_dependencies(source_path):
    inc_pat = None
    fname_matches = None
    if c_ext_pat.search(source_path):
        inc_pat = c_inc_pat
        fname_matches = lambda fn, lf: fn == lf
    elif fortran_ext_pat.search(source_path):
        inc_pat = fortran_inc_pat
        fname_matches = lambda fn, lf: fn == lf.split('.')[0] and fortran_ext_pat.search(lf)
    elif source_path.endswith('.i'):
        inc_pat = swig_inc_pat
        fname_matches = lambda fn, lf: fn == lf
    if inc_pat is not None and os.path.exists(source_path):
        local_files = glob.glob(os.path.join(os.path.dirname(source_path), '*'))
        with open(source_path, 'r') as ff:
            for line in ff:
                try:
                    fname = inc_pat.search(line).group('fname')
                    for local_file in local_files:
                        if fname_matches(fname, local_file):
                            yield local_file
                            break
                except AttributeError:
                    pass


