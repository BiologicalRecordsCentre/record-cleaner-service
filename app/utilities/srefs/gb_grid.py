import re

from math import log10

from . import Sref, SrefAccuracy, SrefCountry
from .sref_base import SrefBase


class GbGrid(SrefBase):

    _srid = 27700

    def __init__(self, sref: Sref):
        sref.country = SrefCountry.GB
        super().__init__(sref)

    @classmethod
    def validate(cls, value: Sref):

        if value.gridref is not None:
            cls.validate_gridref(value)
            # Remove any spurious data.
            value.easting = value.northing = None
        elif (value.easting is not None and
                value.northing is not None and
                value.accuracy is not None):
            cls.validate_coord(value)
        else:
            raise ValueError("Invalid spatial reference. Either a gridref or "
                             "easting, northing and accuracy must be "
                             "provided.")

    @classmethod
    def validate_gridref(cls, value: Sref):
        """Ensure gridref is valid."""

        # Ignore any spaces in the grid ref.
        gridref = value.gridref.replace(' ', '').upper()

        # Check the first two letters are a valid combination.
        sq100 = gridref[:2]
        sq100re = r'(H[L-Z]|J[LMQR]|N[A-HJ-Z]|O[ABFGLMQRVW]|S[A-HJ-Z]|T[ABFGLMQRVW])'
        if not re.match(sq100re, sq100):
            raise ValueError("Invalid grid reference for Great Britain.")

        # Check either remaining chars are all numeric and an equal
        # number, up to 10 digits OR for DINTY Tetrads, 2 numbers followed by a
        # letter (Excluding O, including I).
        eastnorth = gridref[2:]
        if ((
            not re.match(r'^[0-9]*$', eastnorth) or
            len(eastnorth) % 2 != 0 or
            len(eastnorth) > 10
        ) and (
            not re.match(r'^[0-9][0-9][A-NP-Z]$', eastnorth)
        )):
            raise ValueError("Invalid grid reference for Great Britain.")

        # Update the gridref with the clean value.
        value.gridref = gridref

    @classmethod
    def validate_coord(cls, value: Sref):
        """Ensure coordinates are valid."""

        if value.easting < 0 or value.easting > 700000:
            raise ValueError("Invalid spatial reference. Easting must be "
                             "between 0 and 700000")
        if value.northing < 0 or value.northing > 1300000:
            raise ValueError("Invalid spatial reference. Northing must be "
                             "between 0 and 1300000")

    def calculate_gridref(self):
        """Calculate grid reference from easting and northing."""

        easting = self.easting
        northing = self.northing
        accuracy = self.accuracy
        gridref = None

        hundredKmE = easting // 100000
        hundredKmN = northing // 100000
        firstLetter = ""
        if hundredKmN < 5:
            if hundredKmE < 5:
                firstLetter = "S"
            else:
                firstLetter = "T"
        elif hundredKmN < 10:
            if hundredKmE < 5:
                firstLetter = "N"
            else:
                firstLetter = "O"
        else:
            firstLetter = "H"
        secondLetter = ""
        index = 65 + ((4 - (hundredKmN % 5)) * 5) + (hundredKmE % 5)
        # Shift index along if letter is greater than I, since I is skipped.
        if index >= 73:
            index += 1
        secondLetter = chr(index)

        if accuracy == SrefAccuracy.KM2:
            # DINTY TETRADS
            # 2 numbers at start equivalent to accuracy = 10,000.
            e = (easting - (100000 * hundredKmE)) // 10000
            n = (northing - (100000 * hundredKmN)) // 10000
            letter = (
                65 +
                (northing - (100000 * hundredKmN) - (n * 10000)) // 2000 +
                5 * ((easting - (100000 * hundredKmE) - (e * 10000)) // 2000)
            )
            if letter >= 79:
                letter += 1  # Adjust for no O
            gridref = (
                firstLetter + secondLetter +
                str(e).zfill(1) + str(n).zfill(1) + chr(letter)
            )
        else:
            accuracy_digits = int(5 - log10(accuracy))
            # From 10km accuracy with 1 digit to 1m accuracy with 5.
            e = (easting - (100000 * hundredKmE)) // accuracy
            n = (northing - (100000 * hundredKmN)) // accuracy

            gridref = (
                firstLetter + secondLetter +
                str(e).zfill(accuracy_digits) + str(n).zfill(accuracy_digits)
            )

        return gridref
