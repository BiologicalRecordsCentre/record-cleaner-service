import pytest

from app.utility.vice_county.vc_checker import VcChecker


class TestVcChecker:

    VcChecker.load_data()

    def test_valid_gb_code_int(self):
        assert VcChecker.prepare_code(1) == '1'

    def test_valid_gb_code_str(self):
        assert VcChecker.prepare_code('1') == '1'

    def test_invalid_gb_code_0(self):
        with pytest.raises(ValueError):
            VcChecker.prepare_code('0')

    def test_invalid_gb_code_113(self):
        with pytest.raises(ValueError):
            VcChecker.prepare_code('113')

    def test_valid_ie_code(self):
        assert VcChecker.prepare_code('h 1') == 'H1'

    def test_invalid_ie_code_0(self):
        with pytest.raises(ValueError):
            VcChecker.prepare_code('H0')

    def test_invalid_ie_code_41(self):
        with pytest.raises(ValueError):
            VcChecker.prepare_code('H41')

    def test_valid_name(self):
        assert VcChecker.prepare_code('West Lancashire') == '60'

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            VcChecker.prepare_code('West Lancaster')

    def test_valid_10k_sref(self):
        assert VcChecker.prepare_sref('HP30') == 'HP30'

    def test_valid_2k_sref(self):
        assert VcChecker.prepare_sref('HP30K') == 'HP30K'

    def test_valid_1k_sref(self):
        assert VcChecker.prepare_sref('HP3602') == 'HP3602'

    def test_valid_100m_sref(self):
        assert VcChecker.prepare_sref('HP367023') == 'HP3602'

    def test_valid_10m_sref(self):
        assert VcChecker.prepare_sref('HP36780234') == 'HP3602'

    def test_valid_1m_sref(self):
        assert VcChecker.prepare_sref('HP3678902345') == 'HP3602'

    def test_valid_10k_check(self):
        assert VcChecker.check('HP30', '112') is None

    def test_valid_2k_check(self):
        assert VcChecker.check('HP30K', '112') is None

    def test_valid_1k_check(self):
        assert VcChecker.check('HP3602', '112') is None

    def test_valid_dom_check(self):
        assert VcChecker.check('NB91', '105') is None

    def test_valid_sub_check(self):
        assert VcChecker.check('NB91', '108') is None

    def test_invalid_check(self):
        with pytest.raises(ValueError):
            VcChecker.check('HP3602', '1')
