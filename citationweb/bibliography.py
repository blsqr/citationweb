"""This module holds the Bibliography class that provides an OOP interface
to the bibtex file that is to be analysed.
"""

from pybtex.database import BibliographyData, parse_file

# Local constants

# -----------------------------------------------------------------------------

class Bibliography:
    """A Bibliography instance attaches to a bibtex file and provides the OOP
    interface to analyse the corresponding citation network.
    """

    def __init__(self, file: str):
        """Load the content of the given bibtex file.
        
        Args:
            file (str): The bibtex file to load and process
        """

        # Initialise property-managed attributes
        self._bdata = None

        # Store properties
        self._file = file

        # Load the file
        self._load()


    # Properties ..............................................................

    @property
    def file(self) -> str:
        """Returns the path to the associated file"""
        return self._file
    
    @property
    def data(self) -> BibliographyData:
        """Returns the loaded BibliographyData"""
        return self._bdata

    # Public methods ..........................................................

    def save(self, path: str=None):
        """Saves the current state of the bibtex data to
        Args:
            path (str, optional): Description
        """

    # Private methods .........................................................

    def _load(self, **load_kwargs):
        """Load the file associated with this instance."""
        self._bdata = parse_file(self.file, **load_kwargs)
