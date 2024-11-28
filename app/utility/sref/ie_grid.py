import re

from math import log10

from . import Sref, SrefAccuracy, SrefCountry
from .sref_base import SrefBase


class IeGrid(SrefBase):

    _srid = 29903

    def __init__(self, sref: Sref):
        sref.country = SrefCountry.IE

        if sref.gridref is not None:
            sref.gridref = self.validate_gridref(sref.gridref)
            # Remove any spurious data.
            sref.easting = sref.northing = None
            sref.accuracy = None
        elif sref.easting is not None and \
                sref.northing is not None and \
                sref.accuracy is not None:
            self.validate_coord(sref.easting, sref.northing)
        else:
            raise ValueError("Invalid spatial reference for Ireland. Either a "
                             "gridref or easting, northing, and accuracy must "
                             "be provided.")

        super().__init__(sref)

    def validate_gridref(self, gridref):
        """Ensure gridref is valid."""

        # Ignore any spaces in the grid ref.
        gridref = gridref.replace(' ', '').upper()

        # Check the first letter is valid.
        sq100 = gridref[0]
        if not re.match(r'[A-HJ-Z]', sq100):
            raise ValueError("Invalid grid reference for Ireland.")

        # Check either remaining chars are all numeric and an equal
        # number, up to 10 digits OR for DINTY Tetrads, 2 numbers followed by a
        # letter (Excluding O, including I).
        eastnorth = gridref[1:]
        if ((
            not re.match(r'^[0-9]*$', eastnorth) or
            len(eastnorth) % 2 != 0 or
            len(eastnorth) > 10
        ) and (
            not re.match(r'^[0-9][0-9][A-NP-Z]$', eastnorth)
        )):
            raise ValueError("Invalid grid reference for Ireland.")

        # Return the clean value.
        return gridref

    def validate_coord(self, easting, northing):
        """Ensure coordinates are valid."""

        if easting < 0 or easting > 500000:
            raise ValueError("""Invalid spatial reference. Easting must be
                             between 0 and 500000""")
        if northing < 0 or northing > 500000:
            raise ValueError("""Invalid spatial reference. Northing must be
                             between 0 and 500000""")

    def calculate_gridref(self):
        """Calculate grid reference from easting and northing."""

        easting = self.easting
        northing = self.northing
        accuracy = self.accuracy
        gridref = None

        hundred_km_e = easting // 100000
        hundred_km_n = northing // 100000
        index = 65 + ((4 - (hundred_km_n % 5)) * 5) + (hundred_km_e % 5)
        # Shift index along if letter is greater than I, since I is skipped
        if index >= 73:
            index += 1
        first_letter = chr(index)

        if accuracy == SrefAccuracy.KM2:
            # DINTY TETRADS
            # 2 numbers at start equivalent to precision = 2
            e = (easting - (100000 * hundred_km_e)) // 10000
            n = (northing - (100000 * hundred_km_n)) // 10000
            letter = (
                65 +
                (northing - (100000 * hundred_km_n) - (n * 10000)) // 2000 +
                5 * (easting - (100000 * hundred_km_e) - (e * 10000)) // 2000
            )
            if letter >= 79:
                letter += 1  # Adjust for no O
            gridref = (
                first_letter + str(e).zfill(1) + str(n).zfill(1) + chr(letter)
            )
        else:
            accuracy_digits = int(5 - log10(accuracy))
            # From 10km accuracy with 1 digit to 1m accuracy with 5.
            e = int((easting - (100000 * hundred_km_e)) // accuracy)
            n = int((northing - (100000 * hundred_km_n)) // accuracy)
            gridref = (
                first_letter +
                str(e).zfill(accuracy_digits) +
                str(n).zfill(accuracy_digits)
            )

        return gridref
