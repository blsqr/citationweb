# -*- coding: utf-8 -*-
'''(Used for testing the functions of the citationweb package)'''

from pybtex.database import parse_file
import citationweb as cweb

# Settings
in_file 	= "lib.bib"
out_file	= "lib_new.bib"


if __name__ == '__main__':
	# Import
	bdata 		= parse_file(in_file)
	comments 	= cweb.extract_comments(in_file)

	# Parse
	new_bdata 	= cweb.add_missing_links(bdata)

	# Export
	new_bdata.to_file(out_file, 'bibtex')
	with open(out_file, 'a') as f:
		f.write(comments)

