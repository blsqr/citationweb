# -*- coding: utf-8 -*-
'''(Used for testing the functions of the citationweb package)'''

import citationweb as cweb

# Settings
in_file 	= "lib.bib"
out_file	= "lib_new.bib"


if __name__ == '__main__':
	# Import
	bdata, comments	= cweb.import_bdata(in_file)

	# Process
	bdata = cweb.add_missing_links(bdata)
	bdata = cweb.sort_fields(bdata, ['Cites', 'Cited-By'])
	bdata = cweb.convert_url_to_doi(bdata)

	# Export
	cweb.export_bdata(bdata, out_file, appendix=comments)
