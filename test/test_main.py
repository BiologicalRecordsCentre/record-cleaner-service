from app.main import settings


class TestSettings:
    def test_settings(self):
        assert settings.env.indicia_url == "http://localhost:8080/index.php/services/rest/"
