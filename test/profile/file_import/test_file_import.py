import cProfile
import os

from sqlmodel import Session

import app.rule.rule_repo as repo


class TestFileImport:

    def test_file_import(self, db: Session):

        rule_repo = repo.RuleRepo(db)

        basedir = os.path.abspath(os.path.dirname(__file__))
        rule_repo.rulesdir = os.path.join(basedir, 'testdata')
        rule_repo.rules_commit = 'abc123'
        rule_repo.loading_time = '2024-04-29 17:19:00'

        with cProfile.Profile() as pr:
            rule_repo.db_update(full=True)
            pr.dump_stats('test/profile/file_import/results/output.prof')
