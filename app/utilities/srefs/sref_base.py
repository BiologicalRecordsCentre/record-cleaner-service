from . import Sref, SrefSystem, SrefCountry


class SrefBase:

    _value: Sref = None

    def __init__(self):
        pass

    @property
    def value(self) -> Sref:
        return self._value

    @property
    def srid(self) -> int:
        return self._srid

    @property
    def gridref(self) -> str:
        if self._value.gridref is None:
            self.calculate_gridref()
        return self._value.gridref

    @property
    def country(self) -> str:
        if self._value.country is None:
            self.calculate_country()

    def calculate_country(self):
        """Determines the country based on the latitude and longitude."""
        if (self.latitude > 48.8 and self.latitude < 50.0 and
                self.longitude > -3.1 and self.longitude < -1.8):
            self._value.country = SrefCountry.CI
        elif ((
                self.latitude > 51.3 and self.latitude < 55.5 and
                self.longitude > -10.8 and self.longitude < -5.9)
                or (
                self.latitude > 54.0 and self.latitude < 55.1 and
                self.longitude >= -5.9 and self.longitude < -5.3)
              ):
            self._value.country = SrefCountry.IE
        else:
            self._value.country = SrefCountry.GB
