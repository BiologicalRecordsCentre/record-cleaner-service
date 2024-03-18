import re


class NiGrid:

    srid = 29901

    def __init__(self, sref: str):
        self.sref = sref

    def validate(self) -> bool:

        # Ignore any spaces in the grid ref.
        self.sref = self.sref.replace(' ', '')

        # Check the first letter is valid.
        sq100 = self.sref[0].upper()
        if not re.match(r'[A-HJ-Z]', sq100):
            return False

        # Check either remaining chars are all numeric and an equal
        # number, up to 10 digits OR for DINTY Tetrads, 2 numbers followed by a
        # letter (Excluding O, including I).
        eastnorth = self.sref[1:]
        if ((
            not re.match(r'^[0-9]*$', eastnorth) or
            len(eastnorth) % 2 != 0 or
            len(eastnorth) > 10
        ) and (
            not re.match(r'^[0-9][0-9][A-NP-Z]$', eastnorth)
        )):
            return False

        return True
