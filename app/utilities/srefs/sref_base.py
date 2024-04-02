from . import Sref, SrefCountry, SrefAccuracy


class SrefBase:
    """Base class for spatial reference classes."""

    @property
    def value(self) -> Sref:
        return self.__value

    @value.setter
    def value(self, value: Sref):
        self.validate(value)
        self.__value = value

    @property
    def gridref(self) -> str:
        """Gets a grid reference, either that entered or calculated."""
        if self.__value.gridref is None:
            self.__value.gridref = self.calculate_gridref()
        return self.__value.gridref

    @property
    def country(self) -> str:
        """Gets the country, inferred from the grid reference supplied or
        roughly determined from bounding boxes."""
        if self.__value.country is None:
            self.calculate_country()
        return self.__value.country

    @property
    def accuracy(self) -> SrefAccuracy:
        return self.__value.accuracy

    @property
    def latitude(self) -> float:
        return self.__value.latitude

    @property
    def longitude(self) -> float:
        return self.__value.longitude

    @property
    def easting(self) -> int:
        return self.__value.easting

    @property
    def northing(self) -> int:
        return self.__value.northing

    def calculate_country(self):
        """Determines the country based on the latitude and longitude."""
        lat = self.latitude
        lon = self.longitude
        if (lat > 48.8 and lat < 50.0 and lon > -3.1 and lon < -1.8):
            self.__value.country = SrefCountry.CI
        elif (
            (lat > 51.3 and lat < 55.5 and lon > -10.8 and lon < -5.9)
            or
            (lat > 54.0 and lat < 55.1 and lon >= -5.9 and lon < -5.3)
        ):
            self.__value.country = SrefCountry.IE
        elif (
            (lat > 49.8 and lat < 62.0 and lon > -10.0 and lon < 4.0)
        ):
            self.__value.country = SrefCountry.GB
        else:
            raise ValueError("""Invalid spatial reference. Could not assign
                             location to a country.""")
