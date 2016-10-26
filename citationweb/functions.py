# -*- coding: utf-8 -*-
'''This little package provides functions to read and parse a bibtex library, and work on the cited-by and cites keys to create a web of citations'''

# TODO:
#	- make sorting apply not only to parsed entries
#	- improve behaviour of comment extraction by actually parsing opening and closing brackets of the comments section
#
# ------------------------------------------

import copy
import codecs

from pybtex.database import BibliographyData


def extract_comments(filepath):
	'''This method extracts the @comment{} section or sections of a .bib file. These sections are used in programs like BibDesk to store the information of static and smart folders, and are discarded when using parse_file of pybtex.database.
	Note that this relies on having the @comments section at the end of the file.'''

	comments 			= ''
	comments_reached 	= False

	with codecs.open(filepath, 'r', 'utf-8') as bibfile:
		for line in bibfile:
			if "@comment{" in line.lower():
				comments_reached = True

			if comments_reached:
				comments += line

	return comments



def add_missing_links(bdata):
	'''Checks the cites and cited-by fields of each bibliography entry and adds them to the respective targets, if they are not already there. Works in-place of the passed bibliography data.'''

	# Initialisation
	new_bdata 	= copy.deepcopy(bdata)
	n 			= {'cites': 0, 'cited-by': 0}

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	# Loop over all article citekeys
	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		cites 	= _str_to_list(entry.fields.get('Cites'))
		cited_by= _str_to_list(entry.fields.get('Cited-by'))

		# find target entries and add the respective keys
		for target_key in cites:
			n['cited-by'] 	+= _append_citekey(new_bdata.entries[target_key],
			                                   'Cited-By', citekey)

		for target_key in cited_by:
			n['cites'] 		+= _append_citekey(new_bdata.entries[target_key],
			                                   'Cites', citekey)

	print("Added {} missing 'cites' and {} missing 'cited-by' entries.".format(n['cites'], n['cited-by']))

	# Done. Put the new bibliography data in place
	return new_bdata


def sort_fields(bdata, fieldnames, sep=', '):
	'''Sorts the content of the field with names inside the list fieldnames. Works in place of the bibliography data.'''

	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		for fieldname in fieldnames:
			field_content	= _str_to_list(entry.fields.get(fieldname))

			if field_content is not None and field_content != []:
				field_content.sort()
				bdata.entries[citekey].fields[fieldname] = sep.join(field_content)

	print("Sorted fields {}.".format(fieldnames))

	return bdata

# -----------------------------------------------------------------------------
# Private methods -------------------------------------------------------------
# -----------------------------------------------------------------------------

def _append_citekey(entry, fieldname, ckey, sep=', '):
	'''Append a citekey to the entry.fields[fieldname] string of citekeys (if it does not exist already). Note, that this works directly on the passed entry.'''
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

