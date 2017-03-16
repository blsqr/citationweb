# -*- coding: utf-8 -*-
'''This file containts the crosslink method and the interface to the reference-extracting pdf-extract tool.'''

# TODO
# 	- implement pdf-extract as ruby script instead of interfacing with the shell via subprocess?
#	- multiprocessing
# 	- compare not only by DOIs but also ISBN, URI, ...
#	- add timeout?

# FIXME
#	- papers not being read properly (e.g. Flack2014, Szathmary1997, Watson2010)
# 	- the own citekey or doi is sometimes also added

import os
import copy
import warnings
import re
from base64 import b64decode
import subprocess
import shutil
import xml.etree.ElementTree as ET

from PyPDF2 import PdfFileReader

from pybtex.database import BibliographyData

from .functions import _append_citekey
from .timeout import timeout

# TODO parallelise
def crosslink(bdata, save_dois_to_field=True, read_dois_from='auto'):
	'''The crosslink method extracts citations from each pdf in the bibliography and checks if the target entries are in the bibliography -- if that is the case, the target citekey is added to the 'Cites' field of the bibliography entry.

	For extracting citations, the ruby pdf-extract tool by CrossRef is used: https://github.com/CrossRef/pdfextract

	To turn the Bdsk-File-N fields of each bibliography entry into a readable path, ___ is used.'''

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	# Initialisations
	new_bdata	= copy.deepcopy(bdata)
	cnt 		= (0, len(bdata.entries))
	cnt_added 	= 0

	print("\nStarting to scan library for citations. (mode: {})\n... Patience ...".format(read_dois_from))

	# Looping over all entries
	for citekey in bdata.entries.keys():

		# Initialise some variables
		target_dois 	= [] # list of extracted DOIs
		cnt 			= (cnt[0]+1, cnt[1]) # progress counter

		# # for testing only Hordijk2013a
		# if cnt[0] != 22:
		# 		continue
		print("\n\n{1:}/{2:}:\tExtracting citations from {0:}:\n".format(citekey, *cnt))

		if read_dois_from == 'bib':
			target_dois = extract_citation_dois_from_field(bdata.entries[citekey])

		elif read_dois_from == 'pdf':
			target_dois = extract_citation_dois_from_pdfs(bdata.entries[citekey])

		elif read_dois_from == 'auto':
			# first check, if this entry has an entry in the bibfile. In that case it was parsed already and does not need to be read again
			target_dois = extract_citation_dois_from_field(bdata.entries[citekey])
			# note, that there is the possiblity, that it was not possible to read the pdf. In that case, no DOI was extracted and the target_dois list will just be [''] (with the empty string inside!)

			if target_dois is None:
				# field was not present --> check the pdfs
				target_dois = extract_citation_dois_from_pdfs(bdata.entries[citekey])
			else:
				print("\tFrom field 'Extracted-DOIs' in bibtex entry:")

		else:
			raise ValueError("Invalid value {} for read_dois_from argument. Choose between bib, pdf, and auto.".format(read_dois_from))



		# Try to match the extracted DOIs or those found in the bibfile with entries from the bibliography.
		for target_doi in target_dois:
			if target_doi == '':
				print("\t(marked as un-readable)")
				break

			target_citekey 	= _find_citekey_from_doi(bdata, target_doi)

			if target_citekey is not None and target_citekey != citekey:
				# Add (one side of) link
				cnt_added 	+= _append_citekey(new_bdata.entries[citekey], 'Cites', target_citekey)

				print("\t{:<40} --> {}".format(target_doi, target_citekey))

				print("\t\t'Cites': {}".format(new_bdata.entries[citekey].fields.get('Cites')))

			else:
				print("\t{:<40} --x".format(target_doi))


		#Append found DOIs as a field to the bdata
		if save_dois_to_field:
			new_bdata.entries[citekey].fields['Extracted-DOIs'] = '; '.join(target_dois)

	print("\nAdded {} new links.\n".format(cnt_added))

	return new_bdata


