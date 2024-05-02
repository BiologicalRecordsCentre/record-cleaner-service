import pytest
from datetime import datetime, timedelta

from app.utility.vague_date import VagueDate


class TestVagueDates:
    def test_yyyy_mm_dd_hyphen(self):
        v = VagueDate('2024-03-20')
        assert str(v) == '20/03/2024'

    def test_dd_mm_yyyy_slash(self):
        v = VagueDate('20/03/2024')
        assert str(v) == '20/03/2024'

    def test_d_m_yyyy_slash(self):
        v = VagueDate('2/3/2024')
        assert str(v) == '02/03/2024'

    def test_dd_mm_yy_slash(self):
        v = VagueDate('20/03/24')
        assert str(v) == '20/03/2024'

    def test_d_m_yy_slash(self):
        v = VagueDate('2/3/24')
        assert str(v) == '02/03/2024'

    def test_dd_mm_yyyy_dot(self):
        v = VagueDate('20.03.2024')
        assert str(v) == '20/03/2024'

    def test_d_m_yyyy_dot(self):
        v = VagueDate('2.3.2024')
        assert str(v) == '02/03/2024'

    def test_dd_mm_yy_dot(self):
        v = VagueDate('20.03.24')
        assert str(v) == '20/03/2024'

    def test_d_m_yy_dot(self):
        v = VagueDate('2.3.24')
        assert str(v) == '02/03/2024'

    def test_dd_month_yyyy(self):
        v = VagueDate('20 March 2024')
        assert str(v) == '20/03/2024'

    def test_d_month_yyyy(self):
        v = VagueDate('2 March 2024')
        assert str(v) == '02/03/2024'

    def test_dd_mon_yyyy(self):
        v = VagueDate('20 Mar 2024')
        assert str(v) == '20/03/2024'

    def test_d_mon_yyyy(self):
        v = VagueDate('2 Mar 2024')
        assert str(v) == '02/03/2024'

    def test_dd_month_yy(self):
        v = VagueDate('20 March 24')
        assert str(v) == '20/03/2024'

    def test_d_month_yy(self):
        v = VagueDate('2 March 24')
        assert str(v) == '02/03/2024'

    def test_dd_mon_yy(self):
        v = VagueDate('20 Mar 24')
        assert str(v) == '20/03/2024'

    def test_d_mon_yy(self):
        v = VagueDate('2 Mar 24')
        assert str(v) == '02/03/2024'

    def test_yyyy_mm_hyphen(self):
        v = VagueDate('2024-03')
        assert str(v) == '03/2024'

    def test_mm_yyyy_slash(self):
        v = VagueDate('03/2024')
        assert str(v) == '03/2024'

    def test_m_yyyy_slash(self):
        v = VagueDate('3/2024')
        assert str(v) == '03/2024'

    def test_mmyy_slash(self):
        v = VagueDate('03/24')
        assert str(v) == '03/2024'

    def test_myy_slash(self):
        v = VagueDate('3/24')
        assert str(v) == '03/2024'

    def test_mm_yyyy_dot(self):
        v = VagueDate('03.2024')
        assert str(v) == '03/2024'

    def test_m_yyyy_dot(self):
        v = VagueDate('3.2024')
        assert str(v) == '03/2024'

    def test_mm_yy_dot(self):
        v = VagueDate('03.24')
        assert str(v) == '03/2024'

    def test_m_yy_dot(self):
        v = VagueDate('3.24')
        assert str(v) == '03/2024'

    def test_month_yyyy(self):
        v = VagueDate('March 2024')
        assert str(v) == '03/2024'

    def test_mon_yyyy(self):
        v = VagueDate('Mar 2024')
        assert str(v) == '03/2024'

    def test_month_yy(self):
        v = VagueDate('March 24')
        assert str(v) == '03/2024'

    def test_mon_yy(self):
        v = VagueDate('Mar 24')
        assert str(v) == '03/2024'

    def test_yyyy(self):
        v = VagueDate('2023')
        assert str(v) == '2023'

    def test_yy(self):
        v = VagueDate('23')
        assert str(v) == '2023'

    def test_day_range_iso(self):
        v = VagueDate('2024-03-02 - 2024-03-20')
        assert str(v) == '02/03/2024 - 20/03/2024'

    def test_day_range_whole(self):
        v = VagueDate('2/3/2024-20/3/24')
        assert str(v) == '02/03/2024 - 20/03/2024'

    def test_day_range_partial_month(self):
        v = VagueDate('2/2-20/3/2024')
        assert str(v) == '02/02/2024 - 20/03/2024'

    def test_day_range_partial_day(self):
        v = VagueDate('2-20/03/24')
        assert str(v) == '02/03/2024 - 20/03/2024'

    def test_month_range_iso(self):
        v = VagueDate('2024-03 - 2024-03')
        assert str(v) == '03/2024 - 03/2024'

    def test_month_range_whole(self):
        v = VagueDate('2/2024-3/2024')
        assert str(v) == '02/2024 - 03/2024'

    def test_month_range_partial(self):
        v = VagueDate('2-3/2024')
        assert str(v) == '02/2024 - 03/2024'

    def test_year_range_iso(self):
        v = VagueDate('2022 - 2023')
        assert str(v) == '2022 - 2023'

    def test_year_range_whole(self):
        v = VagueDate('2022-2023')
        assert str(v) == '2022 - 2023'

    def test_day_range_error(self):
        with pytest.raises(ValueError):
            VagueDate('20-2/3/24')

    def test_month_range_error(self):
        with pytest.raises(ValueError):
            VagueDate('3-2/24')

    def test_year_range_error(self):
        with pytest.raises(ValueError):
            VagueDate('24-23')

    def test_today(self):
        today = datetime.strftime(datetime.today(), '%d/%m/%Y')
        v = VagueDate(today)
        assert str(v) == today

    def test_tomorrow(self):
        tomorrow = datetime.strftime(
            datetime.today() + timedelta(days=1), '%d/%m/%Y')
        with pytest.raises(ValueError):
            VagueDate(tomorrow)
