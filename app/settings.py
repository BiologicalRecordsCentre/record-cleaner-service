from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import Session, select

from app.database import engine
from app.models import System


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

    model_config = SettingsConfigDict(env_file=".env")


class DbSetting:
    """A descriptor for database settings."""

    def __init__(self, default):
        self.default = default

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
                    value = response.value
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
    rules_commmit = DbSetting('')


class Settings():
    def __init__(self):
        self.env = EnvSettings()
        self.db = DbSettings()


# Import this and use wherever we need it.
settings = Settings()
