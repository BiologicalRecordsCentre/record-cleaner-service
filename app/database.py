import os

from sqlmodel import create_engine, SQLModel

import app.models

basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_file_name = f"{basedir}/data/database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Import this engine everywhere we want to use the database
engine = create_engine(sqlite_url, echo=True)

# Create tables if they don't exist.
SQLModel.metadata.create_all(engine)
