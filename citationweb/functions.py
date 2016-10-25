# -*- coding: utf-8 -*-
'''This little package provides functions to read and parse a bibtex library, and work on the cited-by and cites keys to create a web of citations'''

import copy
import codecs

from pybtex.database import BibliographyData


def extract_comments(filepath):
	'''This method extracts the @comment{} section or sections of a .bib file. These sections are used in programs like BibDesk to store the information of static and smart folders, and are discarded when using parse_file of pybtex.database.
	Note that this relies on having the @comments section at the end of the file.'''
	# TODO improve behaviour by parsing opening and closing brackets of comments section

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
	'''Checks the cites and cited-by fields of each bibliography entry and adds them to the respective targets, if they are not already there.'''

	new_bdata = copy.deepcopy(bdata)

	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	for citekey in bdata.entries.keys():
		entry 	= bdata.entries[citekey]

		cites 	= _str_to_list(entry.fields.get('Cites'))
		cited_by= _str_to_list(entry.fields.get('Cited-by'))

		# find target entries and add the respective keys
		for target_key in cites:
			new_bdata.entries[target_key].fields['Cited-by'] = _append_citekey(new_bdata.entries[target_key].fields.get('Cited-by'), citekey)

		for target_key in cited_by:
			new_bdata.entries[target_key].fields['Cites'] = _append_citekey(new_bdata.entries[target_key].fields.get('Cites'), citekey)

	# Done. Return the new bibliography data
	return new_bdata







# -----------------------------------------------------------------------------
# Private methods -------------------------------------------------------------
# -----------------------------------------------------------------------------

def _append_citekey(ckey_str, ckey, verbatim=True, sep=', '):
	'''Appends string ckey to the string of citekeys ckey_str (if it does not exist already) and returns the re-parsed string of all citekeys.'''
	ckeys = _str_to_list(ckey_str)

	if ckey not in ckeys:
		if verbatim:
			print("Appending {} to {}".format(ckey, ckeys))

		ckeys.append(ckey)

	return sep.join(ckeys)


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

