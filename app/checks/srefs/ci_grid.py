import re


class CiGrid:

    _srid = 23030
    _sref = None

    def __init__(self, sref: str):
        self.sref = sref

    @property
    def srid(self):
        return self._srid

    @property
    def sref(self):
        return self._sref

    @sref.setter
    def sref(self, value):

        # Ignore any spaces in the grid ref.
        value = value.replace(' ', '')

        # Check the first two letters are a valid combination.
        # Column is in range S-Z
        # Rows in the range U-V and A-G
        sq100 = value[:2].upper()
        if not re.match(r'[S-Z]([U-V]|[A-G])', sq100):
            raise ValueError("Invalid grid reference for Channel Islands.")

        # Check either remaining chars are all numeric and an equal
        # number, up to 10 digits OR for DINTY Tetrads, 2 numbers followed by a
        # letter (Excluding O, including I).
        eastnorth = value[2:]
        if ((
            not re.match(r'^[0-9]*$', eastnorth) or
            len(eastnorth) % 2 != 0 or
            len(eastnorth) > 10
        ) and (
            not re.match(r'^[0-9][0-9][A-NP-Z]$', eastnorth)
        )):
            raise ValueError("Invalid grid reference for Channel Islands.")

        self._sref = value
