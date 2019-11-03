""""""

# Standard library modules.
import sys
import subprocess

# Third party modules.

# Local modules.

# Globals and constants variables.


def testbdist_windows(sampleproject_dirpath):
    args = [sys.executable, "setup.py", "--command-packages", "py2win", "bdist_windows"]
    subprocess.run(args, cwd=str(sampleproject_dirpath), check=True)

    distdir = sampleproject_dirpath.joinpath("dist", "sample-1.2.0")
    assert distdir.joinpath("sample-console.exe").exists()
    assert distdir.joinpath("sample-gui.exe").exists()

    args = [str(distdir.joinpath("sample-console.exe")), "--hello"]
    out = subprocess.run(args, cwd=str(distdir), check=True, stdout=subprocess.PIPE)
    assert out.stdout.strip() == b"Hello world"
