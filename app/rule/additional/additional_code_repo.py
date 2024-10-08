import pandas as pd

from sqlmodel import select

from app.sqlmodels import AdditionalCode

from ..rule_repo_base import RuleRepoBase


class AdditionalCodeRepo(RuleRepoBase):
    default_file = 'additional_codes.csv'

    def list(self, org_group_id: int):
        results = self.db.exec(
            select(AdditionalCode)
            .where(AdditionalCode.org_group_id == org_group_id)
            .order_by(AdditionalCode.code)
        ).all()

        codes = []
        for additional_code in results:
            codes.append({
                'code': additional_code.code,
                'text': additional_code.text
            })

        return codes

    def get_or_create(self, org_group_id: int, code: int):
        """Get existing record or create a new one."""
        additional_code = self.db.exec(
            select(AdditionalCode)
            .where(AdditionalCode.org_group_id == org_group_id)
            .where(AdditionalCode.code == code)
        ).one_or_none()

        if additional_code is None:
            # Create new.
            additional_code = AdditionalCode(
                org_group_id=org_group_id,
                code=code
            )

        return additional_code

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        additional_codes = self.db.exec(
            select(AdditionalCode)
            .where(AdditionalCode.org_group_id == org_group_id)
            .where(AdditionalCode.commit != rules_commit)
        )
        for row in additional_codes:
            self.db.delete(row)
        self.db.commit()

    def get_code_lookup(self, org_group_id: int) -> {}:
        """Return a look up from code to code_id"""
        additional_codes = self.db.exec(
            select(AdditionalCode)
            .where(AdditionalCode.org_group_id == org_group_id)
        )

        code_lookup = {}
        for additional_code in additional_codes:
            code_lookup[additional_code.code] = additional_code.id

        return code_lookup

    def load_file(
            self, dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read a additional_codes file and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the additional codes file into a dataframe.
        codes = pd.read_csv(
            f'{dir}/{file}', dtype={'code': int, 'text': str}
        )

        # Add the rule to the db.
        for row in codes.to_dict('records'):
            additional_code = self.get_or_create(org_group_id, row['code'])
            additional_code.text = row['text'].strip()
            additional_code.commit = rules_commit
            self.db.add(additional_code)

        # Save all the changes.
        self.db.commit()
        # Delete orphan AdditionalCodes.
        self.purge(org_group_id, rules_commit)

        return errors
