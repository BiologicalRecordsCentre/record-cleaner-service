from functools import lru_cache
from typing import TypeAlias, Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    data_dir: str = '.'
    backup_dir: str = ''
    log_level: str = 'WARNING'

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_env_settings():
    # A cached function keeping settings in memory.
    return EnvSettings()


# Create a type alias for brevity when defining an endpoint needing env
# settings.
EnvDependency: TypeAlias = Annotated[EnvSettings, Depends(
    get_env_settings)]
