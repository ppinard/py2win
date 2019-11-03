""""""

# Standard library modules.
import subprocess
import sys

# Third party modules.
import pytest

# Local modules.
from py2win.embed import EmbedPython

# Globals and constants variables.


def testembed_run(sampleproject_dirpath, tmp_path):
    # Create wheel
    args = [sys.executable, "setup.py", "bdist_wheel"]
    subprocess.run(args, cwd=str(sampleproject_dirpath), check=True)

    # Setup
    embed = EmbedPython("sample", "1.2.0")

    filepath = sampleproject_dirpath.joinpath(
        "dist", "sample-1.2.0-py2.py3-none-any.whl"
    )
    embed.add_wheel(filepath)

    embed.add_script("sample.console", "main", "sample-console", console=True)
    embed.add_script("sample.gui", "main", "sample-gui", console=False)

    # Run
    workdir = embed.run(tmp_path, clean=False)

    # Test
    assert workdir.joinpath("sample-console.exe").exists()
    assert workdir.joinpath("sample-gui.exe").exists()

    args = [str(workdir.joinpath("sample-console.exe")), "--hello"]
    out = subprocess.run(args, cwd=str(workdir), check=True, stdout=subprocess.PIPE)
    assert out.stdout.strip() == b"Hello world"
