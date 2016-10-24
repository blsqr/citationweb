# -*- coding: utf-8 -*-
'''This little package provides functions to read and parse a bibtex library, and work on the cited-by and cites keys to create a web of citations'''

import copy

from pybtex.database import BibliographyData


def add_missing_links(bdata):
	'''Checks the cites and cited-by fields of each bibliography entry and adds them to the respective targets, if they are not already there.'''

	new_bdata = copy.deepcopy(bdata)

	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	for citekey, entry in bdata.entries:
		cites 	= _str_to_list(entry.fields['cites'])
		cited_by= _str_to_list(entry.fields['cited-by'])

		# find target entries and add the respective keys
		for target_key in cites:
			new_bdata.entries[target_key].fields['cites'] 	= _append_citekey(new_bdata.entries[target_key].fields['cites'], citekey)

		for target_key in cited_by:
			new_bdata.entries[target_key].fields['cited-by']= _append_citekey(new_bdata.entries[target_key].fields['cited-by'], citekey)

	# Done. Return the new bibliography data
	return new_bdata











# -----------------------------------------------------------------------------
# Private methods -------------------------------------------------------------
# -----------------------------------------------------------------------------

def _append_citekey(ckey_str, ckey):
	'''Appends string ckey to the string of citekeys ckey_str'''
	ckeys = _str_to_list(ckey_str)

	if ckey not in ckeys:
		ckeys.append(ckey)

	return '; '.join(ckeys)


def _str_to_list(s, separators=None, remove_spaces=True):
	'''Takes an entry string and parses it to a list. Sevaral separators can be passed and spaces can be removed before splitting the string to the list.'''

	if separators is None:
		# Default values
		separators	= [',', ';']

	for sep in separators[1:]:
		s.replace(sep, separators[0])

	if remove_spaces:
		s.replace(" ", "")

	return s.split(separators[0])

