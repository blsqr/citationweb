"""This module implements bibliography-entry related classes"""

import logging
from typing import Union, List

from pybtex.database import Entry

from .tools import load_cfg

# Local constants
cfg = load_cfg(__name__)
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------

class Reference:
    """A unique identifier of a bibliography entry, consisting of an entry 
    and a DOI.
    """
    __slots__ = ('_entry', '_doi')

    def __init__(self, *, entry: Entry=None, doi: str=None):
        self._entry = None
        self._doi = None

        if entry is not None and doi is not None:
            raise ValueError("Can only supply an entry _or_ a DOI, got both!")

        elif entry is not None:
            self._entry = entry

        elif doi is not None:
            self._doi = doi

        else:
            raise ValueError("Need either a DOI or an entry, got neither!")

    def __hash__(self) -> str:
        """The hash of this entry is _ideally_ the same as that of the DOI.
        Only if there is no DOI, it falls back to the citekey.
        """
        if self.doi:
            return hash(self.doi)
        return hash(self.citekey)

    def __eq__(self, other) -> bool:
        """Compares this object to another Reference or a citekey or a DOI.
        Only one of the comparisons needs to be fulfilled in order to let this
        method return True.
        """
        if isinstance(other, Reference):
            return (self.citekey == other.citekey) or (self.doi == other.doi)
        return (self.citekey == other) or (self.doi == other)

    def __str__(self) -> str:
        """Returns a string representation: either the citekey or the DOI"""
        if self.citekey:
            return self.citekey
        return "doi: " + self.doi

    def __repr__(self) -> str:
        return "<{}.{} at {}, {}>".format(__name__, type(self).__name__,
                                          hex(id(self)), str(self))

    def _get_dois_from_field(self, fieldname: str) -> Union[List[str], None]:
        dois = self.fields.get(fieldname)
        if dois:
            return dois.split(cfg['refs_split_str'])
        return None

    # Properties ..............................................................

    @property
    def entry(self) -> Union[Entry, None]:
        return self._entry

    @property
    def doi(self) -> Union[str, None]:
        if self._doi:
            return self._doi
        return self.entry.fields.get('doi')

    @property
    def citekey(self):
        if self.entry is not None:
            return self.entry.key
        return None

    @property
    def fields(self) -> dict:
        if self.entry is not None:
            return self.entry.fields
        return dict(doi=self.doi)
    
    @property
    def referenced_dois(self) -> Union[List[str], None]:
        return self._get_dois_from_field('referenced-dois')
    
    @property
    def cites(self) -> Union[List[str], None]:
        return self._get_dois_from_field('cites')
        
    @property
    def cited_by(self) -> Union[List[str], None]:
        return self._get_dois_from_field('cited-by')
