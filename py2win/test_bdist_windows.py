#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import sys
import subprocess

# Third party modules.

# Local modules.

# Globals and constants variables.

class Testbdist_windows(unittest.TestCase):

    def setUp(self):
        super().setUp()

        basedir = os.path.dirname(__file__)
        self.sampleproject_dirpath = os.path.join(basedir, 'testdata', 'sampleproject')

    def testbdist_windows(self):
        args = [sys.executable, 'setup.py', '--command-packages', 'py2win', 'bdist_windows']
        subprocess.run(args, cwd=self.sampleproject_dirpath, check=True)

        distdir = os.path.join(self.sampleproject_dirpath, 'dist', 'sample-1.2.0')
        self.assertTrue(os.path.exists(os.path.join(distdir, 'sample-console.exe')))
        self.assertTrue(os.path.exists(os.path.join(distdir, 'sample-gui.exe')))

        args = [os.path.join(distdir, 'sample-console.exe')]
        out = subprocess.run(args, cwd=distdir, check=True, stdout=subprocess.PIPE)
        self.assertEqual(b'Hello world', out.stdout.strip())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
