import pandas as pd

from sqlmodel import select

import app.species.cache as cache

from app.sqlmodels import AdditionalCode, AdditionalRule, Taxon, OrgGroup
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase
from .additional_code_repo import AdditionalCodeRepo


class AdditionalRuleRepo(RuleRepoBase):
    default_file = 'additional.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.db.exec(
            select(AdditionalRule, AdditionalCode)
            .join(AdditionalCode)
            .where(AdditionalRule.org_group_id == org_group_id)
            .order_by(AdditionalRule.organism_key)
        ).all()

        rules = []
        for additional_rule, additional_code in results:
            rules.append({
                'organism_key': additional_rule.organism_key,
                'taxon': additional_rule.taxon,
                'code': additional_code.code
            })

        return rules

    def list_by_organism_key(self, organism_key: str):
        results = self.db.exec(
            select(AdditionalRule, AdditionalCode, OrgGroup)
            .select_from(AdditionalRule)
            .join(AdditionalCode)
            .join(OrgGroup)
            .where(AdditionalRule.organism_key == organism_key)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for additional_rule, additional_code, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'code': additional_code.code,
                'text': additional_code.text
            })

        return rules

    def get_or_create(
        self, org_group_id: int, organism_key: str
    ):
        """Get existing record or create a new one."""
        additional_rule = self.db.exec(
            select(AdditionalRule)
            .where(AdditionalRule.org_group_id == org_group_id)
            .where(AdditionalRule.organism_key == organism_key)
        ).one_or_none()

        if additional_rule is None:
            # Create new.
            additional_rule = AdditionalRule(
                org_group_id=org_group_id,
                organism_key=organism_key,
            )

        return additional_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        additional_codes = self.db.exec(
            select(AdditionalRule)
            .where(AdditionalRule.org_group_id == org_group_id)
            .where(AdditionalRule.commit != rules_commit)
        )
        for row in additional_codes:
            self.db.delete(row)
        self.db.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read the additional file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the additional file into a dataframe.
        df = pd.read_csv(
            f'{dir}/{file}',
            usecols=['organism_key', 'taxon', 'code'],
            dtype={'organism_key': str, 'taxon': str, 'code': 'Int64'}
        )

        # Get the additional codes for this org_group
        code_repo = AdditionalCodeRepo(self.db, self.env)
        code_lookup = code_repo.get_code_lookup(org_group_id)
        if len(code_lookup) == 0:
            errors.append("No additional codes exist.")
            return errors

        for row in df.to_dict('records'):
            # Check code is in limits
            if row['code'] not in code_lookup.keys():
                errors.append(
                    f"Unknown code {row['code']} for {row['organism_key']}.")
                continue

            # Add the rule to the db.
            additional_rule = self.get_or_create(
                org_group_id, row['organism_key'])
            additional_rule.taxon = row['taxon']
            additional_rule.additional_code_id = code_lookup[row['code']]
            additional_rule.commit = rules_commit
            self.db.add(additional_rule)

        # Save all the changes.
        self.db.commit()
        # Delete orphan AdditionalRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group.

        Returns a tuple of (ok, messages) where ok indicates test success
        and messages is a list of details. If there are no rules, ok is None"""

        ok = True
        messages = []

        query = (
            select(OrgGroup, AdditionalCode)
            .select_from(AdditionalRule)
            .join(AdditionalCode)
            .join(OrgGroup)
            .where(AdditionalRule.organism_key == record.organism_key)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        rules = self.db.exec(query).all()
        # Do we have any rules?
        if len(rules) == 0:
            return None, []

        for org_group, additional_code in rules:
            ok = False
            messages.append(
                f"{org_group.organisation}:{org_group.group}:additional: "
                f"{additional_code.text}"
            )

        return ok, messages
