# -*- coding: utf-8 -*-
'''(Used for testing the functions of the citationweb package)'''

import sys
import citationweb as cweb


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        raise ValueError("No in_file supplied!")
    elif len(sys.argv) == 2:
        in_file = sys.argv[1]
        out_file = "libs/_out/library.bib"
    else:
        in_file = sys.argv[1]
        out_file = sys.argv[2]

    print("\nPaths to input and output library set:\n  in:\t{}\n  out:\t{}\n".format(in_file, out_file))

    # Import
    bdata, comments = cweb.import_bdata(in_file)

    # Preprocessing
    bdata = cweb.convert_url_to_doi(bdata)

    # Crosslink bibliography entries by extracting citations from each pdf and checking if they are in the bibliography -- if that is the case, the target citekey is added to the 'Cites' field of the bibliography entry
    bdata = cweb.crosslink(bdata)

    # Postprocessing
    bdata = cweb.remove_self_citations(bdata)
    bdata = cweb.add_missing_links(bdata)
    bdata = cweb.sort_fields(bdata, ['Cites', 'Cited-By'])

    # Analysis
    cnw = cweb.create_network(bdata)

    # Plotting
    cweb.plot_network(cnw, mode='graphviz', output='cnet.pdf')

    # Export
    cweb.export_bdata(bdata, out_file, appendix=comments)
