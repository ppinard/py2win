""""""

# Standard library modules.
from pathlib import Path

# Third party modules.
import pytest

# Local modules.

# Globals and constants variables.


@pytest.fixture
def sampleproject_dirpath():
    return Path(__file__).parent.resolve() / "testdata" / "sampleproject"
