from pyproj import Transformer

from . import Sref, SrefAccuracy, SrefCountry
from .sref_base import SrefBase
from .ci_grid import CiGrid
from .ie_grid import IeGrid
from .gb_grid import GbGrid


class Wgs84(SrefBase):

    def __init__(self, sref: Sref):
        self.value = sref

    @SrefBase.value.setter
    def value(self, value: Sref):

        if value.latitude is None or \
                value.longitude is None or \
                value.accuracy is None:
            raise ValueError("""Invalid spatial reference. Latitude, longitude
                             and accuracy are required.""")

        if value.latitude < -90 or value.latitude > 90:
            raise ValueError("""Invalid spatial reference. Latitude must be
                             between -90 and 90.""")
        if value.longitude < -180 or value.longitude > 180:
            raise ValueError("""Invalid spatial reference. Longitude must be
                             between -180 and 180.""")

        self._value = value

    def calculate_gridref(self):
        """Determines the GB, IE or CI grid reference."""
        match self.country:
            case SrefCountry.GB:
                sref_class = GbGrid
            case SrefCountry.IE:
                sref_class = IeGrid
            case SrefCountry.CI:
                sref_class = CiGrid

        # Convert the lat/lon to coords in the country grid ref system.
        sref_data = {'accuracy': self.accuracy}
        transformer = Transformer.from_crs(self.srid, sref_class.srid)
        sref_data['easting'], sref_data['northing'] = \
            transformer.transform(self.latitude, self.longitude)

        # Instantiate an object of the grid ref class with the calculated
        # values and get the grid reference.
        self._value.gridref = sref_class(**sref_data).gridref
