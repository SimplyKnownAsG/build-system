
import os
import unittest
import glob

import bs

class TargetTestSkeleton(unittest.TestCase):
    '''class to make sure everything is tested, gets deleted later on'''
    def tearDown(self):
        for fname in glob.glob('temp-*'):
            os.remove(fname)
    
    def test_output(self):
        raise NotImplementedError('must be overridden')

    def test_mtime(self):
        raise NotImplementedError('must be overridden')

    def test_needs_updating(self):
        raise NotImplementedError('must be overridden')

    def test_append(self):
        raise NotImplementedError('must be overridden')

    def test_iter(self):
        raise NotImplementedError('must be overridden')

    def test_equal(self):
        raise NotImplementedError('must be overridden')


class TestSource(TargetTestSkeleton):

    def setUp(self):
        self.target = bs.Source('temp-thing.cpp')

    def test_output(self):
        self.assertEqual('temp-thing.cpp', self.target.output)

    def test_mtime(self):
        self.assertEqual(self.target.mtime, -1)

    def test_needs_updating(self):
        self.assertFalse(self.target.needs_updating)

        bs.touch(self.target.output)
        self.assertFalse(self.target.needs_updating)
        self.assertNotEqual(self.target.mtime, -1)

    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(NotImplementedError):
            self.target.append('hi')

    def test_iter(self):
        self.assertEqual(0, len(list(iter(self.target))))

    def test_equal(self):
        src2 = bs.Source(self.target.output)
        self.assertEqual(src2, self.target)
        self.assertNotEqual(id(src2), id(self.target))


class TargetTests(unittest.TestCase):

    def test_accessibleObjects(self):
        '''ensure protected members are not accessible'''
        from bs import targets
        for name in dir(targets):
            if name.startswith('_') and not name.endswith('__'):
                self.assertNotIn(name, dir(bs))


class ObjectTests(TargetTestSkeleton):

    def setUp(self):
        self.target_c = bs.Object(bs.Source('source.c')) # target from source
        self.target_f = bs.Object('source.f') # target from string

    def test_output(self):
        self.assertEqual('./obj/', bs.Object.DIR.value)
        self.assertEqual('.obj', bs.Object.EXT.value)
        self.assertEqual('./obj/source.c.obj', self.target_c.output)
        self.assertEqual('./obj/source.f.obj', self.target_f.output)
        
        bs.Object.DIR.value = './objects/'
        bs.Object.EXT.value = '.o'
        self.assertEqual('./objects/source.c.o', self.target_c.output)
        self.assertEqual('./objects/source.f.o', self.target_f.output)

    @unittest.skip('waiting...')
    def test_mtime(self):
        self.assertEqual(self.target.mtime, -1)

    @unittest.skip('waiting...')
    def test_needs_updating(self):
        self.assertFalse(self.target.needs_updating)

        bs.touch(self.target.output)
        self.assertFalse(self.target.needs_updating)
        self.assertNotEqual(self.target.mtime, -1)

    @unittest.skip('waiting...')
    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(NotImplementedError):
            self.target.append('hi')

    @unittest.skip('waiting...')
    def test_iter(self):
        self.assertEqual(0, len(list(iter(self.target))))

    @unittest.skip('waiting...')
    def test_equal(self):
        src2 = bs.Source(self.target.output)
        self.assertEqual(src2, self.target)
        self.assertNotEqual(id(src2), id(self.target))


@unittest.skip('needs Object')
class SwigSourceTests(TargetTestSkeleton):

    def setUp(self):
        self.target = bs.SwigSource('bacon.i')

    def test_output(self):
        self.assertEqual('temp-thing.cpp', self.target.output)

    def test_mtime(self):
        self.assertEqual(self.target.mtime, -1)

    def test_needs_updating(self):
        self.assertFalse(self.target.needs_updating)

        bs.touch(self.target.output)
        self.assertFalse(self.target.needs_updating)
        self.assertNotEqual(self.target.mtime, -1)

    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(NotImplementedError):
            self.target.append('hi')

    def test_iter(self):
        self.assertEqual(0, len(list(iter(self.target))))

    def test_equal(self):
        src2 = bs.Source(self.target.output)
        self.assertEqual(src2, self.target)
        self.assertNotEqual(id(src2), id(self.target))



del TargetTestSkeleton

if __name__ == '__main__':
    unittest.main()

