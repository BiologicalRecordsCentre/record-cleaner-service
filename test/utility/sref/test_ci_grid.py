import pytest

from app.utility.sref import Sref, SrefSystem
from app.utility.sref.ci_grid import CiGrid


class TestCiGrid:

    def test_2_figures(self):
        sref = Sref(gridref='WV 1 6', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV16'

    def test_4_figures(self):
        sref = Sref(gridref='WV 12 67', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV1267'

    def test_6_figures(self):
        sref = Sref(gridref='WV 123 678', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV123678'

    def test_8_figures(self):
        sref = Sref(gridref='WV 1234 6789', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV12346789'

    def test_10_figures(self):
        sref = Sref(gridref='WV 12345 67890', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV1234567890'

    def test_dinty(self):
        sref = Sref(gridref='WV 16A', srid=SrefSystem.CI_GRID)
        g = CiGrid(sref)
        assert g.gridref == 'WV16A'

    def test_value_error(self):
        sref = Sref(gridref='WV 123', srid=SrefSystem.CI_GRID)
        with pytest.raises(ValueError):
            CiGrid(sref)

    def test_e_n_valid(self):
        sref = Sref(
            easting=567890,
            northing=5412345,
            accuracy=1,
            srid=SrefSystem.CI_GRID
        )
        g = CiGrid(sref)
        assert g.gridref == 'WV6789012345'

    def test_e_n_no_accuracy(self):
        sref = Sref(
            easting=567890,
            northing=5412345,
            srid=SrefSystem.CI_GRID
        )
        with pytest.raises(ValueError):
            CiGrid(sref)

    def test_e_n_too_north(self):
        sref = Sref(
            easting=567890,
            northing=6200001,
            accuracy=1,
            srid=SrefSystem.CI_GRID
        )
        with pytest.raises(ValueError):
            CiGrid(sref)

    def test_e_n_too_south(self):
        sref = Sref(
            easting=567890,
            northing=5299999,
            accuracy=1,
            srid=SrefSystem.CI_GRID
        )
        with pytest.raises(ValueError):
            CiGrid(sref)

    def test_e_n_too_east(self):
        sref = Sref(
            easting=900001,
            northing=5412345,
            accuracy=1,
            srid=SrefSystem.CI_GRID
        )
        with pytest.raises(ValueError):
            CiGrid(sref)

    def test_e_n_too_west(self):
        sref = Sref(
            easting=99999,
            northing=5412345,
            accuracy=1,
            srid=SrefSystem.CI_GRID
        )
        with pytest.raises(ValueError):
            CiGrid(sref)
