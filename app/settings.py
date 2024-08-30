from typing import TypeAlias, Annotated

from fastapi import Depends

from app.settings_env import get_env_settings
from app.settings_db import DbSettings


class Settings():
    def __init__(self):
        self.env = get_env_settings()
        self.db = DbSettings()


# Import this and use wherever we need it.
settings = Settings()


def get_settings() -> Settings:
    """A function for injecting settings as a dependency."""
    return settings


# Create a type alias for brevity when defining an endpoint needing settings.
Config: TypeAlias = Annotated[Settings, Depends(get_settings)]
