from . import Sref, SrefCountry, SrefAccuracy


class SrefBase:
    """Base class for spatial reference classes."""

    def __init__(self, sref: Sref):
        self._value = sref

    @property
    def value(self) -> Sref:
        if self._value.gridref is None:
            self._value.gridref = self.calculate_gridref()
        if self._value.country is None:
            self.calculate_country()
        if self._value.accuracy is None:
            self.calculate_accuracy()
        if self._value.km100 is None:
            self.calculate_km100()
        if self._value.km10 is None:
            self.calculate_km10()

        return self._value

    @property
    def gridref(self) -> str:
        """Gets a grid reference, either that entered or calculated."""
        if self._value.gridref is None:
            self._value.gridref = self.calculate_gridref()
        return self._value.gridref

    @property
    def country(self) -> str:
        """Gets the country, inferred from the grid reference supplied or
        roughly determined from bounding boxes."""
        if self._value.country is None:
            self.calculate_country()
        return self._value.country

    @property
    def accuracy(self) -> SrefAccuracy:
        if self._value.accuracy is None:
            self.calculate_accuracy()
        return self._value.accuracy

    @property
    def latitude(self) -> float:
        return self._value.latitude

    @property
    def longitude(self) -> float:
        return self._value.longitude

    @property
    def easting(self) -> int:
        return self._value.easting

    @property
    def northing(self) -> int:
        return self._value.northing

    @property
    def km100(self) -> str:
        if self._value.km100 is None:
            self.calculate_km100()
        return self._value.km100

    @property
    def km10(self) -> str:
        if self._value.km10 is None:
            self.calculate_km10()
        return self._value.km10

    def calculate_country(self):
        """Determines the country based on the latitude and longitude."""
        lat = self.latitude
        lon = self.longitude
        if (lat > 48.8 and lat < 50.0 and lon > -3.1 and lon < -1.8):
            self._value.country = SrefCountry.CI
        elif (
            (lat > 51.3 and lat < 55.5 and lon > -10.8 and lon < -5.9)
            or
            (lat > 54.0 and lat < 55.1 and lon >= -5.9 and lon < -5.3)
        ):
            self._value.country = SrefCountry.IE
        elif (
            (lat > 49.8 and lat < 62.0 and lon > -10.0 and lon < 4.0)
        ):
            self._value.country = SrefCountry.GB
        else:
            raise ValueError("""Invalid spatial reference. Could not assign
                             location to a country.""")

    def calculate_accuracy(self):
        """Determines the accuracy of a grid reference."""
        match (len(self.gridref) - len(self.km100)):
            case 2:
                accuracy = SrefAccuracy.KM10
            case 3:
                accuracy = SrefAccuracy.KM2
            case 4:
                accuracy = SrefAccuracy.KM1
            case 6:
                accuracy = SrefAccuracy.M100
            case 8:
                accuracy = SrefAccuracy.M10
            case 10:
                accuracy = SrefAccuracy.M1

        self._value.accuracy = accuracy

    def calculate_km100(self):
        """Determines the km100 from the grid reference."""
        match self.country:
            case SrefCountry.GB | SrefCountry.CI:
                km100 = self.gridref[0:2]
            case SrefCountry.IE:
                km100 = self.gridref[0:1]

        self._value.km100 = km100

    def calculate_km10(self):
        """Determines the km10 from the grid reference."""
        match self.country:
            case SrefCountry.GB | SrefCountry.CI:
                eastnorth = self.gridref[2:]
            case SrefCountry.IE:
                eastnorth = self.gridref[1:]

        match self.accuracy:
            case SrefAccuracy.KM10:
                km10 = eastnorth
            case SrefAccuracy.KM2:
                km10 = eastnorth[0:2]
            case SrefAccuracy.KM1:
                km10 = eastnorth[0:1] + eastnorth[2:3]
            case SrefAccuracy.M100:
                km10 = eastnorth[0:1] + eastnorth[3:4]
            case SrefAccuracy.M10:
                km10 = eastnorth[0:1] + eastnorth[4:5]
            case SrefAccuracy.M1:
                km10 = eastnorth[0:1] + eastnorth[5:6]

        self._value.km10 = km10

    def props(self):
        return {
            'srid': self._srid,
            'gridref': self.gridref,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'easting': self.easting,
            'northing': self.northing,
            'accuracy': self.accuracy,
            'country': self.country
        }
