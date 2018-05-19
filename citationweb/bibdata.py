"""This module holds the BibData class that provides an OOP interface to the
bibtex that is to be analysed.
"""

from pybtex.database import BibliographyData, parse_file

# Local constants

# -----------------------------------------------------------------------------

class BibData:
    """A BibData instance attaches to a bibtex file and provides the OOP
    interface to analyse the corresponding citation network.
    """

    def __init__(self, bibfile: str):
        """Load the content of the given bibtex file.
        
        Args:
            bibfile (str): The bibtex file to load and process
        """

        # Initialise property-managed attributes
        self._bdata = None

        # Store properties
        self._bibfile = bibfile

        # Load the file
        self._load()


    # Properties ..............................................................

    @property
    def bibfile(self) -> str:
        """Returns the path to the associated bibfile"""
        return self._bibfile

    # Public methods ..........................................................

    def save(self, path: str=None):
        """Saves the current state of the bibtex data to
        Args:
            path (str, optional): Description
        """
        pass

    # Private methods .........................................................

    def _load(self, **load_kwargs):
        """Load the bibfile associated with this instance."""
        self._bdata = parse_file(self.bibfile, **load_kwargs)
