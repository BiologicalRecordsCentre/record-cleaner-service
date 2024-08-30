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
        results = self.session.exec(
            select(AdditionalRule, Taxon, AdditionalCode)
            .join(Taxon)
            .join(AdditionalCode)
            .where(AdditionalRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for additional_rule, taxon, additional_code in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'code': additional_code.code
            })

        return rules

    def list_by_tvk(self, tvk: str):
        results = self.session.exec(
            select(AdditionalRule, Taxon, AdditionalCode, OrgGroup)
            .join(Taxon)
            .join(AdditionalCode)
            .join(OrgGroup)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for additional_rule, taxon, additional_code, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'code': additional_code.code,
                'text': additional_code.text
            })

        return rules

    def get_or_create(
        self, org_group_id: int, taxon_id: int
    ):
        """Get existing record or create a new one."""
        additional_rule = self.session.exec(
            select(AdditionalRule)
            .where(AdditionalRule.org_group_id == org_group_id)
            .where(AdditionalRule.taxon_id == taxon_id)
        ).one_or_none()

        if additional_rule is None:
            # Create new.
            additional_rule = AdditionalRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id,
            )

        return additional_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        additional_codes = self.session.exec(
            select(AdditionalRule)
            .where(AdditionalRule.org_group_id == org_group_id)
            .where(AdditionalRule.commit != rules_commit)
        )
        for row in additional_codes:
            self.session.delete(row)
        self.session.commit()

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
            usecols=['tvk', 'code'],
            dtype={'tvk': str, 'code': int}
        )

        # Get the additional codes for this org_group
        code_repo = AdditionalCodeRepo(self.session)
        code_lookup = code_repo.get_code_lookup(org_group_id)
        if len(code_lookup) == 0:
            errors.append("No additional codes exist.")
            return errors

        for row in df.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    self.session, row['tvk'].strip()
                )
            except ValueError as e:
                errors.append(str(e))
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.session, taxon.preferred_tvk
                )

            # Check code is in limits
            if row['code'] not in code_lookup.keys():
                errors.append(f"Unknown code {row['code']} for {row['tvk']}.")
                continue

            # Add the rule to the session.
            additional_rule = self.get_or_create(org_group_id, taxon.id)
            additional_rule.additional_code_id = code_lookup[row['code']]
            additional_rule.commit = rules_commit
            self.session.add(additional_rule)

        # Save all the changes.
        self.session.commit()
        # Delete orphan AdditionalRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group."""
        failures = []

        query = (
            select(OrgGroup, AdditionalCode)
            .select_from(AdditionalRule)
            .join(AdditionalCode)
            .join(OrgGroup)
            .join(Taxon)
            .where(Taxon.preferred_tvk == record.tvk)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        results = self.session.exec(query).all()
        for org_group, additional_code in results:
            failures.append(
                f"{org_group.organisation}:{org_group.group}:additional: "
                f"{additional_code.text}"
            )

        return failures
