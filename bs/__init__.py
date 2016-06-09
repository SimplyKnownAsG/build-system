
TARGETS_FILE = 'objectives.py'
LIST = False
BUILD = False
CLEAN = False

from bs.utils import *
from bs.targets import *
        

def find_root():
    import glob
    import os
    root = os.path.abspath(os.getcwd())
    while root != '':
        root
        if any(glob.glob(os.path.join(root, 'objectives.py'))):
            return root
        root = os.path.dirname(root)


def cd_root():
    from bs import logger
    root = find_root()
    if not root:
        logger.error('could not find `objectives.py` in tree')
    logger.info('found root dir {}', root)
    os.chdir(root)

