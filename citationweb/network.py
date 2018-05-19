# -*- coding: utf-8 -*-
"""Here, network functionality is implemented"""

import matplotlib as mpl

from pybtex.database import BibliographyData

import graph_tool.all as gt

def create_network(bdata, verbose=False):
    """Takes the bibliography data, analyses its cites field and returns a network of citations: vertices are publications, edges are (directed) citations."""


    # Checks
    if not isinstance(bdata, BibliographyData):
        raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

    # Initialisation of a directed graph
    nw  = gt.Graph()
    nw.set_directed(True)

    # Initialise graph-internal property maps for citekey, year, targets
    nw.vp.ckey = nw.new_vertex_property('string')
    nw.vp.year = nw.new_vertex_property('short')
    nw.vp.cites = nw.new_vertex_property('object')
    nw.vp.alone = nw.new_vertex_property('bool')
    nw.vp.num_cits = nw.new_vertex_property('short')

    # First loop: create all vertices and populate property maps
    for ckey in bdata.entries.keys():
        v = nw.add_vertex()
        nw.vp.ckey[v] = ckey
        nw.vp.year[v] = bdata.entries[ckey].fields.get('year')
        nw.vp.alone[v] = True

        cites = bdata.entries[ckey].fields.get('cites')
        nw.vp.cites[v] = cites.split(', ') if cites is not None else []

    # Second loop: over the graph. Add the cites targets as edges
    for v in nw.vertices():
        # find vertex specificer of the targets in cites field. As the vertices are still unconnected, just loop over everything.
        cites = nw.vp.cites[v] # a python list

        if cites == ['']:
            continue

        for t in nw.vertices():
            for c in cites:
                if nw.vp.ckey[t] == c:
                    nw.add_edge(v, t)
                    cites.remove(c)

                    # ...these vertices are no longer alone
                    nw.vp.alone[v] = False
                    nw.vp.alone[t] = False

                    # ...increase the citation number of the target by 1
                    nw.vp.num_cits[t] += 1

                    if verbose:
                        print("Added edge {}->{}".format(nw.vp.ckey[v],c))

        if len(cites) > 0:
            print("{} unresolved targets for publication {}: {}".format(len(cites), nw.vp.ckey[v], cites))

    return nw


def plot_network(nw, filter_unconnected=True, mode='graphviz', **kwargs):
    """Plots a graphical presentation of the passed network. The view is specialised on citation networks."""

    if filter_unconnected:
        nw.set_vertex_filter(nw.vp.alone, inverted=True)




    if mode == None:
        vprops  = {
            # 'shape':      'none',
            # 'aspect':     2,
            # 'size':           10,
            'font_family':  'sans-serif',
            'font_size':    8,
            # 'text_color':     'black'
        }

        pos = gt.arf_layout(nw, max_iter=10000)
        # pos   = gt.fruchterman_reingold_layout(nw, n_iter=1000, r=100, scale=20)

        gt.graph_draw(nw, pos=pos,
                      vorder=nw.vp.year,
                      vprops=vprops, vertex_text=nw.vp.ckey,
                      output_size=(1200,1200),
                      fit_view=True,
                      **kwargs)

    elif mode == 'graphviz':

        output = kwargs.get('output')
        if output is None:
            output = 'out.pdf'

        vprops = {
            'label':        nw.vp.ckey,
            'fontname':     'Helvetica bold',
            'fontsize':     20,
            'fontcolor':    'black'
        }

        eprops = {
            'len':          0.5,
            'dir':          'forward',
            'arrowsize':    1.5,
        }

        gt.graphviz_draw(nw, size=(10,16), output=output,
                         vprops=vprops,
                         eprops=eprops,
                         layout='fdp',
                         ratio=10/16,
                         vcolor=nw.vp.num_cits,
                         vnorm=True,
                         vcmap=mpl.cm.get_cmap('Reds'),
                         sep=0.1,
                         vsize=1,
                         overlap='prism',
                         penwidth=2.5,
                         splines='curved')

    print("plotted")
