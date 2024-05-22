from datetime import date
import pandas as pd

from sqlmodel import select

import app.species.cache as cache
from app.utility.vague_date import VagueDate

from app.sqlmodels import PhenologyRule, Taxon, OrgGroup, Stage, StageSynonym
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase
from ..stage.stage_repo import StageRepo


class PhenologyRuleRepo(RuleRepoBase):
    default_file = 'periodwithinyear.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.session.exec(
            select(PhenologyRule, Taxon, Stage)
            .join(Taxon)
            .join(Stage)
            .where(PhenologyRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for phenology, taxon, stage in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'start_date': f"{phenology.start_day}/{phenology.start_month}",
                'end_date': f"{phenology.end_day}/{phenology.end_month}",
                'stage': stage.stage
            })

        return rules

    def list_by_tvk(self, tvk: str):
        query = (
            select(PhenologyRule, OrgGroup, Stage)
            .join(Taxon)
            .join(OrgGroup)
            .join(Stage, Stage.id == PhenologyRule.stage_id)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        )
        results = self.session.exec(query).all()

        rules = []
        for phenology, org_group, stage in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'start_date': f"{phenology.start_day}/{phenology.start_month}",
                'end_date': f"{phenology.end_day}/{phenology.end_month}",
                'stage': stage.stage
            })

        return rules

    def get_or_create(self, org_group_id: int, taxon_id: int, stage_id: int):
        """Get existing record or create a new one."""

        phenology_rule = self.session.exec(
            select(PhenologyRule)
            .where(PhenologyRule.org_group_id == org_group_id)
            .where(PhenologyRule.taxon_id == taxon_id)
            .where(PhenologyRule.stage_id == stage_id)
        ).one_or_none()

        if phenology_rule is None:
            # Create new.
            phenology_rule = PhenologyRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id,
                stage_id=stage_id
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
        # Read the file into a dataframe.
        df = pd.read_csv(
            f'{dir}/{file}',
            usecols=[
                'tvk',
                'start_day',
                'start_month',
                'end_day',
                'end_month',
                'stage'
            ],
            dtype={
                'tvk': str,
                'start_day': int,
                'start_month': int,
                'end_day': int,
                'end_month': int,
                'stage': str
            }
        )

        # Get the additional codes for this org_group
        stage_repo = StageRepo(self.session)
        stage_lookup = stage_repo.get_stage_lookup(org_group_id)

        for row in df.to_dict('records'):
            # Lookup preferred tvk.
            taxon = cache.get_taxon_by_tvk(self.session, row['tvk'].strip())
            if taxon is None:
                errors.append(f"Could not find taxon for {row['tvk']}.")
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.session, taxon.preferred_tvk
                )

            # Validate start date.
            m = row['start_month']
            d = row['start_day']
            if pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete start date for {row['tvk']}."
                )
                continue
            else:
                try:
                    date(2000, m, d)
                except ValueError as e:
                    errors.append(
                        f"Invalid start date for {row['tvk']}. {e}"
                    )
                    continue

            # Validate end date.
            m = row['end_month']
            d = row['end_day']
            if pd.isna(m) or pd.isna(d):
                errors.append(
                    f"Incomplete end date for {row['tvk']}."
                )
                continue
            else:
                try:
                    date(2000, m, d)
                except ValueError as e:
                    errors.append(
                        f"Invalid end date for {row['tvk']}. {e}"
                    )
                    continue

            # Validate stage.
            stage = row['stage'].strip().lower()
            if (
                stage not in stage_lookup.keys() and
                stage != '*'
            ):
                errors.append(f"Unknown stage '{stage}' for {row['tvk']}.")
                continue

            # Add the rule to the session.
            phenology_rule = self.get_or_create(
                org_group_id, taxon.id, stage_lookup[stage])
            phenology_rule.start_day = row['start_day']
            phenology_rule.start_month = row['start_month']
            phenology_rule.end_day = row['end_day']
            phenology_rule.end_month = row['end_month']
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
