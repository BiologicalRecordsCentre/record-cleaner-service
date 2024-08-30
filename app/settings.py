from functools import lru_cache
from typing import TypeAlias, Annotated


from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import Session, select

from app.database import engine
from app.sqlmodels import System


class EnvSettings(BaseSettings):
    jwt_key: str
    jwt_algorithm: str
    jwt_expires_minutes: int
    indicia_url: str
    indicia_rest_user: str
    indicia_rest_password: str
    indicia_taxon_list_id: int
    rules_repo: str
    rules_branch: str
    rules_dir: str
    rules_subdir: str
    initial_user_name: str
    initial_user_pass: str
    environment: str = 'prod'  # ['dev'|'test'|'prod']

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_env_settings():
    # A cached function keeping settings in memory.
    return EnvSettings()


class DbSetting:
    """A descriptor for database settings."""

    def __init__(self, default):
        # A default value to use if the setting is not yet in the database.
        self.default = default
        # A function to convert from database storage back to python type.
        if type(default) is bool:
            self.convert = lambda x: bool(int(x))
        elif type(default) is int:
            self.convert = lambda x: int(x)
        else:
            self.convert = lambda x: str(x)

    def __set_name__(self, owner, name):
        self.name = name
        self.obj_name = '_' + name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.obj_name, None)
        if value is None:
            with Session(engine) as session:
                response = session.exec(
                    select(System)
                    .where(System.key == self.name)
                ).one_or_none()
                if response is None:
                    value = self.default
                else:
                    value = self.convert(response.value)

            setattr(obj, self.obj_name, value)
        return value

    def __set__(self, obj, value):
        setattr(obj, self.obj_name, value)
        with Session(engine) as session:
            response = session.exec(
                select(System)
                .where(System.key == self.name)
            ).one_or_none()
            if response is None:
                # Insert.
                session.add(System(key=self.name, value=value))
            else:
                # Update.
                response.value = value
                session.add(response)
            session.commit()


class DbSettings:
    maintenance_mode = DbSetting(False)
    maintenance_message = DbSetting('Normal operation.')
    rules_commit = DbSetting('')
    rules_updating = DbSetting(False)
    rules_update_result = DbSetting(
        '{"ok": true, "data": "Rules not yet updated."}')

    def list(self):
        """List all database settings."""
        result = {}
        # Loop through vars of DbSettings Class to find descriptors
        for name, var in vars(DbSettings).items():
            if isinstance(var, DbSetting):
                result[name] = getattr(self, name)

        return result


class Settings():
    def __init__(self):
        self.env = get_env_settings()
        self.db = DbSettings()


# Import this and use wherever we need it.
settings = Settings()


def get_settings() -> Settings:
    """A function for injecting settings as a dependency."""
    return settings


# Create a type alias for brevity when defining an endpoint needing
# a database session.
Config: TypeAlias = Annotated[Settings, Depends(get_settings)]
