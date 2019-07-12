"""This module implements the network representation of a Bibliography"""

import copy
import logging
from typing import List, Sequence

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import networkx.readwrite

from .tools import load_cfg, recursive_update
from .bibliography import Bibliography, Entry
from .reference import Reference

# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)
    

# -----------------------------------------------------------------------------

class CitationWeb(nx.DiGraph):
    """A network representation of a bibliography and its citations"""

    def __init__(self, bib: Bibliography,
                 *nx_args,
                 include_external_refs: bool=False,
                 prune_lonely: bool=True,
                 **nx_kwargs):
        """Initialize a CitationWeb from a bibliography"""
        # Initialize the parent
        super().__init__(*nx_args, **nx_kwargs)

        self._bib = bib

        # From the bibliography, create the network
        self._construct_citation_web(include_external=include_external_refs,
                                     prune_lonely=prune_lonely)

    def _construct_citation_web(self, *,
                                include_external: bool,
                                prune_lonely: bool) -> None:
        """From the given bibliography, creates a network of citations"""
        log.info("Constructing citation web ...")

        # Go over all entries in the bibliography and add them as nodes
        for entry in self.bib.entries.values():
            node = Reference(entry=entry)
            self.add_node(node)

        log.info("  Created %d nodes from bibliography entries.",
                 self.number_of_nodes())
        log.info("  Adding citations ...")

        # For all entries, also add their references as (directed) edges
        for i, entry in enumerate(self.bib.entries.values()):
            print("  Entry  {:4d} / {:d} ..."
                  "".format(i+1, len(self.bib.entries)), end='\r')

            entry = Reference(entry=entry)
            
            # Get references
            if include_external:
                refs = entry.referenced_dois
            else:
                refs = entry.cites

            if not refs:
                continue

            for doi in refs:
                ref = Reference(doi=doi)

                # Explicitly add a node, if it is not already there
                if ref not in self.nodes:
                    self.add_node(ref)
                    # TODO Add metadata here?

                # Create the link
                self.add_edge(entry, ref)

        if prune_lonely:
            lonely = [n for n in self.nodes
                      if self.in_degree(n) + self.out_degree(n) == 0]
            log.info("  Pruning %d lonely nodes ...", len(lonely))

            for node in lonely:
                self.remove_node(node)

        log.info("Constructed citation web with %d nodes and %d edges.",
                 self.number_of_nodes(), self.number_of_edges())

    # .........................................................................

    @property
    def bib(self):
        """Return the bibliography associated with this citationweb"""
        return self._bib

    def simplified(self, *, fields: Sequence[str]=None) -> nx.DiGraph:
        """Simplifies the network to only include the specified fields. The
        node key will automatically be simplified to either the DOI or the
        citekey.
        """
        web = nx.DiGraph()

        for node, node_attrs in self.nodes.items():
            web.add_node(str(node))

            for ref in self.successors(node):
                web.add_edge(str(node), str(ref))

            if fields:
                raise NotImplementedError("fields")

        return web

    # Plotting ................................................................

    def draw(self, *, show: bool=True,
             layout_algo: str='spring', layout_kwargs: dict=None,
             min_size: float=10., size_factor: float=5.,
             **draw_kwargs):
        """Draw the citationweb using networkx.draw"""
        log.info("Layouting ...")
        # pos = nx.nx_agraph.graphviz_layout(self,
        #                                    prog=layout_algo, args=layout_args)
        # FIXME graphviz layouting; this oughta work!
        pos = getattr(nx, layout_algo + "_layout")(self,
                                                   **(layout_kwargs
                                                      if layout_kwargs
                                                      else {}))

        # Specify node labels, sizes, colors, etc.
        labels = {ref: str(ref) for ref in self.nodes}
        sizes = [min_size + size_factor * self.in_degree(n)
                 for n in self.nodes]
        color = [float(ref.fields.get('year', np.nan)) for ref in self.nodes]

        # Prepare draw kwargs
        draw_kwargs = recursive_update(copy.deepcopy(cfg['draw_kwargs']),
                                       draw_kwargs)

        # Draw now ...
        log.info("Drawing ...")
        nx.draw_networkx(self, pos=pos,
                         labels=labels, node_size=sizes, node_color=color,
                         **draw_kwargs)
        print(labels)
        
        if show:
            plt.show()
        else:
            plt.savefig('cweb.pdf') # FIXME generalise

        plt.close()

    # Saving ..................................................................

    def save(self, *, path: str, format: str='GraphML',
             fields: Sequence[str]=None):
        """Saves the graph at the given path"""
        web = self.simplified(fields=fields)

        # Write it
        nx.readwrite.graphml.write_graphml(web, path=path)
