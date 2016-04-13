
import time
import os
import unittest
import glob

import bs

class TargetTestSkeleton(unittest.TestCase):
    '''class to make sure everything is tested, gets deleted later on'''
    def tearDown(self):
        for fname in glob.glob('temp*'):
            os.remove(fname)

    def test_name(self):
        raise NotImplementedError('must be overridden')
    
    def test_path(self):
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

    def test_name(self):
        self.assertEqual('temp-thing.cpp', self.target.name)

    def test_path(self):
        self.assertEqual('temp-thing.cpp', self.target.path)

    def test_mtime(self):
        self.assertEqual(self.target.mtime, -1)

    def test_needs_updating(self):
        self.assertFalse(self.target.needs_updating)

        bs.touch(self.target.path)
        self.assertFalse(self.target.needs_updating)
        self.assertNotEqual(self.target.mtime, -1)

    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(TypeError):
            self.target.append('hi')

    def test_iter(self):
        self.assertEqual(0, len(list(iter(self.target))))

    def test_equal(self):
        src2 = bs.Source(self.target.path)
        self.assertEqual(src2, self.target)
        self.assertNotEqual(id(src2), id(self.target))

    def test_find_c_dependencies(self):
        bs.touch('temp-existing.h')
        bs.touch('temp-existing-fake.h')
        with open(self.target.path, 'w') as ff:
            ff.write('#include "temp-existing.h"\n')
            ff.write('// #include "temp-existing-fake.h"\n')
            ff.write('#include "missing.h"\n')
            ff.write('#include <iostream>\n')
        self.assertFalse(self.target.needs_updating)
        self.target.find_dependencies()
        self.assertEqual(1, len(self.target))
        self.assertEqual('temp-existing.h', self.target[0].path)
        self.assertTrue(self.target.needs_updating)

    def test_find_fortran_dependencies(self):
        target = bs.Source('temp_thing.f')
        bs.touch('temp_existing.f')
        bs.touch('temp_existing90.f90')
        bs.touch('temp_existing_fake.h')
        with open(target.path, 'w') as ff:
            ff.write('  use temp_existing\n')
            ff.write('  use temp_existing90\n')
            ff.write('! use temp_existing_fake\n')
        self.assertFalse(target.needs_updating)
        target.find_dependencies()
        self.assertEqual(2, len(target))
        self.assertEqual('temp_existing.f', target[0].path)
        self.assertEqual('temp_existing90.f90', target[1].path)
        self.assertTrue(target.needs_updating)


class TargetTests(unittest.TestCase):

    def test_accessibleObjects(self):
        '''ensure protected members are not accessible'''
        from bs import targets
        for name in dir(targets):
            if name.startswith('_') and not name.endswith('__'):
                self.assertNotIn(name, dir(bs))


class ObjectTests(TargetTestSkeleton):

    def setUp(self):
        self.target_c = bs.Object(bs.Source('./src/temp-source.c'))
        self.target_f = bs.Object(bs.Source('./src/temp-source.f'))

    def tearDown(self):
        bs.clean('temp-*')
        for target in [self.target_c, self.target_f]:
            bs.clean(target.path)
            for source in target:
                bs.clean(source.path)

    def help_name_path(self, func):
        self.assertEqual('./obj/', bs.Object.DIR.value)
        self.assertEqual('.obj', bs.Object.EXT.value)
        self.assertEqual('./obj/./src/temp-source.c.obj', func(self.target_c))
        self.assertEqual('./obj/./src/temp-source.f.obj', func(self.target_f))
        
        bs.Object.DIR.value = './objects/'
        bs.Object.EXT.value = '.o'
        self.assertEqual('./objects/./src/temp-source.c.o', func(self.target_c))
        self.assertEqual('./objects/./src/temp-source.f.o', func(self.target_f))

        bs.Object.DIR.value = './obj/'
        bs.Object.EXT.value = '.obj'

    def test_name(self):
        self.help_name_path(lambda obj: obj.name)

    def test_path(self):
        self.help_name_path(lambda obj: obj.path)

    def test_mtime(self):
        self.assertEqual(self.target_c.mtime, -1)
        self.assertEqual(self.target_f.mtime, -1)

        bs.touch(self.target_c.path)
        bs.touch(self.target_f.path)

        self.assertGreater(self.target_c.mtime, -1)
        self.assertGreater(self.target_f.mtime, -1)

    def test_needs_updating(self):
        '''A non-existent Object file always needs to be update'''
        self.assertFalse(os.path.exists(self.target_c.path))
        self.assertTrue(self.target_c.needs_updating)

        bs.touch(self.target_c.path)
        self.assertFalse(self.target_c.needs_updating)
        self.assertNotEqual(self.target_c.mtime, -1)

    def test_needs_updating_due_to_source(self):
        '''An object file needs to be updated if its sources are newer'''
        bs.touch(self.target_c.path)
        self.assertFalse(self.target_c.needs_updating)
        bs.touch(self.target_c[0].path) # source is newer
        self.assertTrue(self.target_c.needs_updating)

        bs.touch(self.target_c.path) # touch it...
        while self.target_c[0].mtime >= self.target_c.mtime:
            bs.touch(self.target_c.path) # touch it...
        self.assertFalse(self.target_c.needs_updating)

    def test_append(self):
        with self.assertRaises(TypeError):
            self.target_c.append('hi')
        self.target_c.append(bs.Source('some-header.h'))

    def test_iter(self):
        self.target_c.append(bs.Source('some-header1.h'))
        self.target_c.append(bs.Source('some-header2.h'))
        self.target_c.append(bs.Source('some-header3.h'))
        self.assertEqual(4, len(list(iter(self.target_c))))

    def test_equal(self):
        src2 = bs.Object(bs.Source(self.target_c[0].path))
        self.assertEqual(src2, self.target_c)
        self.assertNotEqual(id(src2), id(self.target_c))


