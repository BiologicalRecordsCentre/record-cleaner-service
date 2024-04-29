import pandas as pd

from sqlmodel import select

from app.sqlmodels import DifficultyCode

from ..rule_repo_base import RuleRepoBase


class DifficultyCodeRepo(RuleRepoBase):
    default_file = 'difficulty_codes.csv'

    def list(self, org_group_id: int):
        results = self.session.exec(
            select(DifficultyCode)
            .where(DifficultyCode.org_group_id == org_group_id)
            .order_by(DifficultyCode.code)
        ).all()

        codes = []
        for difficulty_code in results:
            codes.append({
                'difficulty': difficulty_code.code,
                'text': difficulty_code.text
            })

        return codes

    def get_or_create(self, org_group_id: int, code: int):
        """Get existing record or create a new one."""
        difficulty_code = self.session.exec(
            select(DifficultyCode)
            .where(DifficultyCode.org_group_id == org_group_id)
            .where(DifficultyCode.code == code)
        ).one_or_none()

        if difficulty_code is None:
            # Create new.
            difficulty_code = DifficultyCode(
                org_group_id=org_group_id,
                code=code
            )

        return difficulty_code

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        difficulty_codes = self.session.exec(
            select(DifficultyCode)
            .where(DifficultyCode.org_group_id == org_group_id)
            .where(DifficultyCode.commit != rules_commit)
        )
        for row in difficulty_codes:
            self.session.delete(row)
        self.session.commit()

    def get_code_lookup(self, org_group_id: int) -> {}:
        """Return a look up from code to code_id"""
        difficulty_codes = self.session.exec(
            select(DifficultyCode)
            .where(DifficultyCode.org_group_id == org_group_id)
        )

        code_lookup = {}
        for difficulty_code in difficulty_codes:
            code_lookup[difficulty_code.code] = difficulty_code.id

        return code_lookup

    def load_file(
            self, dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read a difficulty_codes file and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the difficulty codes file into a dataframe.
        codes = pd.read_csv(
            f'{dir}/{file}'
        )

        # Save the difficulty codes in the database.
        for row in codes.to_dict('records'):
            difficulty_code = self.get_or_create(org_group_id, row['code'])
            difficulty_code.text = row['text'].strip()
            difficulty_code.commit = rules_commit
            self.session.add(difficulty_code)
            self.session.commit()

        # Delete orphan DifficultyCodes.
        self.purge(org_group_id, rules_commit)

        return errors
