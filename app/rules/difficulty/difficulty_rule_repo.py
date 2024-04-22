import pandas as pd

from sqlmodel import Session, select

import app.species.cache as cache

from app.sqlmodels import DifficultyCode, DifficultyRule, Taxon, OrgGroup

from .difficulty_code_repo import DifficultyCodeRepo


class DifficultyRuleRepo:

    def __init__(self, session: Session):
        self.session = session

    def list_by_org_group(self, org_group_id: int):
        results = self.session.exec(
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
        results = self.session.exec(
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
        difficulty_rule = self.session.exec(
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
        difficulty_codes = self.session.exec(
            select(DifficultyRule)
            .where(DifficultyRule.org_group_id == org_group_id)
            .where(DifficultyRule.commit != rules_commit)
        )
        for row in difficulty_codes:
            self.session.delete(row)
        self.session.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str = 'id_difficulty.csv'
    ):
        """Read the id difficulty file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        # Get the difficulty codes for this org_group
        code_repo = DifficultyCodeRepo(self.session)
        code_lookup = code_repo.get_code_lookup(org_group_id)
        if len(code_lookup) == 0:
            errors.append(
                f"No difficulty codes for org_group_id {org_group_id}"
            )
            return errors

        # Read the id difficulty file into a dataframe.
        difficulties = pd.read_csv(
            f'{dir}/{file}'
        )

        for row in difficulties.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    row['tvk'].strip(), self.session
                )
            except ValueError:
                errors.append(f"Could not find taxon for {row['tvk']}.")
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    taxon.preferred_tvk, self.session
                )

            # Check code is in limits
            if row['code'] not in code_lookup.keys():
                errors.append(
                    f"Unknown code {row['code']} for {row['tvk']} "
                    f"of org_group_id {org_group_id}."
                )
                continue

            # Save the difficulty rule in the database.
            difficulty_rule = self.get_or_create(org_group_id, taxon.id)
            difficulty_rule.difficulty_code_id = code_lookup[row['code']]
            difficulty_rule.commit = rules_commit
            self.session.add(difficulty_rule)
            self.session.commit()

        # Delete orphan DifficultyRules.
        self.purge(org_group_id, rules_commit)

        return errors
