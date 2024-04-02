import pytest

from app.utilities.srefs.ci_grid import CiGrid


class TestCiGrid:

    def test_2_figures(self):
        g = CiGrid('WV 1 6')
        assert g.sref == 'WV16'

    def test_4_figures(self):
        g = CiGrid('WV 12 67')
        assert g.sref == 'WV1267'

    def test_6_figures(self):
        g = CiGrid('WV 123 678')
        assert g.sref == 'WV123678'

    def test_8_figures(self):
        g = CiGrid('WV 1234 6789')
        assert g.sref == 'WV12346789'

    def test_10_figures(self):
        g = CiGrid('WV 12345 67890')
        assert g.sref == 'WV1234567890'

    def test_dinty(self):
        g = CiGrid('WV 16A')
        assert g.sref == 'WV16A'

    def test_value_error(self):
        with pytest.raises(ValueError):
            CiGrid('WV 123')
