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

        # Get the org_groups having rules for the taxon.
        query = (
            select(OrgGroup)
            .select_from(PhenologyRule)
            .distinct()
            .join(OrgGroup)
            .join(Taxon)
            .where(Taxon.preferred_tvk == record.tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        # Do we have any rules?
        org_groups = self.session.exec(query).all()
        if len(org_groups) == 0:
            if org_group_id is None:
                failures.append(
                    "*:*:phenology: There is no rule for this taxon."
                )
            else:
                org_group = self.session.get(OrgGroup, org_group_id)
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:phenology: "
                    "There is no rule for this taxon."
                )
            return failures

        # Try the rules from each org_group.
        for org_group in org_groups:

            query = (
                select(PhenologyRule)
                .join(Taxon)
                .join(Stage)
                .where(Taxon.preferred_tvk == record.tvk)
                .where(PhenologyRule.org_group_id == org_group.id)
            )

            if record.stage is None:
                # Use mature rule if no stage is specified.
                query = query.where(Stage.stage == 'mature')
            else:
                query = (
                    query
                    .join(StageSynonym)
                    .where(StageSynonym.synonym == record.stage)
                )

            phenology_rule = self.session.exec(query).one_or_none()

            if phenology_rule is None:
                # No rule found matching stage.
                if record.stage is None:
                    failures.append(
                        f"{org_group.organisation}:{org_group.group}:"
                        f"phenology: Could not find rule for stage 'mature'."
                    )
                else:
                    failures.append(
                        f"{org_group.organisation}:{org_group.group}:"
                        "phenology: Could not find rule for stage "
                        f"'{record.stage}'."
                    )
                continue

            # Apply the rule we have found.
            result = self.test(record, phenology_rule)
            if result is not None:
                failures.append(
                    f"{org_group.organisation}:{org_group.group}:{result}"
                )

        return failures

    def test(self, record: Verified, rule: PhenologyRule):
        """Test the record against the rule."""

        vague_date = VagueDate(record.date).value
        start_day = int(vague_date['start'].strftime('%d'))
        start_month = int(vague_date['start'].strftime('%m'))
        end_day = int(vague_date['end'].strftime('%d'))
        end_month = int(vague_date['end'].strftime('%m'))

        record_ends_before_rule_starts = (
            (end_month < rule.start_month) or
            (end_month == rule.start_month and end_day < rule.start_day)
        )

        record_starts_after_rule_ends = (
            (start_month > rule.end_month) or
            (start_month == rule.end_month and start_day > rule.end_day)
        )

        rule_spans_new_year = rule.start_month > rule.end_month

        record_spans_new_year = start_month > end_month

        # It seems to be easier to define the failure conditions.
        # See docs/assests/images/phenology-tests.png for explanation.
        if (
                (
                    rule_spans_new_year and
                    not record_spans_new_year and
                    record_starts_after_rule_ends and
                    record_ends_before_rule_starts
                )
                or
                (
                    not rule_spans_new_year and (
                        record_ends_before_rule_starts or
                        record_starts_after_rule_ends)
                )
        ):
            return (
                f"phenology: Record is outside of expected period of "
                f"{rule.start_day}/{rule.start_month} - "
                f"{rule.end_day}/{rule.end_month}."
            )
