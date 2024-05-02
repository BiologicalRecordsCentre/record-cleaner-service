import pytest

from app.utility.sref import Sref, SrefSystem
from app.utility.sref.ie_grid import IeGrid


class TestIeGrid:

    def test_2_figures(self):
        sref = Sref(gridref='C 1 6', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C16'

    def test_4_figures(self):
        sref = Sref(gridref='C 12 67', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C1267'

    def test_6_figures(self):
        sref = Sref(gridref='C 123 678', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C123678'

    def test_8_figures(self):
        sref = Sref(gridref='C 1234 6789', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C12346789'

    def test_10_figures(self):
        sref = Sref(gridref='C 12345 67890', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C1234567890'

    def test_dinty(self):
        sref = Sref(gridref='C 16A', srid=SrefSystem.IE_GRID)
        g = IeGrid(sref)
        assert g.gridref == 'C16A'

    def test_value_error(self):
        sref = Sref(gridref='C 123', srid=SrefSystem.IE_GRID)
        with pytest.raises(ValueError):
            IeGrid(sref)
