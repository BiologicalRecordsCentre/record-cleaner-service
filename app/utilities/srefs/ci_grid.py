import re

from math import log10

from . import Sref, SrefAccuracy, SrefCountry
from .sref_base import SrefBase


class CiGrid(SrefBase):

    def __init__(self, sref: Sref):
        sref.country = SrefCountry.CI
        self.value = sref

    @SrefBase.value.setter
    def value(self, value: Sref):

        if value.gridref is not None:
            self.validate_gridref(value)
        elif value.easting is not None and \
                value.northing is not None and \
                value.accuracy is not None:
            self.coord_to_gridref(value)
        else:
            raise ValueError("Invalid grid reference for Channel Islands.")

        self._value = value

    @staticmethod
    def validate_gridref(value: Sref):
        # Ignore any spaces in the grid ref.
        gridref = value.gridref.replace(' ', '').upper()

        # Check the first two letters are a valid combination.
        # Column is in range S-Z
        # Rows in the range U-V and A-G
        sq100 = gridref[:2]
        if not re.match(r'[S-Z]([U-V]|[A-G])', sq100):
            raise ValueError("Invalid grid reference for Channel Islands.")

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
            raise ValueError("Invalid grid reference for Channel Islands.")

        value.gridref = gridref

    @staticmethod
    def coord_to_gridref(value: Sref):

        easting = value.easting
        northing = value.northing
        accuracy = value.accuracy
        gridref = None

        if (easting < 100000 or easting > 900000 or
                northing < 5300000 or northing > 6200000):
            raise ValueError('Invalid grid reference for Channel Islands.')

        hundredKmE = easting // 100000
        hundredKmN = northing // 100000
        firstLetter = chr(ord('S') + hundredKmE - 1)

        if hundredKmN < 55:
            index = ord('U') + hundredKmN - 53
        else:
            index = ord('A') + hundredKmN - 55
        secondLetter = chr(index)

        if accuracy == SrefAccuracy.KM2:
            # DINTY TETRADS
            # 2 numbers at start equivalent to precision = 2
            e = (easting - (100000 * hundredKmE)) // 10000
            n = (northing - (100000 * hundredKmN)) // 10000
            letter = (
                65 +
                (northing - (100000 * hundredKmN) - (n * 10000)) // 2000 +
                5 * (easting - (100000 * hundredKmE) - (e * 10000)) // 2000
            )
            if letter >= 79:
                letter += 1  # Adjust for no O
            gridref = firstLetter + secondLetter + e + n + chr(letter)
        else:
            accuracy_digits = int(5 - log10(accuracy))
            # From 10km accuracy with 1 digit to 1m accuracy with 5.
            e = (easting - (100000 * hundredKmE)) // accuracy
            n = (northing - (100000 * hundredKmN)) // accuracy
            gridref = (
                firstLetter + secondLetter +
                str(e).zfill(accuracy_digits) + str(n).zfill(accuracy_digits)
            )

        value.gridref = gridref