def extract_citation_dois_from_pdf(path, max_num_pages=42, verbatim=True):
	'''Method to extract citations and their DOIs from a pdf file. Returns a list of the found DOIs or an empty list, if an error occured.'''

	# Check, if installed
	if shutil.which('pdf-extract') is None:
		raise EnvironmentError("pdf-extract was not found, but is necessary to extract citations from the PDF files. Please check, if it is installed.")

	cmd			= ["pdf-extract", "extract", "--resolved_references"] #, "--set", "reference_flex:4"]

	num_pages 	= _count_pages(path)
	if verbatim:
		print("\tReading {} ({} pages)".format(os.path.basename(path), num_pages if num_pages != 0 else '?'))

	if num_pages > max_num_pages:
		if verbatim:
			print("too many (>{}) pages! Skipping file".format(max_num_pages))
		return []

	# Get citations and collect terminal prints + xml with results
	try:
		output 	= subprocess.check_output(cmd + [path],
	    	                              shell=False,
	        	                          stderr=subprocess.STDOUT)

	except subprocess.CalledProcessError:
		# does not work with this file
		if verbatim:
			print("\t(not readable)")
		return ['']

	except KeyboardInterrupt:
		print("\n-- Cancelled --")
		exit()

	# extract DOIs from the XML output and return
	return _get_dois_from_xml(output)


def extract_citation_dois_from_pdfs(entry, **kwargs):
	'''Wrapper for extracting citation DOIs from an bibliography entry, which might have multiple files attached'''

	target_dois 	= []

	for path in _resolve_filepaths(entry):
		target_dois 	+= extract_citation_dois_from_pdf(path, **kwargs)

	return target_dois

def extract_citation_dois_from_field(entry):
	'''Checks if there is a field 'Extracted-DOIs' in the entry, parses it to a list and returns it.'''

	extracted_dois 	= entry.fields.get('Extracted-DOIs')

	if extracted_dois is None:
		return None
	else:
		return extracted_dois.split('; ')

# -----------------------------------------------------------------------------
# Private methods -------------------------------------------------------------
# -----------------------------------------------------------------------------


def _resolve_filepaths(entry):
	'''Turns the base64-encoded values from the Bdsk-File-N fields of an entry into actual filepaths.'''

	paths 	= []
	n 		= 1
	regex 	= r"(Users\/.*\/.*?.pdf)\\" # only first match considered

	while entry.fields.get('Bdsk-File-'+str(n)) is not None and n <= 5:
		b64 	= entry.fields.get('Bdsk-File-'+str(n))

		decoded	= str(b64decode(b64))

		match 	= re.findall(regex, decoded)

		paths.append("/" + match[0])

		n += 1

	return paths

def _prepare_xml(s):
	'''Preprocesses the xml string to be readable by the XML parser'''

	# print("XML before:\n{}".format(s))

	xml_start	= '<?xml version="1.0"?>'
	xml_end		= '</pdf>'

	s 	= str(s)
	s 	= s.replace(r"\n"," ")
	s 	= s.replace("<pdf/>", "<pdf></pdf>")

	# if nothing was found, the xml consists only of '<?xml ...?>\n<pdf/>' and in that case, no further stuff should be tried to be stripped away. Note that .find returns -1 when the search string is not found.
	if s.find(xml_start) >= 0 and s.find(xml_end) >= 0:
		s 	= s[s.find(xml_start):s.find(xml_end)+len(xml_end)]

	# print("\nXML after:\n{}\n".format(s))

	return s


def _get_dois_from_xml(xml_str):
	'''This method parses an xml string and returns a list of found DOIs'''
	dois 	= []

	try:
		root 	= ET.fromstring(_prepare_xml(xml_str))

	except ET.ParseError as xml_err:
		print("\tError in parsing XML: {}\n\n{}\n".format(xml_err,_prepare_xml(xml_str)))
		return dois
	else:
		if len(root.findall("resolved_reference")) == 0:
			print("\t(no citations found)")
			return dois

		# Extract DOIs
		for res_ref in root.findall("resolved_reference"):
			dois.append(res_ref.get('doi'))

		return dois


def _find_citekey_from_doi(bdata, target_doi):
	'''Loops over all entries in bibliography data and -- if found -- returns the citekey of an entry, otherwise returns None.'''
	# NOTE consider making public?

	# Checks
	if not isinstance(bdata, BibliographyData):
		raise TypeError("Expected {}, got {}.".format(type(BibliographyData), type(bdata)))

	for citekey in bdata.entries.keys():
		if bdata.entries[citekey].fields.get('doi') == target_doi:
			return citekey

	return None


def _count_pages(filename):
	'''Returns the number of pages of a PDF document'''
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		return PdfFileReader(open(filename, 'rb')).getNumPages()


