"""This module holds the Bibliography class that provides an OOP interface
to the bibtex file that is to be analysed.
"""

from pybtex.database import BibliographyData, parse_file

from citationweb.tools import load_cfg

# Local constants
cfg = load_cfg(__name__)

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
        if creator and creator not in self.CREATOR_PARAMS.keys():
            creators = [k for k in self.CREATOR_PARAMS.keys()]
            raise ValueError("Unsupported creator '{}'! Supported creators "
                             "are: {}".format(creator, ", ".join(creators)))

        self._creator = creator

    @property
    def creator_params(self) -> dict:
        """Returns the parameters for the set creator or an empty dict"""
        if self.creator:
            return self.CREATORS[self.creator]
        return dict()

    # Public methods ..........................................................

    def save(self, path: str=None):
        """Saves the current state of the bibtex data to
        Args:
            path (str, optional): Description
        """

    # Private methods .........................................................

    def _load(self, **load_kwargs):
        """Load the file associated with this instance.

        This loads not only bibliography data but also any form of appendix to
        the file, as common with e.g. BibDesk.
        """
        # Load the bibliography data
        self._data = parse_file(self.file, **load_kwargs)

        # Load the appendix
        self._load_appdx(self.creator_params.get('load_appdx'))

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
                        appdx_reached = True
                    continue

                # Store this line
                appdx += line

        self._appdx = appdx
