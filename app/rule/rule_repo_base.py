import datetime
import os

from sqlmodel import Session

from app.settings_env import EnvSettings


class RuleRepoBase:

    def __init__(self, db: Session, env: EnvSettings):
        self.db = db
        self.env = env

    def file_updated(self, dir: str, file: str | None = None):
        if file is None:
            file = self.default_file

        path = f'{dir}/{file}'
        if os.path.exists(path):
            return (
                datetime.datetime.fromtimestamp(os.path.getmtime(path))
                .strftime('%Y-%m-%d %H:%M:%S')
            )
        else:
            return None
