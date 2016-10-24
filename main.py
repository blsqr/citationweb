# -*- coding: utf-8 -*-
'''(Used for testing the functions of the citationweb package)'''

from pybtex.database import parse_file
import citationweb as cweb

# Settings
in_file 	= "lib.bib"
out_file	= "lib_new.bib"


if __name__ == '__main__':
	bdata 		= parse_file(in_file)

	new_bdata 	= cweb.add_missing_links(bdata)

	new_bdata.to_file(out_file, 'bibtex') #TODO check compatibility of saving format

