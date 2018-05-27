"""Test the pdf extraction feature"""

import glob
from typing import List

from pkg_resources import resource_filename

import pytest

import citationweb.pdf_extract as pdfx

# Fixtures --------------------------------------------------------------------

@pytest.fixture
def pdf_files() -> List[str]:
    """Returns a list of pdf file paths that are included with the tests."""
    test_dir = resource_filename('citationweb', 'tests/pdfs')
    return glob.glob(os.path.join(test_dir, "*.pdf"))
    

# Tests -----------------------------------------------------------------------
