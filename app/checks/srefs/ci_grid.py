import re


class CiGrid:

    srid = 23030

    def __init__(self, sref: str):
        self.sref = sref

    def validate(self) -> bool:

        # Ignore any spaces in the grid ref.
        self.sref = self.sref.replace(' ', '')

        # Check the first two letters are a valid combination.
        # Column is in range S-Z
        # Rows in the range U-V and A-G
        sq100 = self.sref[:2].upper()
        if not re.match(r'[S-Z]([U-V]|[A-G])', sq100):
            return False

        # Check either remaining chars are all numeric and an equal
        # number, up to 10 digits OR for DINTY Tetrads, 2 numbers followed by a
        # letter (Excluding O, including I).
        eastnorth = self.sref[2:]
        if ((
            not re.match(r'^[0-9]*$', eastnorth) or
            len(eastnorth) % 2 != 0 or
            len(eastnorth) > 10
        ) and (
            not re.match(r'^[0-9][0-9][A-NP-Z]$', eastnorth)
        )):
            return False

        return True
