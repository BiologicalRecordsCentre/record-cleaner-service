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
            select(DifficultyRule, DifficultyCode)
            .join(DifficultyCode)
            .where(DifficultyRule.org_group_id == org_group_id)
            .order_by(DifficultyRule.organism_key)
        ).all()

        rules = []
        for difficulty_rule, difficulty_code in results:
            rules.append({
                'organism_key': difficulty_rule.organism_key,
                'taxon': difficulty_rule.taxon,
                'difficulty': difficulty_code.code
            })

        return rules

    def list_by_organism_key(self, organism_key: str):
        results = self.db.exec(
            select(DifficultyRule, DifficultyCode, OrgGroup)
            .select_from(DifficultyRule)
            .join(DifficultyCode)
            .join(OrgGroup)
            .where(DifficultyRule.organism_key == organism_key)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for difficulty_rule, difficulty_code, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'difficulty': difficulty_code.code,
                'text': difficulty_code.text
            })

        return rules

    def get_or_create(
        self, org_group_id: int, organism_key: str, stage: str = 'mature'
    ):
        """Get existing record or create a new one."""
        difficulty_rule = self.db.exec(
            select(DifficultyRule)
            .where(DifficultyRule.org_group_id == org_group_id)
            .where(DifficultyRule.organism_key == organism_key)
            .where(DifficultyRule.stage == stage)
        ).one_or_none()

        if difficulty_rule is None:
            # Create new.
            difficulty_rule = DifficultyRule(
                org_group_id=org_group_id,
                organism_key=organism_key,
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
            usecols=['organism_key', 'taxon', 'code'],
            dtype={'organism_key': str, 'taxon': str, 'code': 'Int64'}
        )

        # Get the difficulty codes for this org_group
        code_repo = DifficultyCodeRepo(self.db, self.env)
        code_lookup = code_repo.get_code_lookup(org_group_id)
        if len(code_lookup) == 0:
            errors.append("No difficulty codes exist.")
            return errors

        for row in difficulties.to_dict('records'):
            # Check code is in limits
            if row['code'] not in code_lookup.keys():
                errors.append(
                    f"Unknown code {row['code']} for {row['organism_key']}.")
                continue

            # Add the rule to the db.
            difficulty_rule = self.get_or_create(
                org_group_id, row['organism_key'])
            difficulty_rule.taxon = row['taxon']
            difficulty_rule.difficulty_code_id = code_lookup[row['code']]
            difficulty_rule.commit = rules_commit
            self.db.add(difficulty_rule)

        # Save all the changes.
        self.db.commit()
        # Delete orphan DifficultyRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(
        self,
        record: Verified,
        verbose: bool = True,
        org_group_id: int | None = None,
    ):
        """Run rules against record, optionally filter rules by org_group.

        Returns a tuple of (id_difficulty, messages) where id_difficulty is the
        maximum difficulty code found and messages is a list of difficulty
        text. If no rules are found, id_difficulty is None. If verbose is
        False, messages is an empty list."""
        messages = []
        id_difficulty = 0

        query = (
            select(OrgGroup, DifficultyCode)
            .select_from(DifficultyRule)
            .join(DifficultyCode)
            .join(OrgGroup)
            .where(DifficultyRule.organism_key == record.organism_key)
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
            if verbose:
                messages.append(
                    f"{org_group.organisation}:{org_group.group}:difficulty:"
                    f"{difficulty_code.code}: {difficulty_code.text}"
                )

        return id_difficulty, messages
