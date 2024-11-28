import pytest

from app.utility.sref import Sref, SrefSystem
from app.utility.sref.gb_grid import GbGrid


class TestGbGrid:

    def test_2_figures(self):
        sref = Sref(gridref='TL 1 6', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL16'

    def test_4_figures(self):
        sref = Sref(gridref='TL 12 67', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL1267'

    def test_6_figures(self):
        sref = Sref(gridref='TL 123 678', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL123678'

    def test_8_figures(self):
        sref = Sref(gridref='TL 1234 6789', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL12346789'

    def test_10_figures(self):
        sref = Sref(gridref='TL 12345 67890', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL1234567890'

    def test_dinty(self):
        sref = Sref(gridref='TL 16A', srid=SrefSystem.GB_GRID)
        g = GbGrid(sref)
        assert g.gridref == 'TL16A'

    def test_value_error(self):
        sref = Sref(gridref='TL 123', srid=SrefSystem.GB_GRID)
        with pytest.raises(ValueError):
            GbGrid(sref)

    def test_e_n_valid(self):
        sref = Sref(
            easting=123456,
            northing=678900,
            accuracy=1,
            srid=SrefSystem.GB_GRID
        )
        g = GbGrid(sref)
        assert g.gridref == 'NR2345678900'

    def test_e_n_no_accuracy(self):
        sref = Sref(
            easting=123456,
            northing=678900,
            srid=SrefSystem.GB_GRID
        )
        with pytest.raises(ValueError):
            GbGrid(sref)

    def test_e_n_too_north(self):
        sref = Sref(
            easting=123456,
            northing=5678900,
            accuracy=1,
            srid=SrefSystem.GB_GRID
        )
        with pytest.raises(ValueError):
            GbGrid(sref)

    def test_e_n_too_east(self):
        sref = Sref(
            easting=1234567,
            northing=678900,
            accuracy=1,
            srid=SrefSystem.GB_GRID
        )
        with pytest.raises(ValueError):
            GbGrid(sref)
