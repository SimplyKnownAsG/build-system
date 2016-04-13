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


c_inc_pat = re.compile(r'^\s*#\s*include ["<](?P<fname>.+)[">]')

def find_dependencies(source_path):
    pattern = None
    if re.search(r'\.(c|h|cpp|hpp|cc)$', source_path, re.IGNORECASE):
        pattern = c_inc_pat
    elif re.search(r'\.(f|for|f\d\d)$', source_path, re.IGNORECASE):
        pattern = f_inc_pat
    if pattern is not None and os.path.exists(source_path):
        with open(source_path, 'r') as ff:
            for line in ff:
                match = pattern.search(line)
                if match:
                    fname = match.group('fname')
                    if os.path.exists(fname):
                        yield fname


