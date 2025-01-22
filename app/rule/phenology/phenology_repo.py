from datetime import date
import pandas as pd

from sqlmodel import select, or_

import app.species.cache as cache
from app.utility.vague_date import VagueDate

from app.sqlmodels import PhenologyRule, Taxon, OrgGroup, Stage, StageSynonym
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase
from ..stage.stage_repo import StageRepo


class PhenologyRuleRepo(RuleRepoBase):
    default_file = 'periodwithinyear.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.db.exec(
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
        results = self.db.exec(query).all()

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

        phenology_rule = self.db.exec(
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
        phenology_rules = self.db.exec(
            select(PhenologyRule)
            .where(PhenologyRule.org_group_id == org_group_id)
            .where(PhenologyRule.commit != rules_commit)
        )
        for row in phenology_rules:
            self.db.delete(row)
        self.db.commit()

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
                'start_day': 'Int64',
                'start_month': 'Int64',
                'end_day': 'Int64',
                'end_month': 'Int64',
                'stage': str
            }
        )

        # Get the stage codes for this org_group
        stage_repo = StageRepo(self.db, self.env)
        stage_lookup = stage_repo.get_stage_lookup(org_group_id)

        if len(stage_lookup) == 0:
            # No stages defined for this org_group so add 'everything' stage.
            stage = stage_repo.get_or_create(org_group_id, '*')
            stage.commit = rules_commit
            stage.sort_order = 0
            self.db.add(stage)
            self.db.commit()
            stage_lookup['*'] = stage.id

        for row in df.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, row['tvk'].strip()
                )
            except ValueError as e:
                errors.append(str(e))
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, taxon.preferred_tvk
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
            if stage not in stage_lookup.keys():
                errors.append(f"Unknown stage '{stage}' for {row['tvk']}.")
                continue

            # Add the rule to the db.
            phenology_rule = self.get_or_create(
                org_group_id, taxon.id, stage_lookup[stage])
            phenology_rule.start_day = row['start_day']
            phenology_rule.start_month = row['start_month']
            phenology_rule.end_day = row['end_day']
            phenology_rule.end_month = row['end_month']
            phenology_rule.commit = rules_commit
            self.db.add(phenology_rule)

        # Save all the changes.
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

        query = (
            select(PhenologyRule, OrgGroup, Stage)
            .select_from(PhenologyRule)
            .join(OrgGroup, OrgGroup.id == PhenologyRule.org_group_id)
            .join(Taxon, Taxon.id == PhenologyRule.taxon_id)
            .join(Stage, Stage.id == PhenologyRule.stage_id)
            .where(Taxon.preferred_tvk == record.preferred_tvk)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        if record.stage is None:
            # Use mature or 'everything' rule if no stage is specified.
            # No need to look at synonmms.
            query = query.where(or_(
                Stage.stage == 'mature',
                Stage.stage == '*'))
        else:
            # Use rule with matching stage synonym or 'everything' rule.
            # Left join synonyms as 'everything' rule won't have them.
            query = (
                query
                .join(StageSynonym, isouter=True)
                .where(or_(
                    StageSynonym.synonym == record.stage,
                    Stage.stage == '*'))
            )

        rules = self.db.exec(query).all()
        # Do we have any rules?
        if len(rules) == 0:
            return None, []

        for phenology_rule, org_group, stage in rules:
            # Apply the rule we have found.
            result = self.test(record, phenology_rule)
            if result is not None:
                ok = False
                messages.append(
                    f"{org_group.organisation}:{org_group.group}:phenology:"
                    f"{stage.stage}:{result}"
                )

        return ok, messages

    def test(self, record: Verified, rule: PhenologyRule):
        """Test the record against the rule.

        It seems to be easier to test the failure conditions.

        For a rule spanning the new year, a failing record is one that falls
        wholly between the end of the rule in spring and it starting in
        autumn of the same year.

        When the rule does not span the new year, a failing record is one that
        falls wholly between the end of the rule in autumn and it starting
        in spring of the next year."""

        # Get record start and end as date objects.
        vague_date = VagueDate(record.date).value
        record_start = vague_date['start'].date()
        record_end = vague_date['end'].date()

        # Look out for rules spanning new year.
        rule_spans_new_year = rule.start_month > rule.end_month

        # Get rule start and end as date objects.
        start_year = int(record_start.strftime('%Y'))
        rule_start = date(start_year, rule.start_month, rule.start_day)
        rule_end = date(start_year, rule.end_month, rule.end_day)
        if not rule_spans_new_year:
            # For 'summer' rules, the failure period is between autumn of one
            # year and spring of the next.
            if record_start < rule_start:
                rule_end = date(
                    start_year - 1, rule.start_month, rule.start_day)
            else:
                rule_start = date(
                    start_year + 1, rule.start_month, rule.start_day)

        # Calculate the days of separation between the rule and the record.
        record_end_to_rule_start = (rule_start - record_end).days
        rule_end_to_record_start = (record_start - rule_end).days

        tolerance = int(self.env.phenology_tolerance)

        # Create boolean values used for testing rule.
        record_ends_before_rule_starts = record_end_to_rule_start > 0
        record_starts_after_rule_ends = rule_end_to_record_start > 0
        record_ends_just_before_rule_starts = (
            record_end_to_rule_start <= tolerance)
        record_starts_just_after_rule_ends = (
            rule_end_to_record_start <= tolerance)

        if (record_starts_after_rule_ends and record_ends_before_rule_starts):
            if (record_starts_just_after_rule_ends or
                    record_ends_just_before_rule_starts):
                return (
                    f"Record is just outside of expected period of "
                    f"{rule.start_day}/{rule.start_month} - "
                    f"{rule.end_day}/{rule.end_month}."
                )
            else:
                return (
                    f"Record is outside of expected period of "
                    f"{rule.start_day}/{rule.start_month} - "
                    f"{rule.end_day}/{rule.end_month}."
                )
