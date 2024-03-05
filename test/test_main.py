import app.main as main


class TestSettings:
    def test_get_settings(self):
        settings = main.get_settings()
        assert settings.indicia_url == "http://localhost:8080"
