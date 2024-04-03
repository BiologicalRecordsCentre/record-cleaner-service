import os
import re
from functools import lru_cache

import pandas as pd


class VcChecker:

    # Private class variables.
    __vc_names = None
    __vc_squares = None

    @classmethod
    def load_data(cls):
        basedir = os.path.abspath(os.path.dirname(__file__))

        # Load the list of vice county names and codes.
        if cls.__vc_names is None:
            cls.__vc_names = pd.read_csv(
                f'{basedir}/vc_names.csv',
                sep=',',
                names=['name', 'code'],
                converters={'name': lambda x: x.lower()}
            )

        # Load the list that relates grid squares to vice counties.
        if cls.__vc_squares is None:
            cls.__vc_squares = pd.read_csv(
                f'{basedir}/vc_squares.csv',
                sep=',',
                header=0,
                names=['gridref', 'vc_dominant', 'vc_count', 'vc_list']
            )

    @classmethod
    @lru_cache
    def prepare_code(cls, value: str | int) -> str:
        """Takes a supplied VC value and returns a code."""

        # British codes may be passes as int or str.
        try:
            value = int(value)
        except ValueError:
            pass

        # British VC codes are in the range 1 to 112.
        if isinstance(value, int):
            if value > 0 and value < 113:
                # A valid British VC code was supplied
                return str(value)
            else:
                raise ValueError('Unrecognised vice county value.')

        # Irish VC codes are in the range H1 to H40.
        match_ie = re.match(r'^[H|h] *(?P<num>\d\d?)$', value)
        if match_ie:
            num = int(match_ie['num'])
            if num > 0 and num < 41:
                # A valid Irish VC code was supplied
                return 'H' + match_ie['num']
            else:
                raise ValueError('Unrecognised vice county value.')

        # Search the VC names for a match if value was not a code.
        seek = value.lower()
        df = cls.__vc_names
        # Locate in the dataframe of __vc_names, the code where the name matches
        # the entered value.
        series = df.loc[df['name'] == seek, 'code']
        if series.size == 1:
            return series.iloc[0]
        else:
            raise ValueError('Unrecognised vice county value.')

    @classmethod
    def prepare_sref(cls, value: str) -> str:
        """Takes a supplied sref and returns a 10km, 2km, or 1km square."""

        # Remove the 100km square indicator. Maybe 1 or 2 characters.
        if value[1].isdigit():
            prefix = value[0]
            suffix = value[1:]
        else:
            prefix = value[0:2]
            suffix = value[2:]

        if len(suffix) in [2, 3, 4]:
            # Already a 10km, 2km, or 1km square
            return value

        # Return a 1km square.
        match len(suffix):
            case 6:
                return prefix + suffix[0:2] + suffix[3:5]
            case 8:
                return prefix + suffix[0:2] + suffix[4:6]
            case 10:
                return prefix + suffix[0:2] + suffix[5:7]

    @classmethod
    @lru_cache
    def check(cls, gridref: str, code: str) -> str:
        """Checks whether the supplied gridref could be in the given VC.

        The gridref should define a 10km, 2km, or 1km square as output by
        self.prepare_sref.
        The code should be a value as output by self.prepare_code.

        By asking you to prep the parameters, the lru_caching will be more
        efficient.
        """

        if code[0] == 'H':
            raise ValueError("Validattion of spatial references against Irish "
                             "VCs is not yet supported.")

        df = cls.__vc_squares
        series = df.loc[df['gridref'] == gridref, 'vc_list']
        if series.size == 1:
            # The gridref is in the list so we can check it.
            # If it is not in the list then we ignore it as it might be at sea,
            # for example, and actually okay.
            vc_list = series.iloc[0].split('#')
            if code not in vc_list:
                raise ValueError("Sref not in vice county.")
