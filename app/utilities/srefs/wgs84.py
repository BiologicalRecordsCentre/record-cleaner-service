from pyproj import Transformer

from . import Sref, SrefCountry
from .sref_base import SrefBase
from .ci_grid import CiGrid
from .ie_grid import IeGrid
from .gb_grid import GbGrid


class Wgs84(SrefBase):

    _srid = 4326

    def __init__(self, sref: Sref):
        sref.country = None
        sref.gridref = None
        self.value = sref

    @classmethod
    def validate(clas, value: Sref):

        # Validate the input.
        if value.latitude is None or \
                value.longitude is None or \
                value.accuracy is None:
            raise ValueError("""Invalid spatial reference. Latitude, longitude
                             and accuracy are required.""")

        if value.latitude < 48.0 or value.latitude > 62.0:
            raise ValueError("""Invalid spatial reference. Latitude must be
                             roughly between 48 and 62.""")
        if value.longitude < -12.0 or value.longitude > 4.0:
            raise ValueError("""Invalid spatial reference. Longitude must be
                             roughly between -12 and 4.""")

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
        transformer = Transformer.from_crs(self._srid, sref_class._srid)
        e, n = transformer.transform(self.latitude, self.longitude)

        # Instantiate an object of the grid ref class with the calculated
        # values and get the grid reference.
        sref = Sref(
            srid=sref_class._srid,
            accuracy=self.accuracy,
            easting=int(e),
            northing=int(n)
        )
        sref_instance = sref_class(sref)
        return sref_instance.gridref
