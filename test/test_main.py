from app.main import settings


class TestSettings:
    def test_settings(self):
        assert settings.indicia_url == "http://localhost:8080"
