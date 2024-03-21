import pytest

from app.validate.srefs.ie_grid import IeGrid


class TestCiGrid:

    def test_2_figures(self):
        g = IeGrid('C 1 6')
        assert g.sref == 'C16'

    def test_4_figures(self):
        g = IeGrid('C 12 67')
        assert g.sref == 'C1267'

    def test_6_figures(self):
        g = IeGrid('C 123 678')
        assert g.sref == 'C123678'

    def test_8_figures(self):
        g = IeGrid('C 1234 6789')
        assert g.sref == 'C12346789'

    def test_10_figures(self):
        g = IeGrid('C 12345 67890')
        assert g.sref == 'C1234567890'

    def test_dinty(self):
        g = IeGrid('C 16A')
        assert g.sref == 'C16A'

    def test_value_error(self):
        with pytest.raises(ValueError):
            IeGrid('C123')
