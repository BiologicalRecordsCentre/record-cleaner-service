import pytest

from app.utilities.srefs import Sref, SrefSystem, SrefCountry
from app.utilities.srefs.wgs84 import Wgs84


class TestWgs84:

    def test_okay_britain(self):
        sref = Sref(latitude=54, longitude=-2, srid=SrefSystem.WGS84)
        g = Wgs84(sref)
        assert g.country == SrefCountry.GB
        assert g.gridref == 'SE0055'

    def test_okay_ireland(self):
        sref = Sref(latitude=53, longitude=-8, srid=SrefSystem.WGS84)
        g = Wgs84(sref)
        assert g.country == SrefCountry.IE
        assert g.gridref == 'S0094'

    def test_okay_channel_islands(self):
        sref = Sref(latitude=49.5, longitude=-2.5, srid=SrefSystem.WGS84)
        g = Wgs84(sref)
        assert g.country == SrefCountry.CI
        assert g.gridref == 'WV3683'

    def test_latitude_error(self):
        with pytest.raises(ValueError):
            sref = Sref(latitude=34, longitude=-2, srid=SrefSystem.WGS84)
            Wgs84(sref)

    def test_longitude_error(self):
        with pytest.raises(ValueError):
            sref = Sref(latitude=54, longitude=-20, srid=SrefSystem.WGS84)
            Wgs84(sref)
