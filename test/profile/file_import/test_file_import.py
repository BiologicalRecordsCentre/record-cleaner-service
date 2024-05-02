import cProfile
import json
import os
import pstats
import pytest
from collections.abc import Generator

from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

import app.rule.rule_repo as repo


# @pytest.fixture(name="session")
# def session_fixture() -> Generator[Session, None, None]:
#     """Fixture which creates an in-memory SQLite database for testing."""

#     engine = create_engine(
#         "sqlite://",
#         connect_args={"check_same_thread": False},
#         poolclass=StaticPool
#     )
#     SQLModel.metadata.create_all(engine)

#     with Session(engine) as session:
#         yield session


class TestFileImport:

    def test_file_import(self, session: Session):

        rule_repo = repo.RuleRepo(session)

        basedir = os.path.abspath(os.path.dirname(__file__))
        rule_repo.rulesdir = os.path.join(basedir, 'testdata')
        rule_repo.rules_commit = 'abc123'
        rule_repo.loading_time = '2024-04-29 17:19:00'

        with cProfile.Profile() as pr:
            rule_repo.db_update(full=True)
            pr.dump_stats('test/profile/file_import/results/output.prof')
