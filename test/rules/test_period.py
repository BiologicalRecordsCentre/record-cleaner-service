import app.rules.period as period


class TestInPeriod:
    def test_dateOk(self):
        assert period.inPeriod("2022-08-01", 1) is True

    def test_dateBad(self):
        assert period.inPeriod("2022-01-01", 1) is False
