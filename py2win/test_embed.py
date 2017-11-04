#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil
import subprocess
import sys

# Third party modules.

# Local modules.
from py2win.embed import EmbedPython

# Globals and constants variables.

class TestEmbedPython(unittest.TestCase):

    def setUp(self):
        super().setUp()

        basedir = os.path.dirname(__file__)
        self.sampleproject_dirpath = os.path.join(basedir, 'testdata', 'sampleproject')

        self.tmpdir = tempfile.mkdtemp()

        self.embed = EmbedPython('sample', '1.2.0')

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testrun(self):
        # Create wheel
        args = [sys.executable, 'setup.py', 'bdist_wheel']
        subprocess.run(args, cwd=self.sampleproject_dirpath, check=True)

        # Setup
        filepath = os.path.join(self.sampleproject_dirpath, 'dist', 'sample-1.2.0-py2.py3-none-any.whl')
        self.embed.add_wheel(filepath)

        self.embed.add_script('sample.console', 'main', 'sample-console', console=True)
        self.embed.add_script('sample.gui', 'main', 'sample-gui', console=False)

        # Run
        workdir = self.embed.run(self.tmpdir, clean=False)

        # Test
        self.assertTrue(os.path.exists(os.path.join(workdir, 'sample-console.exe')))
        self.assertTrue(os.path.exists(os.path.join(workdir, 'sample-gui.exe')))

        args = [os.path.join(workdir, 'sample-console.exe')]
        out = subprocess.run(args, cwd=workdir, check=True, stdout=subprocess.PIPE)
        self.assertEqual(b'Hello world', out.stdout.strip())

if __name__ == '__main__': #pragma: no cover
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
