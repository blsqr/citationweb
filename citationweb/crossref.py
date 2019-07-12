"""This module implements functions to call to the crossref API"""

import logging
import requests
from typing import Union

from .tools import load_cfg


# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)

REQUIRE_SCORE = cfg['require_score']
MIN_SCORE = cfg['min_doi_search_score']

# -----------------------------------------------------------------------------

def search_for_doi(query: str, *, require_score: bool=REQUIRE_SCORE,
                   min_score: float=MIN_SCORE,
                   expected_title: str=None, expected_year: str=None
                   ) -> Union[str, None]:
    """Given a query text, searches via CrossRef to find the DOI
    
    If no DOI could be found or the score is too low, returns None
    
    Args:
        query (str): The search string
        require_score (bool, optional): Whether to require that a score is
            provided by the API
        min_score (float, optional): If so, the minimum score that is to be
            reached in order to
        expected_title (str, optional): If given, will check the title of the
            matched query against the expected title.
        expected_year (str, optional): If given, will check the year of the
            matched query against the expected year.
    
    Returns:
        Union[str, None]: If found (and the score is high enough), the DOI.
            Otherwise None.
    
    Raises:
        ValueError: If a score was required but None could be found or if there
            was an error in stripping a http prefix from the DOI.
    """
    log.debug("Searching for DOI using query:  %s", query)

    # Search via the CrossRef search API, https://search.crossref.org/help/api
    payload = dict(rows=1, q=query)
    r = requests.get('https://search.crossref.org/dois', params=payload)
    # TODO Should check timeout here

    # Read the result, json-encoded
    res = r.json()
    if not res:
        log.warning("  No matches for search query '%s'!", query)
        return None

    # Only need to look at the first entry; was only a single row anyway
    entry = res[0]
    log.debug("  Looking at first entry ...\n%s", entry)

    # Check the score
    log.debug("  Score:  %s", entry.get('score'))
    if require_score and not entry.get('score'):
        raise ValueError("A score was required, but the API request did not "
                         "return one ...")
    
    elif entry.get('score') and entry.get('score') < min_score:
        log.warning("  Search result score %s is below the minimum score %s",
                    entry.get('score'), min_score)
        return None

    # Check the title and year against the expected ones
    if expected_title is not None:
        # TODO Some fuzzy matching
        pass

    if expected_year is not None and entry.get('year') != expected_year:
        log.warning("  Expected the search result to have year %s, was %s!",
                    expected_year, entry.get('year'))
        return None

    # Get the DOI.
    doi = entry.get('doi')
    log.debug("  Found DOI corresponding to citation:  %s", doi)
    return doi
