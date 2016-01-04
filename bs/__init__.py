
import os
import shutil

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
        


