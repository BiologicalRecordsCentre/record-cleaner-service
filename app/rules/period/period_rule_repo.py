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
        # Read the period file into a dataframe. Int64 is a nullable integer
        # allowing start or end to be omitted.
        periods = pd.read_csv(
            f'{dir}/{file}',
            usecols=[
                'tvk',
                'start_year',
                'start_month',
                'start_day',
                'end_year',
                'end_month',
                'end_day'
            ],
            dtype={
                'tvk': str,
                'start_year': 'Int64',
                'start_month': 'Int64',
                'start_day': 'Int64',
                'end_year': 'Int64',
                'end_month': 'Int64',
                'end_day': 'Int64'
            }
        )

        for row in periods.to_dict('records'):
            # Lookup preferred tvk.
            taxon = cache.get_taxon_by_tvk(self.session, row['tvk'].strip())
            if taxon is None:
                errors.append(f"Could not find taxon for {row['tvk']}.")
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.session, taxon.preferred_tvk
                )

            # Validate the data supplied.
            y = row['start_year']
            m = row['start_month']
            d = row['start_day']
            if pd.isna(y) and pd.isna(m) and pd.isna(d):
                start_date = None
            elif pd.isna(y) or pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete start date {y}-{m}-{d} for {row['tvk']}."
                )
                continue
            else:
                try:
                    start_date = date(y, m, d)
                except ValueError as e:
                    errors.append(
                        f"Invalid start date {y}-{m}-{d} for {row['tvk']}. {e}"
                    )
                    continue

            y = row['end_year']
            m = row['end_month']
            d = row['end_day']
            if pd.isna(y) and pd.isna(m) and pd.isna(d):
                end_date = None
            elif pd.isna(y) or pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete end date {y}-{m}-{d} for {row['tvk']}."
                )
                continue
            else:
                try:
                    end_date = date(y, m, d)
                except ValueError as e:
                    errors.append(
                        f"Invalid end date {y}-{m}-{d} for {row['tvk']}. {e}"
                    )
                    continue

            # Add the rule to the session.
            period_rule = self.get_or_create(org_group_id, taxon.id)
            period_rule.start_date = start_date
            period_rule.end_date = end_date
            period_rule.commit = rules_commit
            self.session.add(period_rule)

        # Save all the changes.
        self.session.commit()
        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return errors
