"""This module implements the network representation of a Bibliography"""

import logging
from typing import List

import networkx as nx

from .tools import load_cfg
from .bibliography import Bibliography, Entry
from .entry import UniqueEntry

# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)

    

# -----------------------------------------------------------------------------

class CitationWeb:
    """A network representation of a bibliography and its citations"""

    def __init__(self, bib: Bibliography):
        """Initialize a CitationWeb from a bibliography"""
        self._bib = bib

        # From the bibliography, create the network
        self._web = self._construct_citation_web(self._bib)

    def _construct_citation_web(self, bib: Bibliography) -> nx.DiGraph:
        """From the given bibliography, creates a network of citations"""
        web = nx.DiGraph()

        # Go over all entries in the bibliography and add them as nodes. If
        # there are referenced DOIs, also add those nodes.
        for cite_key, entry in bib.entries.items():
            node = UniqueEntry(entry=entry)
            web.add_node(node)


    # Properties ..............................................................

    @property
    def bib(self):
        """Return the bibliography associated with this citationweb"""
        return self._bib
    
    # Plotting ................................................................

    def plot(self):
        raise NotImplementedError("plot")


    # Helpers .................................................................
