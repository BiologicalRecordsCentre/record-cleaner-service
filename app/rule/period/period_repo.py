from datetime import date
import pandas as pd

from sqlmodel import select

import app.species.cache as cache
from app.utility.vague_date import VagueDate

from app.sqlmodels import PeriodRule, Taxon, OrgGroup
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase


class PeriodRuleRepo(RuleRepoBase):
    default_file = 'period.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.db.exec(
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
        results = self.db.exec(
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
        period_rule = self.db.exec(
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
        period_rules = self.db.exec(
            select(PeriodRule)
            .where(PeriodRule.org_group_id == org_group_id)
            .where(PeriodRule.commit != rules_commit)
        )
        for row in period_rules:
            self.db.delete(row)
        self.db.commit()

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
            try:
                taxon = cache.get_taxon_by_tvk(
                    self.db, row['tvk'].strip()
                )
            except ValueError as e:
                errors.append(str(e))
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.db, taxon.preferred_tvk
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

            # Add the rule to the db.
            period_rule = self.get_or_create(org_group_id, taxon.id)
            period_rule.start_date = start_date
            period_rule.end_date = end_date
            period_rule.commit = rules_commit
            self.db.add(period_rule)

        # Save all the changes.
        self.db.commit()
        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group."""
        failures = []

        vague_date = VagueDate(record.date).value
        start_date = vague_date['start'].strftime('%Y-%m-%d')
        end_date = vague_date['end'].strftime('%Y-%m-%d')

        query = (
            select(PeriodRule, OrgGroup)
            .join(OrgGroup)
            .join(Taxon)
            .where(Taxon.preferred_tvk == record.preferred_tvk)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        results = self.db.exec(query).all()
        for period_rule, org_group in results:
            if (
                period_rule.start_date is not None and
                end_date < period_rule.start_date
            ):
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record is before introduction date of "
                    f"{period_rule.start_date}"
                )

            if (
                period_rule.end_date is not None and
                start_date > period_rule.end_date
            ):
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record follows extinction date of "
                    f"{period_rule.end_date}"
                )

        return failures
