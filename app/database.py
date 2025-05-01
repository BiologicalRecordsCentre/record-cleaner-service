from collections.abc import Generator
import logging
import os
import shutil
import sqlite3
from typing import TypeAlias, Annotated

import alembic.command
import alembic.config
import alembic.migration
import alembic.script
from fastapi import Request, Depends, HTTPException, status
from sqlmodel import create_engine, SQLModel, Session

# Importing all the sqlmodels ensures the tables are created in the database
import app.sqlmodels as sqlmodels
from app.settings_env import EnvSettings


logger = logging.getLogger(f"uvicorn.{__name__}")


def create_db(env: EnvSettings):
    # Locate the directory for the database.
    app_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = env.data_dir
    if data_dir[0] == '.':
        # Determine absolute path from relative path setting.
        data_dir = os.path.join(app_dir, data_dir[1:])

    datadir = os.path.join(data_dir, 'data')
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    sqlite_file_path = os.path.join(datadir, 'database.sqlite')

    # Check if the database file exists.
    if not os.path.exists(sqlite_file_path):
        # If not, check if a backup exists.
        backupdir = env.backup_dir
        if backupdir != '':
            sqlite_backup_path = os.path.join(backupdir, 'database.sqlite')
            if os.path.exists(sqlite_backup_path):
                # Copy in the backup.
                shutil.copy(sqlite_backup_path, sqlite_file_path)
                logger.warning('Database restored from backup.')

    sqlite_url = f"sqlite:///{sqlite_file_path}"

    # Import this engine everywhere we want to use the database
    if env.environment == 'dev':
        engine = create_engine(sqlite_url, echo=True)
    else:
        engine = create_engine(sqlite_url, echo=False)

    # Get config for alembic database migrations.
    base_dir = os.path.dirname(app_dir)
    ini_file_path = os.path.join(base_dir, 'alembic.ini')
    cfg = alembic.config.Config(ini_file_path)

    if not os.path.exists(sqlite_file_path):
        # Create tables if they don't exist.
        SQLModel.metadata.create_all(engine)
        # Generate the alembic version table, "stamping" it with the most
        # recent rev
        alembic.command.stamp(cfg, "head")
        logger.info("New database created.")
    else:
        # We run any alembic migrations outside the application as they may be
        # long running. During development, run `alembic upgrade head` at a
        # terminal prompt. In production, this should be automated during
        # deployment.
        dir = alembic.script.ScriptDirectory.from_config(cfg)
        with engine.begin() as connection:
            context = alembic.migration.MigrationContext.configure(connection)
            if set(context.get_current_heads()) != set(dir.get_heads()):
                logger.error("Database is out of sync with code.")
                raise Exception("Database is out of sync with code. "
                                "Please run `alembic upgrade head`.")

    return engine


def get_db_session(request: Request) -> Generator[Session, None, None]:
    """A function for injecting a session as a dependency."""
    with Session(request.state.engine) as session:
        try:
            yield session
        except sqlite3.OperationalError:
            # Probably a database locked error.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service busy. Please try again shortly.")
        except Exception as e:
            # Don't swallow other exceptions.
            raise e


# Create a type alias for brevity when defining an endpoint needing
# a database session.
DbDependency: TypeAlias = Annotated[Session, Depends(get_db_session)]
