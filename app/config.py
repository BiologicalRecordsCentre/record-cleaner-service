from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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


# @lru_cache
def get_settings():
    return Settings()
