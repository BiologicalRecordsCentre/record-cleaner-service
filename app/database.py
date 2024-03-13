from sqlmodel import create_engine, SQLModel

import app.models as models

# Why doesn't relative path work?
# sqlite_file_name = "data/database.db"
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Import this engine everywhere we want to use the database
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
