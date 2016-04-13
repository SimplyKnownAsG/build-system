
import os
import unittest
import glob

import bs


class UtilTests(unittest.TestCase):

    def tearDown(self):
        for fname in glob.glob('temp-*'):
            os.remove(fname)

    def test_touchCreatesFile(self):
        fname = 'temp-turtles-are-awesome'
        self.assertFalse(os.path.exists(fname))
        bs.touch(fname)
        self.assertTrue(os.path.exists(fname))

    def test_touchCreatesFolders_cleanDeletesRecursively(self):
        fname = 'path/to/temp-file'
        bs.clean(fname)
        self.assertFalse(os.path.exists('path'))
        self.assertFalse(os.path.exists('path/to'))
        self.assertFalse(os.path.exists(fname))
        bs.touch(fname)
        self.assertTrue(os.path.exists(fname))

        bs.clean(fname)
        self.assertFalse(os.path.exists('path'))

    def test_cleanLeavesFoldersWithHiddenFiles(self):
        self.assertFalse(os.path.exists('.dirname'))
        bs.touch('.dirname/.hidden')
        bs.touch('.dirname/visible')
        self.assertTrue(os.path.exists('.dirname'))
        bs.clean('.dirname/visible')
        self.assertTrue(os.path.exists('.dirname')) # kept becuase there was a file
        bs.clean('.dirname/.hidden')
        self.assertFalse(os.path.exists('.dirname'))

    def test_copy_cleans_when_cleaning(self):
        self.assertFalse(bs.CLEAN)
        bs.touch('somewhere/out_there')
        self.assertTrue(os.path.exists('somewhere/out_there'))
        self.assertFalse(os.path.exists('somewhere/out_there.copy'))

        bs.copy('somewhere/out_there', 'somewhere/out_there.copy')
        self.assertTrue(os.path.exists('somewhere/out_there.copy'))
        bs.CLEAN = True
        bs.copy('somewhere/out_there', 'somewhere/out_there.copy')
        self.assertFalse(os.path.exists('somewhere/out_there.copy'))
        bs.CLEAN = False
        bs.clean('somewhere/out_there')


