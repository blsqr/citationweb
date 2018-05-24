"""This module holds the Bibliography class that provides an OOP interface
to the bibtex file that is to be analysed.
"""

import os
import logging
from typing import List

from pybtex.database import BibliographyData, Entry, parse_file

from citationweb.pdf_extract import extract_refs
from citationweb.tools import load_cfg

# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)

REFS_SPLIT_STR = cfg['refs_split_str']

# -----------------------------------------------------------------------------

class Bibliography:
    """A Bibliography instance attaches to a bibtex file and provides the OOP
    interface to analyse the corresponding citation network.
    
    Attributes:
        CREATORS (list): A list of supported creator programmes
    """
    # Class variables
    CREATORS = cfg['creators']

    def __init__(self, file: str, creator: str=None):
        """Load the content of the given bibtex file.
        
        Args:
            file (str): The bibtex file to load and process
            creator (str, optional): The creator of the bibtex file. This will
                have an impact on how the file is read and written.
        """
        log.info("Initialising Bibliography ...")

        # Initialise property-managed attributes
        self._file = None
        self._creator = None
        self._data = None
        self._appdx = None

        # Store properties
        self.file = file
        self.creator = creator

        # Load the bibliography data
        self._load()

        log.info("Bibliography initialised.")


    # Properties ..............................................................

    @property
    def file(self) -> str:
        """Returns the path to the associated file"""
        return self._file

    @file.setter
    def file(self, path: str):
        """Stores the file property, performing a check if it exists."""
        if not os.path.isfile(path):
            raise FileNotFoundError("No such bibliography file: "+str(path))

        self._file = path
        log.debug("Associated bibliography file:  %s", self.file)
    
    @property
    def data(self) -> BibliographyData:
        """Returns the loaded BibliographyData"""
        return self._data
    
    @property
    def appdx(self) -> str:
        """Returns the appendix of the bibfile"""
        return self._appdx

    @property
    def creator(self) -> str:
        """Returns the name of the creator for the bibfile"""
        return self._creator

    @creator.setter
    def creator(self, creator: str):
        """Sets the creator of this Bibliography file"""
        if creator and creator not in self.CREATORS.keys():
            creators = [k for k in self.CREATORS.keys()]
            raise ValueError("Unsupported creator '{}'! Supported creators "
                             "are: {}".format(creator, ", ".join(creators)))

        self._creator = creator

    @property
    def creator_params(self) -> dict:
        """Returns the parameters for the set creator or an empty dict

        This property can be conveniently used to check whether a certain
        action is available for a creator.
        """
        if self.creator:
            return self.CREATORS[self.creator]
        return dict()

    # Public methods ..........................................................

    def save(self, path: str=None):
        """Saves the current state of the bibtex data to
        Args:
            path (str, optional): Description
        """
        # TODO

    def extract_refs(self):
        """Extracts the references of linked pdf files."""
        params = self.creator_params.get('extract_refs')

        if not params:
            log.info("Extracting references not supported for creator %s.",
                     self.creator)
            return

        for cite_key, entry in self.data.entries.items():
            log.debug("Entry:  %s", cite_key)
            # Check if references were already extracted and whether to skip
            if params.get('skip_existing') and self._extracted_refs(entry):
                log.debug("  References were already extracted.")
                continue

            filepaths = self._resolve_filepaths(entry)

            if not filepaths:
                # Could not resolve a file path for this one
                log.debug("  Could not find a file path for this entry.")
                continue

            # Check the PDF files



    # Private methods .........................................................

    def _load(self, **parse_kwargs):
        """Load the file associated with this instance.
        
        This loads not only bibliography data but also any form of appendix to
        the file, as common with e.g. BibDesk.
        
        Args:
            **parse_kwargs: Passed to pybtex.database.parse_file
        """
        log.info("Loading bibliography file ...")

        # Load the bibliography data
        self._data = parse_file(self.file, **parse_kwargs)

        # Load the appendix
        if 'load_appdx' in self.creator_params:
            self._load_appdx(**self.creator_params['load_appdx'])

    def _load_appdx(self, start_str: str) -> str:
        """This method extracts a part at the end of the bibfile, starting
        with a start_str, for example the @comment{} section or sections of a
        bibtex file.
        
        These sections are used in programs like BibDesk to store the
        information of static and smart folders, and are discarded when using
        parse_file of pybtex.database.
        
        Note that this relies on having the appendix section at the end of the
        file.
        
        Args:
            start_str (str): The string that indicates the start of the appdx
        
        Returns:
            str: The appendix of the bibfile
        """

        appdx = ''
        appdx_reached = False

        with open(self.file) as bibfile:
            for line in bibfile:
                if not appdx_reached:
                    # Check if this line starts with the desired string
                    if line.startswith(start_str):
                        # Yup. Reached the appendix now
                        appdx_reached = True

                # Store this line, if in appdx
                if appdx_reached:
                    appdx += line

        self._appdx = appdx

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
        return refd_dois.split(REFS_SPLIT_STR)

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
                paths.append("/" + match[0])

                # Look at the next Bdsk-File-n field
                n += 1

        else:
            raise ValueError("Filepath resolution from entry is not supported "
                             "for creator: {}".format(self.creator))

        log.debug("Resolved %d file paths of entry %s:\n  %s",
                  len(paths), entry.key, "\n  ".join(paths))
        return paths
