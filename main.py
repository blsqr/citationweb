# -*- coding: utf-8 -*-
'''(Used for testing the functions of the citationweb package)'''

import citationweb as cweb

# Settings
in_file 	= "library_small_new.bib"
out_file	= "library_small_new2.bib"


if __name__ == '__main__':
	# Import
	bdata, comments	= cweb.import_bdata(in_file)

	# Preprocessing
	bdata = cweb.convert_url_to_doi(bdata)

	# Crosslink bibliography entries by extracting citations from each pdf and checking if they are in the bibliography -- if that is the case, the target citekey is added to the 'Cites' field of the bibliography entry
	bdata = cweb.crosslink(bdata)

	# Postprocessing
	bdata = cweb.add_missing_links(bdata)
	bdata = cweb.sort_fields(bdata, ['Cites', 'Cited-By'])

	# Export
	cweb.export_bdata(bdata, out_file, appendix=comments)
