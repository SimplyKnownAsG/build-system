import os
import glob

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

