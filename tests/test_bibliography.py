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

# Tests -----------------------------------------------------------------------

def test_init(bib_minimal):
    """Test the Bibliograpy class initialisation"""
    bib = Bibliography(bib_minimal)

    # Assert the file and the data is loaded
    assert bib.file
    assert bib.data

    # Test different creators
    Bibliography(bib_minimal, creator='BibDesk')

    # Assert failure for unsupported creators
    with pytest.raises(ValueError, match="Unsupported creator 'invalid'"):
        Bibliography(bib_minimal, creator='invalid')