class SwigSourceTests(TargetTestSkeleton):

    def setUp(self):
        bs.touch('temppork.h')
        with open('tempbacon.i', 'w') as ff:
            ff.write('%include "temppork.h"')
        self.target = bs.SwigSource('tempbacon.i')

    def test_name(self):
        self.assertEqual('tempbacon', self.target.name)

    def test_path(self):
        self.assertEqual('tempbacon_wrap.c', self.target.path)
        self.assertEqual('tempbacon_wrap.h', self.target.header)
        self.target.cpp = True
        self.assertEqual('tempbacon_wrap.cxx', self.target.path)
        self.assertEqual('tempbacon_wrap.hxx', self.target.header)

    def test_mtime(self):
        self.assertEqual(self.target.mtime, -1)
        bs.touch(self.target.path)
        self.assertEqual(self.target.mtime, -1)
        bs.touch(self.target.header)
        self.assertGreater(self.target.mtime, 0)

    def test_needs_updating(self):
        self.assertTrue(self.target.needs_updating)

        bs.touch(self.target.path)
        while self.target[0].mtime >= self.target.mtime:
            bs.touch(self.target.path)
            bs.touch(self.target.header)

        self.assertFalse(self.target.needs_updating)

        bs.clean(self.target.header) # if either file is deleted, we need to update
        self.assertTrue(self.target.needs_updating)

    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(TypeError):
            self.target.append('hi')
        self.target.append(bs.Source('s'))

    def test_iter(self):
        self.assertEqual('tempbacon.i', self.target[0].path)
        self.assertEqual('temppork.h', self.target[1].path)

    def test_equal(self):
        src2 = bs.SwigSource(self.target[0].path)
        self.assertEqual(src2, self.target)
        self.assertNotEqual(id(src2), id(self.target))


class LinkedObjectTests(TargetTestSkeleton):

    def setUp(self):
        self.so = bs.SharedLibrary('temphello', 'tempmain.c', bs.Source('temphello.c'))
        self.a = bs.StaticLibrary('temphello', 'tempmain.c', bs.Source('temphello.c'))

    def test_name(self):
        self.assertEqual('temphello', self.so.name)
        self.assertEqual('temphello', self.a.name)

    def test_path(self):
        self.assertEqual('./bin/temphello.so', self.so.path)
        self.assertEqual('./bin/temphello.a', self.a.path)

    def test_mtime(self):
        self.assertEqual(self.so.mtime, -1)
        self.assertEqual(self.a.mtime, -1)

    def test_needs_updating(self):
        self.assertTrue(self.so.needs_updating)
        self.assertTrue(self.a.needs_updating)

    def test_append(self):
        '''Source.append fails'''
        with self.assertRaises(TypeError):
            self.so.append('hi')
        self.a.append(bs.Source('s'))

    def test_iter(self):
        for target in [self.so, self.a]:
            self.assertEqual('tempmain.c', target[0].path)
            self.assertEqual('temphello.c', target[1].path)

    def test_equal(self):
        self.assertEqual(self.so.name, self.a.name)
        self.assertNotEqual(self.so, self.a)


del TargetTestSkeleton

if __name__ == '__main__':
    unittest.main()

