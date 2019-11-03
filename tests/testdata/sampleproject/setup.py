"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sample",
    version="1.2.0",
    description="A sample Python project",
    long_description=long_description,
    url="https://github.com/pypa/sampleproject",
    author="The Python Packaging Authority",
    author_email="pypa-dev@googlegroups.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="sample setuptools development",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["PyQt5"],
    extras_require={"dev": ["check-manifest"], "test": ["coverage"],},
    package_data={"sample": ["package_data.dat"],},
    data_files=[],
    entry_points={
        "gui_scripts": ["sample-gui=sample.gui:main"],
        "console_scripts": ["sample-console=sample.console:main"],
    },
)
