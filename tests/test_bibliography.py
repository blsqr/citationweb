"""Test the Bibliography class"""

from shutil import copyfile
from pkg_resources import resource_filename

import pytest

from citationweb.bibliography import Bibliography

# Fixtures --------------------------------------------------------------------

@pytest.fixture
def bib_minimal(tmpdir) -> str:
    """Returns the path to a minimal bibliography file that is copied to a
    temporary directory."""
    src = resource_filename("tests", "libs/minimal.bib")
    dst = tmpdir.join("tmp.bib")

    # Copy the file to the temporary directory and return the path
    copyfile(src, dst)
    return str(dst)

@pytest.fixture
def bib_bibdesk(tmpdir) -> str:
    """Returns the path to a BibDesk bibliography file that is copied to a
    temporary directory."""
    src = resource_filename("tests", "libs/bibdesk.bib")
    dst = tmpdir.join("tmp.bib")

    # Copy the file to the temporary directory and return the path
    copyfile(src, dst)
    return str(dst)

# Tests -----------------------------------------------------------------------

def test_init(bib_minimal, bib_bibdesk):
    """Test the Bibliograpy class initialisation"""
    bib = Bibliography(bib_minimal)

    # Assert the file and the data is loaded
    assert bib.file
    assert bib.data
    assert bib.appdx is None

    # Test different creators
    bd_bib = Bibliography(bib_bibdesk, creator='BibDesk')

    assert bd_bib.file
    assert bd_bib.data
    assert bd_bib.appdx

    # Assert failure for unsupported creators
    with pytest.raises(ValueError, match="Unsupported creator 'invalid'"):
        Bibliography(bib_minimal, creator='invalid')
