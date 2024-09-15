from typing import TypeAlias, Annotated

from fastapi import Request, Depends

from app.settings_env import get_env_settings
from app.settings_db import DbSettings


class Settings():
    def __init__(self, engine):
        self.env = get_env_settings()
        self.db = DbSettings(engine)


def get_settings(request: Request) -> Settings:
    """A function for injecting settings as a dependency."""
    return request.state.settings


# Create a type alias for brevity when defining an endpoint needing settings.
SettingsDependency: TypeAlias = Annotated[Settings, Depends(get_settings)]
