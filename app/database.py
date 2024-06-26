from collections.abc import Generator
import os
from typing import TypeAlias, Annotated

from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

# Importing all the sqlmodels ensures the tables are created in the database
import app.sqlmodels as sqlmodels

basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_file_name = f"{basedir}/data/database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Import this engine everywhere we want to use the database
engine = create_engine(sqlite_url, echo=True)

# Create tables if they don't exist.
SQLModel.metadata.create_all(engine)


def get_db_session() -> Generator[Session, None, None]:
    """A function for injecting a session as a dependency."""
    with Session(engine) as session:
        yield session


# Create a type alias for brevity when defining an endpoint needing
# a database session.
DB: TypeAlias = Annotated[Session, Depends(get_db_session)]
