#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, 'README.rst'), 'r') as fp:
    LONG_DESCRIPTION = fp.read()

INSTALL_REQUIRES = ['wheel', 'requests']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage']}

setup(name="py2win",
      version='0.1.0',
      url='https://github.com/ppinard/py2win',
      description="Create a stand-alone Windows distribution of a Python program",
      long_description=LONG_DESCRIPTION,
      author="Philippe T. Pinard",
      author_email="philippe.pinard@gmail.com",
      license="MIT",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: Microsoft :: Windows',
                   'Topic :: Software Development'],

      packages=find_packages(),

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      test_suite='nose.collector',
)

