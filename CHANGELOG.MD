# Changelog

---

## v0.2

**TODO:**
* Multiprocess crosslinking
* Do not read library from code directory and write output to an output directory alongside with network data, plots, ...
* Add network analysis, plotting, ...
* Decouple crosslinking and analysis in a concise way
	* `crosslink.py` handles crosslinking, adding links etc.
	* `cweb.py` handles network creation, analysis, and plotting
* Also analyse/crosslink DOIs to find "missing entries and links" (plot these differently in the citation network)
* *Maybe:*
	* Make bib-file reading more general (not BibDesk-specific)?
	* Consistent way of marking files as unreadable

**FIX:**
* There is an additional ", " in the beginning of Cited-by and Cites fields, probably from a join operation with an empty string as one list element

---

## v0.1
* Base functionality:
	* Importing library
	* Converting URLs to DOIs
	* Reading citations from PDFs and extracting DOIs
	* Crosslinking entries by DOI
	* Adding missing links
	* Simple plotting of citation network
	* Exporting the processed library
	* Comments at the end of the bibfile are preserved
