import pytest

from app.utilities.srefs import Sref, SrefSystem
from app.utilities.srefs.gb_grid import GbGrid


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
