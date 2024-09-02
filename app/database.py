from collections.abc import Generator
import os
from typing import TypeAlias, Annotated

from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

# Importing all the sqlmodels ensures the tables are created in the database
import app.sqlmodels as sqlmodels
from app.settings_env import get_env_settings

env_settings = get_env_settings()

# Locate the directory for the database.
basedir = env_settings.data_dir
if basedir[0] == '.':
    # Determine absolute path from relative path setting.
    current_dir = os.path.abspath(os.path.dirname(__file__))
    basedir = os.path.join(current_dir, basedir[1:])

datadir = os.path.join(basedir, 'data')
if not os.path.exists(datadir):
    os.mkdir(datadir)
sqlite_file_name = f"{datadir}/database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Import this engine everywhere we want to use the database
if env_settings.environment == 'dev':
    engine = create_engine(sqlite_url, echo=True)
else:
    engine = create_engine(sqlite_url)

# Create tables if they don't exist.
SQLModel.metadata.create_all(engine)


def get_db_session() -> Generator[Session, None, None]:
    """A function for injecting a session as a dependency."""
    with Session(engine) as session:
        yield session


# Create a type alias for brevity when defining an endpoint needing
# a database session.
DB: TypeAlias = Annotated[Session, Depends(get_db_session)]
