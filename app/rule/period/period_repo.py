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
            select(PeriodRule)
            .where(PeriodRule.org_group_id == org_group_id)
            .order_by(PeriodRule.organism_key)
        ).all()

        rules = []
        for period_rule in results:
            rules.append({
                'organism_key': period_rule.organism_key,
                'taxon': period_rule.taxon,
                'start_date': period_rule.start_date,
                'end_date': period_rule.end_date
            })

        return rules

    def list_by_organism_key(self, organism_key: str):
        results = self.db.exec(
            select(PeriodRule, OrgGroup)
            .join(OrgGroup)
            .where(PeriodRule.organism_key == organism_key)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for period_rule, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'start_date': period_rule.start_date,
                'end_date': period_rule.end_date
            })

        return rules

    def get_or_create(self, org_group_id: int, organism_key: str):
        """Get existing record or create a new one."""
        period_rule = self.db.exec(
            select(PeriodRule)
            .where(PeriodRule.org_group_id == org_group_id)
            .where(PeriodRule.organism_key == organism_key)
        ).one_or_none()

        if period_rule is None:
            # Create new.
            period_rule = PeriodRule(
                org_group_id=org_group_id,
                organism_key=organism_key
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
                'organism_key',
                'taxon',
                'start_year',
                'start_month',
                'start_day',
                'end_year',
                'end_month',
                'end_day'
            ],
            dtype={
                'organism_key': str,
                'taxon': str,
                'start_year': 'Int64',
                'start_month': 'Int64',
                'start_day': 'Int64',
                'end_year': 'Int64',
                'end_month': 'Int64',
                'end_day': 'Int64'
            }
        )

        for row in periods.to_dict('records'):
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
            period_rule = self.get_or_create(org_group_id, row['organism_key'])
            period_rule.taxon = row['taxon']
            period_rule.start_date = start_date
            period_rule.end_date = end_date
            period_rule.commit = rules_commit
            self.db.add(period_rule)
            # Save change immediately to avoid locks.
            self.db.commit()
        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return errors

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group.

        Returns a tuple of (ok, messages) where ok indicates test success
        and messages is a list of details. If there are no rules, ok is None"""

        ok = True
        messages = []

        vague_date = VagueDate(record.date).value
        start_date = vague_date['start'].strftime('%Y-%m-%d')
        end_date = vague_date['end'].strftime('%Y-%m-%d')

        query = (
            select(PeriodRule, OrgGroup)
            .join(OrgGroup)
            .where(PeriodRule.organism_key == record.organism_key)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        rules = self.db.exec(query).all()
        # Do we have any rules?
        if len(rules) == 0:
            return None, []

        for period_rule, org_group in rules:
            if (
                period_rule.start_date is not None and
                end_date < period_rule.start_date
            ):
                ok = False
                messages.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record is before introduction date of "
                    f"{period_rule.start_date}"
                )

            if (
                period_rule.end_date is not None and
                start_date > period_rule.end_date
            ):
                ok = False
                messages.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record follows extinction date of "
                    f"{period_rule.end_date}"
                )

        return ok, messages
