import os

from sqlmodel import create_engine, SQLModel

# Why doesn't relative path work?
# sqlite_file_name = "data/database.db"


basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_file_name = f"{basedir}/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Import this engine everywhere we want to use the database
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
