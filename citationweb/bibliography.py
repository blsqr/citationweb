"""This module holds the Bibliography class that provides an OOP interface
to the bibtex file that is to be analysed.
"""

import os
import copy
import logging
from base64 import b64decode
from typing import List, Tuple, Union

from pybtex.database import BibliographyData, Entry, parse_file

from .pdf_extract import extract_refs_from_pdf
from .crossref import search_for_doi
from .tools import load_cfg, recursive_update

# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------

class Bibliography:
    """A Bibliography instance attaches to a BibTeX file and can extend its
    informations, e.g. by adding missing DOIs or extracting references.
    """

    def __init__(self, filepath: str, *, creator: str=None, **update_cfg):
        """Load the content of the given bibtex file.
        
        Args:
            filepath (str): The bibtex file to load and process
            creator (str, optional): The creator of the BibTeX file. This will
                have an impact on how the file is read and written.
            **update_cfg: Further arguments updating the default configuration
        """
        log.info("Initialising Bibliography ...")

        # Store configuration
        self._cfg = recursive_update(copy.deepcopy(cfg),
                                     copy.deepcopy(update_cfg))

        # Initialise property-managed attributes
        self._filepath = None
        self._creator = None
        self._data = None
        self._appendix = None

        # Store attributes
        self._refs_split_str = self.cfg['refs_split_str']
        self.filepath = filepath
        self.creator = creator

        # Load the bibliography data
        self._load()

        log.info("Bibliography initialised with %d entries.",
                 len(self.entries))


    # Properties ..............................................................

    @property
    def cfg(self) -> dict:
        """Returns the configuration of this object"""
        return self._cfg

    @property
    def filepath(self) -> str:
        """Returns the path to the associated file"""
        return self._filepath

    @filepath.setter
    def filepath(self, path: str):
        """Stores the file property, performing a check if it exists."""
        path = os.path.expanduser(path)

        if not os.path.isfile(path):
            raise FileNotFoundError("No file found at: {} !".format(path))

        self._filepath = path
        log.debug("Associated bibliography file:  %s", self.filepath)
    
    @property
    def data(self) -> BibliographyData:
        """Returns the loaded BibliographyData"""
        return self._data
    
    @property
    def entries(self):
        """Returns the BibliographyData's entries"""
        return self._data.entries
    
    @property
    def appendix(self) -> str:
        """Returns the appendix of the bibfile"""
        return self._appendix

    @property
    def creator(self) -> str:
        """Returns the name of the creator for the bibfile"""
        return self._creator

    @creator.setter
    def creator(self, creator: Union[str, None]):
        """Sets the creator of this Bibliography file"""
        if creator and creator not in self.cfg['creators']:
            raise ValueError("Unsupported creator '{}'! Available: {}"
                             "".format(creator,
                                       ", ".join(self.cfg['creators'])))

        self._creator = creator

    @property
    def creator_params(self) -> dict:
        """Returns the parameters for the set creator or an empty dict

        This property can be conveniently used to check whether a certain
        action is available for a creator.
        """
        if self.creator:
            return self.cfg['creators'][self.creator]
        return dict()

    # Public methods ..........................................................

    def save(self, path: str=None):
        """Saves the current state of the bibtex data to a new file at the
        Args:
            path (str, optional): Description
        """
        # TODO

    def find_DOIs(self, *, search_fields: Tuple[str]=None, **search_kwargs):
        """Goes over all entries and if a DOI is missing, attempts to find it
        by making a crossref API request.
        """
        def generate_query(entry, *, fields: Tuple[str]) -> str:
            """Helper function to generate a query using certain fields"""
            return "; ".join([str(entry.fields.get(field))
                              for field in fields if entry.fields.get(field)])

        # Determine the search fields, if not given
        if not search_fields:
            search_fields = tuple(self.cfg['find_dois']['search_fields'])

        log.info("Finding missing DOIs for %d entries ...", len(self.entries))
        n = 0

        for cite_key, entry in self.entries.items():
            log.debug("Entry:  %s", cite_key)

            if entry.fields.get('doi'):
                continue

            # Generate the query
            query = generate_query(entry, fields=search_fields)

            # Search for it
            doi = search_for_doi(query, **search_kwargs,
                                 expected_title=entry.fields.get('title'),
                                 expected_year=entry.fields.get('year'))

        log.info("Found %d previously missing DOI%s.",
                 n, "s" if n != 1 else "")

    def extract_refs(self, *, from_pdfs: bool=None, from_crossref: bool=False,
                     skip_existing: bool=True):
        """For all entries, extract the references they make to other works.

        This can happen in two ways: By looking at the PDF file and extracting
        the references from there or by making API calls to CrossRef.
        """
        def get_from_pdfs(entry: Entry, *, refs: set):
            """Extracts the references from PDF files of an entry"""
            filepaths = self._resolve_filepaths(entry)
            log.debug("  Found %d associated file(s).", len(filepaths))

            for path in filepaths:
                refs.update(extract_refs_from_pdf(path))
            return refs

        def get_from_crossref(entry: Entry, *, refs: set):
            raise NotImplementedError("from_crossref")

        # Parse parameters
        supports_pdf = self.creator_params.get('can_extract_refs_from_pdfs')
        if from_pdfs is None:
            from_pdfs = supports_pdf
        
        if from_pdfs and not supports_pdf:
            raise ValueError("Extracting references not supported for "
                             "bibliography creator '{}'!".format(self.creator))

        # Go over all entries and extract the information
        log.info("Extracting references for %d entries ...", len(self.entries))

        for cite_key, entry in self.entries.items():
            log.debug("Entry:  %s", cite_key)
            
            # Get already extracted references
            refs = self._extracted_refs(entry)
            log.debug("  Currently have %d reference(s) extracted.", len(refs))

            # Check if references were already extracted and whether to skip
            if refs and params.get('skip_existing'):
                log.debug("  References were already extracted. Skipping ...")
                continue

            if from_pdfs:
                refs = get_from_pdfs(entry, refs=refs)

            if from_crossref:
                refs = get_from_crossref(entry, refs=refs)

            log.debug("  Now have a total of %d references.", len(refs))

            # Store back to the entry
            entry.fields['referenced-dois'] = self._refs_split_str.join(refs)
            log.debug("  Updated references in entry %s.", cite_key)

        log.info("Finished extracting references.")

    def crosslink(self):
        """Using the information from the referenced DOIs of each entry, tries
        to match with other cite keys from within the bibliography and link
        those by adding the cite keys to the ``cites`` and ``cited-by`` fields.
        """
        raise NotImplementedError()

    # Helpers .................................................................

    def _load(self, **parse_kwargs):
        """Load the file associated with this instance.
        
        This loads not only bibliography data but also any form of appendix to
        the file, as common with e.g. BibDesk.
        
        Args:
            **parse_kwargs: Passed to pybtex.database.parse_file
        """
        log.info("Loading bibliography file (%s) ...", self.filepath)

        # Load the bibliography data
        self._data = parse_file(self.filepath, **parse_kwargs)

        # Load the appendix
        if self.creator_params.get('load_appendix'):
            self._load_appendix(**self.creator_params['load_appendix'])

    def _load_appendix(self, *, start_str: str) -> str:
        """This method extracts a part at the end of the bibfile, starting
        with a start_str, for example the @comment{} section or sections of a
        bibtex file.
        
        These sections are used in programs like BibDesk to store the
        information of static and smart folders, and are discarded when using
        parse_file of pybtex.database.
        
        Note that this relies on having the appendix section at the end of the
        file.
        
        Args:
            start_str (str): The string that indicates the start of the appendix
        
        Returns:
            str: The appendix of the bibfile
        """
        appendix = ''
        appendix_reached = False

        with open(self.filepath) as bibfile:
            for line in bibfile:
                if not appendix_reached:
                    # Check if this line starts with the desired string
                    if line.startswith(start_str):
                        # Yup. Reached the appendix now
                        appendix_reached = True

                # Store this line, if in appendix
                if appendix_reached:
                    appendix += line

        self._appendix = appendix

    def _extracted_refs(self, entry: Entry) -> List[str]:
        """Return a list of extracted references, i.e. list of DOIs, for the
        given entry.
        
        Args:
            entry (Entry): The entry to get the extracted references from
        
        Returns:
            List[str]: A list of DOIs
        """
        # Get the entry
        refd_dois = entry.fields.get('referenced-dois')

        if not refd_dois:
            return []

        # There were entries: make a list of DOIs and strip possible whitespace
        return refd_dois.split(self._refs_split_str)

    def _resolve_filepaths(self, entry: Entry) -> List[str]:
        """Depending on the chosen creator, extracts the file path from the 
        given BibliographyData.entry
        
        Args:
            entry (Entry): The entry to resolve the filepaths from
        
        Returns:
            List[str]: List of file paths
        
        Raises:
            ValueError: Unsupported creator
        """
        paths = []
        
        if self.creator == "BibDesk":
            # In BibDesk, the file paths are stored as base-64 encoded symlinks
            # to the linked files and stored in the Bdsk-File-N fields.
            # The Path can be extracted by decoding and matching the filepath
            # pattern. Only PDF files are included here.
            
            # The Bdsk-File-N fields start at 1
            n = 1

            # See if there are such fields, maximum 9
            while entry.fields.get('Bdsk-File-'+str(n)) is not None and n <= 9:
                # Get the b64-encoded field and decode it
                b64 = entry.fields.get('Bdsk-File-'+str(n))
                decoded = str(b64decode(b64))

                # Find the match
                match = re.findall(r"(Users\/.*\/.*?.pdf)\\", decoded)

                # Use the first match to create the appropriate path
                log.debug("  Found a file match: %s", match[0])
                paths.append("/" + match[0])
                # TODO Is this correct?

                # Look at the next Bdsk-File-n field
                n += 1

        else:
            raise ValueError("Filepath resolution from entry is not supported "
                             "for creator: {}".format(self.creator))

        log.debug("Resolved %d file paths of entry %s:\n  %s",
                  len(paths), entry.key, "\n  ".join(paths))
        return paths
