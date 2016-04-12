
import os
import unittest

import bs

class TestSource(unittest.TestCase):

    def test_souceOutputIsSource(self):
        src = bs.Source('thing.cpp')
        self.assertEqual('thing.cpp', src.output)

    def test_nonExisttentSouceHasNegativeMtime(self):
        src = bs.Source('non-existent.cpp')
        self.assertEqual(src.mtime, -1)

    def test_needsUpdating(self):
        src = bs.Source('non-existent.cpp')
        self.assertEqual(src.mtime, -1)



