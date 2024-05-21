from datetime import date
import pandas as pd

from sqlmodel import select

import app.species.cache as cache
from app.utility.vague_date import VagueDate

from app.sqlmodels import PhenologyRule, Taxon, OrgGroup, StageSynonym
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase


class PhenologyRuleRepo(RuleRepoBase):
    default_file = 'periodwithinyear.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.session.exec(
            select(PhenologyRule, Taxon)
            .join(Taxon)
            .where(PhenologyRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for phenology_rule, taxon in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'start_date': phenology_rule.start_day + "/" +
                phenology_rule.start_month,
                'end_date': phenology_rule.end_day + "/" +
                phenology_rule.end_month
            })

        return rules

    def list_by_tvk(self, tvk: str):
        results = self.session.exec(
            select(PhenologyRule, Taxon, OrgGroup)
            .join(Taxon)
            .join(OrgGroup)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        ).all()

        rules = []
        for phenology_rule, taxon, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'start_date': phenology_rule.start_day + "/" +
                phenology_rule.start_month,
                'end_date': phenology_rule.end_day + "/" +
                phenology_rule.end_month
            })

        return rules

    def get_or_create(self, org_group_id: int, taxon_id: int):
        """Get existing record or create a new one."""
        phenology_rule = self.session.exec(
            select(PhenologyRule)
            .where(PhenologyRule.org_group_id == org_group_id)
            .where(PhenologyRule.taxon_id == taxon_id)
        ).one_or_none()

        if phenology_rule is None:
            # Create new.
            phenology_rule = PhenologyRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id
            )

        return phenology_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        phenology_rules = self.session.exec(
            select(PhenologyRule)
            .where(PhenologyRule.org_group_id == org_group_id)
            .where(PhenologyRule.commit != rules_commit)
        )
        for row in phenology_rules:
            self.session.delete(row)
        self.session.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read period within year file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the file into a dataframe. Int64 is a nullable integer
        # allowing start or end to be omitted.
        periods = pd.read_csv(
            f'{dir}/{file}',
            usecols=[
                'tvk',
                'start_month',
                'start_day',
                'end_month',
                'end_day'
            ],
            dtype={
                'tvk': str,
                'start_month': 'Int64',
                'start_day': 'Int64',
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
            m = row['start_month']
            d = row['start_day']
            if pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete start date for {row['tvk']}."
                )
                continue
            else:
                try:
                    start_date = date(y, m, d)
                except ValueError as e:
                    errors.append(
                        f"Invalid start date for {row['tvk']}. {e}"
                    )
                    continue

            m = row['end_month']
            d = row['end_day']
            if pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete end date for {row['tvk']}."
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
            phenology_rule = self.get_or_create(org_group_id, taxon.id)
            phenology_rule.start_date = start_date
            phenology_rule.end_date = end_date
            phenology_rule.commit = rules_commit
            self.session.add(phenology_rule)

        # Save all the changes.
        self.session.commit()
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
            select(PhenologyRule, OrgGroup, StageSynonym)
            .join(OrgGroup)
            .join(Taxon)
            .join(StageSynonym)
            .where(record.tvk == Taxon.preferred_tvk)
            .where(record.stage in StageSynonym.synonyms)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        results = self.session.exec(query).all()
        for phenology_rule, org_group in results:
            if (
                phenology_rule.start_date is not None and
                end_date < phenology_rule.start_date
            ):
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record is before introduction date of "
                    f"{phenology_rule.start_date}"
                )

            if (
                phenology_rule.end_date is not None and
                start_date > phenology_rule.end_date
            ):
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:period: "
                    f"Record follows extinction date of "
                    f"{phenology_rule.end_date}"
                )

        return failures
