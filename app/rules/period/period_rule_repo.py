from datetime import date
import pandas as pd

from sqlmodel import select

import app.species.cache as cache

from app.sqlmodels import PeriodRule, Taxon, OrgGroup

from ..rule_repo_base import RuleRepoBase


class PeriodRuleRepo(RuleRepoBase):
    default_file = 'period.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.session.exec(
            select(PeriodRule, Taxon)
            .join(Taxon)
            .where(PeriodRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for period_rule, taxon in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'start_date': period_rule.start_date,
                'end_date': period_rule.end_date
            })

        return rules

    def list_by_tvk(self, tvk: str):
        results = self.session.exec(
            select(PeriodRule, Taxon, OrgGroup)
            .join(Taxon)
            .join(OrgGroup)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for period_rule, taxon, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'start_date': period_rule.start_date,
                'end_date': period_rule.end_date
            })

        return rules

    def get_or_create(self, org_group_id: int, taxon_id: int):
        """Get existing record or create a new one."""
        period_rule = self.session.exec(
            select(PeriodRule)
            .where(PeriodRule.org_group_id == org_group_id)
            .where(PeriodRule.taxon_id == taxon_id)
        ).one_or_none()

        if period_rule is None:
            # Create new.
            period_rule = PeriodRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id
            )

        return period_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        period_rules = self.session.exec(
            select(PeriodRule)
            .where(PeriodRule.org_group_id == org_group_id)
            .where(PeriodRule.commit != rules_commit)
        )
        for row in period_rules:
            self.session.delete(row)
        self.session.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read the period file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the period file into a dataframe.
        periods = pd.read_csv(
            f'{dir}/{file}'
        )

        for row in periods.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    row['tvk'].strip(), self.session)
            except ValueError:
                errors.append(f"Could not find taxon for {row['tvk']}.")
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    taxon.preferred_tvk, self.session
                )

            # Save the period rule in the database.
            period_rule = self.get_or_create(org_group_id, taxon.id)
            period_rule.start_date = date(
                row['start_year'], row['start_month'], row['start_day']
            )
            period_rule.end_date = date(
                row['end_year'], row['end_month'], row['end_day']
            )
            period_rule.commit = rules_commit
            self.session.add(period_rule)
            self.session.commit()

        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return errors
