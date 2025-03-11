from logging.config import fileConfig
import logging
import os

from app import sqlmodels
from app.settings_env import get_env_settings

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

from alembic import context

logger = logging.getLogger('alembic')

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    logger.info("Running migrations offline.")
    url = get_sqlalchemy_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    logger.info("Running migrations online.")
    connectable = engine_from_config(
        {'sqlalchemy.url': get_sqlalchemy_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def get_sqlalchemy_url():
    """Get the SQLAlchemy URL for the database.

    The SQLite file is called `database.sqlite` and it is located in the `data`
    subdirectory of the DATA_DIR location set in the environment.
    """
    env = get_env_settings()
    basedir = env.data_dir
    if basedir[0] == '.':
        # Determine absolute path from relative path setting.
        # Relative paths are with respect to the app directory.
        alembic_dir = os.path.abspath(os.path.dirname(__file__))
        app_dir = os.path.join(os.path.dirname(alembic_dir), 'app')
        basedir = os.path.join(app_dir, basedir[1:])

    datadir = os.path.join(basedir, 'data')
    sqlite_file_path = os.path.join(datadir, 'database.sqlite')
    url = f"sqlite:///{sqlite_file_path}"

    logger.info(f"Database URL: {url}")
    return f"sqlite:///{sqlite_file_path}"


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
