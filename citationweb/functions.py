# -*- coding: utf-8 -*-
'''This file defines all the basic functions of the citationweb package, e.g. import/export and simple processing methods.'''

# TODO:
#	- improve behaviour of comment extraction by actually parsing opening and closing brackets of the comments section



import copy
import codecs

from pybtex.database import BibliographyData, parse_file

# -----------------------------------------------------------------------------
# Import / Export -------------------------------------------------------------
# -----------------------------------------------------------------------------

def import_bdata(bibfile):
	'''This method imports the bibliography from a file and returns its content as a BibliographyData object and a string of comments'''

	bdata 		= parse_file(bibfile)
	comments 	= extract_appendix(bibfile, "@comment{")

	# Info
	if len(comments) > 0:
		print("Imported bibfile '{}' and comments. Bibliography has {} entries.\n".format(bibfile, len(bdata.entries)))
	else:
		print("Imported bibfile '{}'. Bibliography has {} entries.\n".format(bibfile, len(bdata.entries)))

	return bdata, comments


def export_bdata(bdata, targetfile, appendix=None):
	'''Exports the BibliographyData object (and, if passed, an appendix like comments section) to a target.'''
	bdata.to_file(targetfile, 'bibtex')

	if appendix is not None:
		with open(targetfile, 'a') as f:
			f.write(appendix)

		print("\nBibliography and appendix exported to '{}'.".format(targetfile))
	else:
		print("\nBibliography exported to '{}'.".format(targetfile))

	return


def extract_appendix(filepath, start_str):
	'''This method extracts a part at the end of a file, starting with a start_str, for example the @comment{} section or sections of a .bib file.

	These sections are used in programs like BibDesk to store the information of static and smart folders, and are discarded when using parse_file of pybtex.database.
	Note that this relies on having the appendix section at the end of the file.'''

	appdx 			= ''
	appdx_reached 	= False

	with codecs.open(filepath, 'r', 'utf-8') as bibfile:
		for line in bibfile:
			if start_str in line.lower():
				appdx_reached = True

			if appdx_reached:
				appdx += line

	return appdx


# -----------------------------------------------------------------------------
# Simple processing functions -------------------------------------------------
# -----------------------------------------------------------------------------

def add_missing_links(bdata):
	'''Checks the cites and cited-by fields of each bibliography entry and adds them to the respective targets, if they are not already there. Works in-place of the passed bibliography data.'''

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	# Initialisation
	new_bdata 	= copy.deepcopy(bdata)
	n 			= {'cites': 0, 'cited-by': 0}


	# Loop over all article citekeys
	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		cites 	= _str_to_list(entry.fields.get('Cites'))
		cited_by= _str_to_list(entry.fields.get('Cited-by'))

		# find target entries and add the respective keys
		for target_key in cites:
			n['cited-by'] 	+= _append_citekey(new_bdata.entries.get(target_key), 'Cited-By', citekey)

		for target_key in cited_by:
			n['cites'] 		+= _append_citekey(new_bdata.entries.get(target_key), 'Cites', citekey)

	print("Added {} missing 'cites' and {} missing 'cited-by' entries.".format(n['cites'], n['cited-by']))

	# Done. Put the new bibliography data in place
	return new_bdata


def remove_self_citations(bdata):
	'''Removes the own citekey from the cites and cited-by fields'''

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	# Initialisation
	new_bdata 	= copy.deepcopy(bdata)

	# Loop over all article citekeys
	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		cites 	= _str_to_list(entry.fields.get('Cites'))
		cited_by= _str_to_list(entry.fields.get('Cited-by'))

		# find target entries and add the respective keys
		for target_key in cites:
			if target_key == citekey:
				print("removed self-citation in 'Cites' field from {}".format(citekey))
				cites.remove(target_key)

		for target_key in cited_by:
			if target_key == citekey:
				print("removed self-citation in 'Cited-by' field from {}".format(citekey))
				cited_by.remove(target_key)

		# overwrite
		new_bdata.entries[citekey].fields['Cites'] 		= ', '.join(cites)
		new_bdata.entries[citekey].fields['Cited-By'] 	= ', '.join(cited_by)

	# Done. Put the new bibliography data in place
	return new_bdata



def sort_fields(bdata, fieldnames, sep=', '):
	'''Sorts the content of the field with names inside the list fieldnames. Works in place of the bibliography data.'''

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		for fieldname in fieldnames:
			field_content	= _str_to_list(entry.fields.get(fieldname))

			if field_content is not None and field_content != []:
				field_content.sort()
				bdata.entries[citekey].fields[fieldname] = sep.join(field_content)

	print("Sorted fields {} alphabetically.".format(fieldnames))

	return bdata


def convert_url_to_doi(bdata):
	'''Tries to extract the DOI from the Bdsk-url-N field and adds it as an extra field.'''

	# Initialisation
	num_converted 	= 0

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	for citekey in bdata.entries.keys():
		n 		= 1
		entry 	= bdata.entries[citekey]

		if entry.fields.get('doi') is not None:
			# there already is a DOI field in this entry
			continue

		while entry.fields.get('Bdsk-Url-'+str(n)) is not None and n <= 5:
			doi	= _extract_doi_from_url(entry.fields.get('Bdsk-Url-'+str(n)))

			if doi is not None:
				bdata.entries[citekey].fields['DOI'] = doi

				num_converted += 1
				break
			else:
				# continue
				n += 1

	print("Converted {} remote URLs to DOIs.".format(num_converted))

	return bdata

# -----------------------------------------------------------------------------
# Private methods -------------------------------------------------------------
# -----------------------------------------------------------------------------

def _append_citekey(entry, fieldname, ckey, sep=', '):
	'''Append a citekey to the entry.fields[fieldname] string of citekeys (if it does not exist already). Note, that this works directly on the passed entry.'''
	if entry is None:
		# there is no such entry, most probably because this method was called with the .__getitem__ or .get() in the function call and the key was not present
		return False

	ckeys = _str_to_list(entry.fields.get(fieldname))

	if ckey not in ckeys:
		ckeys.append(ckey)
		entry.fields[fieldname] = sep.join(ckeys)

		return True

	else:
		entry.fields[fieldname] = sep.join(ckeys)

		return False


def _str_to_list(s, separators=None, remove_spaces=True):
	'''Takes an entry string and parses it to a list. Sevaral separators can be passed and spaces can be removed before splitting the string to the list.'''

	if s is None:
		return []

	if separators is None:
		# Default values
		separators	= [',', ';']

	# Replace all separators by the first one and remove all spaces
	for sep in separators[1:]:
		s = s.replace(sep, separators[0])

	if remove_spaces:
		s = s.replace(" ", "")

	return s.split(separators[0])


def _extract_doi_from_url(url, tld="http://dx.doi.org/"):
	'''Extracts a DOI from a tld-type url specifying the doi, e.g. addresses starting with http://dx.doi.org/'''

	pos = url.find(tld)

	if pos >= 0:
		# Returns everything after the tld-string
		return url[pos + len(tld):]

	else:
		# No recognisable part in the URL, no conversion possible
		return None
