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

def test_search_for_doi():
    """Test whether searching for DOIs via CrossRef API calls works"""
    citations = [ # format: (target DOI, search text)
        ("10.1073/pnas.1618722114",
         "Optimal incentives for collective intelligence "
         "Richard P. Mann, Dirk Helbing "
         "Proceedings of the National Academy of Sciences May 2017"),
        (None, "foo bar"),
    ]

    for doi, citation in citations:
        print("Citation: ", citation)
        print("Expected DOI: ", doi)
        assert doi == pdfx._search_for_doi(citation)
        print("Search was successful.\n")
