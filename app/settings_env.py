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

    # Making the settings frozen means they are hashable.
    # https://github.com/fastapi/fastapi/issues/1985#issuecomment-1290899088
    model_config = SettingsConfigDict(env_file=".env", frozen=True)


@lru_cache
def get_env_settings():
    # A cached function keeping settings in memory.
    env = EnvSettings()
    return env


# Create a type alias for brevity when defining an endpoint needing env
# settings.
EnvDependency: TypeAlias = Annotated[EnvSettings, Depends(
    get_env_settings)]
