import pytest

from app.checks.srefs.gb_grid import GbGrid


class TestGbGrid:

    def test_2_figures(self):
        g = GbGrid('TL 1 6')
        assert g.sref == 'TL16'

    def test_4_figures(self):
        g = GbGrid('TL 12 67')
        assert g.sref == 'TL1267'

    def test_6_figures(self):
        g = GbGrid('TL 123 678')
        assert g.sref == 'TL123678'

    def test_8_figures(self):
        g = GbGrid('TL 1234 6789')
        assert g.sref == 'TL12346789'

    def test_10_figures(self):
        g = GbGrid('TL 12345 67890')
        assert g.sref == 'TL1234567890'

    def test_dinty(self):
        g = GbGrid('TL 16A')
        assert g.sref == 'TL16A'

    def test_value_error(self):
        with pytest.raises(ValueError):
            GbGrid('TL 123')
