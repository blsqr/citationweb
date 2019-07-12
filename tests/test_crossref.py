"""Test the pdf extraction feature"""

import pytest

from citationweb.crossref import search_for_doi

# -----------------------------------------------------------------------------

def test_search_for_doi():
    """Test whether searching for DOIs via CrossRef API calls works"""
    citations = [ # format: (target DOI, search text)
        ("10.1073/pnas.1618722114",
         "Optimal incentives for collective intelligence "
         "Richard P. Mann, Dirk Helbing "
         "Proceedings of the National Academy of Sciences May 2017",
         dict(expected_year=2017)),
        ("10.1073/pnas.1618722114",
         "Optimal incentives for collective intelligence",
         dict(expected_year=2017)),
        ("10.1038/ncomms12285",
         "High-order species interactions shape ecosystem diversity", {}),
        ("10.1098/rstb.2016.0175",
         "The major synthetic evolutionary transitions R.V. Solé", {}),
        (None, "boVszEQfwmKItVV8qebp", {}),  # should not give a result
    ]

    for doi, citation, kws in citations:
        print("Citation:      ", citation)
        print("Expected DOI:  ", doi)
        assert doi == search_for_doi(citation, **kws)
        print("Search was successful.\n")

    # Test error messages
    with pytest.raises(ValueError, match="A score was required"):
        search_for_doi(citations[0], require_score=True)
