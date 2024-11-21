import pandas as pd

from sqlmodel import select

import app.species.cache as cache

from app.sqlmodels import DifficultyCode, DifficultyRule, Taxon, OrgGroup
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase
from .difficulty_code_repo import DifficultyCodeRepo


class DifficultyRuleRepo(RuleRepoBase):
    default_file = 'id_difficulty.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.db.exec(
            select(DifficultyRule, Taxon, DifficultyCode)
            .join(Taxon)
            .join(DifficultyCode)
            .where(DifficultyRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for difficulty_rule, taxon, difficulty_code in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'difficulty': difficulty_code.code
            })

        return rules

    def list_by_tvk(self, tvk: str):
        results = self.db.exec(
            select(DifficultyRule, Taxon, DifficultyCode, OrgGroup)
            .join(Taxon)
            .join(DifficultyCode)
            .join(OrgGroup)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for difficulty_rule, taxon, difficulty_code, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'difficulty': difficulty_code.code,
                'text': difficulty_code.text
            })

        return rules

    def get_or_create(
        self, org_group_id: int, taxon_id: int, stage: str = 'mature'
    ):
        """Get existing record or create a new one."""
        difficulty_rule = self.db.exec(
            select(DifficultyRule)
            .where(DifficultyRule.org_group_id == org_group_id)
            .where(DifficultyRule.taxon_id == taxon_id)
            .where(DifficultyRule.stage == stage)
        ).one_or_none()

        if difficulty_rule is None:
            # Create new.
            difficulty_rule = DifficultyRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id,
                stage=stage
            )

        return difficulty_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        difficulty_codes = self.db.exec(
            select(DifficultyRule)
            .where(DifficultyRule.org_group_id == org_group_id)
            .where(DifficultyRule.commit != rules_commit)
        )
        for row in difficulty_codes:
            self.db.delete(row)
        self.db.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read the id difficulty file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the id difficulty file into a dataframe.
        difficulties = pd.read_csv(
            f'{dir}/{file}',
            usecols=['tvk', 'code'],
            dtype={'tvk': str, 'code': 'Int64'}
        )

        # Get the difficulty codes for this org_group
        code_repo = DifficultyCodeRepo(self.db, self.env)
        code_lookup = code_repo.get_code_lookup(org_group_id)
        if len(code_lookup) == 0:
            errors.append("No difficulty codes exist.")
            return errors

        for row in difficulties.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, row['tvk'].strip()
                )
            except ValueError as e:
                errors.append(str(e))
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, taxon.preferred_tvk
                )

            # Check code is in limits
            if row['code'] not in code_lookup.keys():
                errors.append(f"Unknown code {row['code']} for {row['tvk']}.")
                continue

            # Add the rule to the db.
            difficulty_rule = self.get_or_create(org_group_id, taxon.id)
            difficulty_rule.difficulty_code_id = code_lookup[row['code']]
            difficulty_rule.commit = rules_commit
            self.db.add(difficulty_rule)

        # Save all the changes.
        self.db.commit()
        # Delete orphan DifficultyRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group.

        Returns a tuple of (id_difficulty, messages) where id_difficulty is the
        maximum difficulty code found and messages is a list of difficulty
        text. If no rules are found, id_difficulty is None."""
        messages = []
        id_difficulty = 0

        query = (
            select(OrgGroup, DifficultyCode)
            .select_from(DifficultyRule)
            .join(DifficultyCode)
            .join(OrgGroup)
            .join(Taxon)
            .where(Taxon.preferred_tvk == record.preferred_tvk)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        results = self.db.exec(query).all()

        # Do we have any id_difficulties?
        if len(results) == 0:
            return None, []

        # Find maximum difficulty code. The intention is to remove duplicates
        # in future. See
        # https://github.com/BiologicalRecordsCentre/record-cleaner-rules/issues/16
        for org_group, difficulty_code in results:
            if difficulty_code.code > id_difficulty:
                id_difficulty = difficulty_code.code
            messages.append(
                f"{org_group.organisation}:{org_group.group}:difficulty:"
                f"{difficulty_code.code}: {difficulty_code.text}"
            )

        return id_difficulty, messages
