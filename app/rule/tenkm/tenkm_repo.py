import re
import pandas as pd

from sqlmodel import select

import app.species.cache as cache

from app.sqlmodels import TenkmRule, Taxon, OrgGroup
from app.utility.sref.grid_utils import GridUtils
from app.verify.verify_models import Verified

from ..rule_repo_base import RuleRepoBase


class TenkmRuleRepo(RuleRepoBase):
    default_file = 'tenkm.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.db.exec(
            select(TenkmRule, Taxon)
            .join(Taxon)
            .where(TenkmRule.org_group_id == org_group_id)
            .order_by(Taxon.tvk)
        ).all()

        rules = []
        for tenkm_rule, taxon in results:
            rules.append({
                'tvk': taxon.tvk,
                'taxon': taxon.name,
                'km100': tenkm_rule.km100,
                'km10': tenkm_rule.km10,
                'coord_system': tenkm_rule.coord_system
            })

        return rules

    def list_by_tvk(self, tvk: str):
        results = self.db.exec(
            select(TenkmRule, Taxon, OrgGroup)
            .join(Taxon)
            .join(OrgGroup)
            .where(Taxon.tvk == tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group, TenkmRule.km100)
        ).all()

        rules = []
        for tenkm_rule, taxon, org_group in results:
            rules.append({
                'organisation': org_group.organisation,
                'group': org_group.group,
                'km100': tenkm_rule.km100,
                'km10': tenkm_rule.km10,
                'coord_system': tenkm_rule.coord_system
            })

        return rules

    def get_or_create(self, org_group_id: int, taxon_id: int, km100: str):
        """Get existing record or create a new one."""
        tenkm_rule = self.db.exec(
            select(TenkmRule)
            .where(TenkmRule.org_group_id == org_group_id)
            .where(TenkmRule.taxon_id == taxon_id)
            .where(TenkmRule.km100 == km100)
        ).one_or_none()

        if tenkm_rule is None:
            # Create new.
            tenkm_rule = TenkmRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id,
                km100=km100
            )

        return tenkm_rule

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        tenkm_rules = self.db.exec(
            select(TenkmRule)
            .where(TenkmRule.org_group_id == org_group_id)
            .where(TenkmRule.commit != rules_commit)
        )
        for row in tenkm_rules:
            self.db.delete(row)
        self.db.commit()

    def load_file(
            self,
            dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read the tenkm file, interpret, and save to database."""

        # Accumulate a list of unique errors.
        errors = set()

        if file is None:
            file = self.default_file
        # Read the period file into a dataframe.
        # Ensure km100 = NA is not treated as NaN.
        tenkms = pd.read_csv(
            f'{dir}/{file}', dtype=str, keep_default_na=False
        )

        for row in tenkms.to_dict('records'):
            # Lookup preferred tvk.
            try:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, row['tvk'].strip()
                )
            except ValueError as e:
                errors.add(str(e))
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.db, self.env, taxon.preferred_tvk
                )

            # Validate the data supplied.
            coord_system = row['coord_system'].strip().upper()
            if coord_system not in ['OSGB', 'OSNI', 'OSIE', 'CI']:
                errors.add(
                    f"Invalid coord_system {coord_system} "
                    f"for {row['tvk']}"
                )
                continue

            km100 = row['km100'].replace(' ', '').upper()
            match coord_system:
                case 'OSGB':
                    pattern = r'^(H[L-Z]|J[LMQR]|N[A-HJ-Z]|O[ABFGLMQRVW]|S[A-HJ-Z]|T[ABFGLMQRVW])$'
                case 'OSNI' | 'OSIE':
                    pattern = r'^[A-HJ-Z]$'
                case 'CI':
                    pattern = r'^[S-Z]([U-V]|[A-G])$'
            if not re.match(pattern, km100):
                errors.add(
                    f"Invalid km100 {km100} in {coord_system} "
                    f"for {row['tvk']}"
                )
                continue

            km10str = row['km10'].strip()
            km10s = km10str.split()
            pattern = r'^[0-9][0-9]$'
            for km10 in km10s:
                if not re.match(pattern, km10):
                    errors.add(
                        f"Invalid km10 {km10} in {coord_system} "
                        f"for {row['tvk']}"
                    )
                    continue

            # Add the rule to the db.
            tenkm_rule = self.get_or_create(org_group_id, taxon.id, km100)
            tenkm_rule.km10 = km10str
            tenkm_rule.coord_system = coord_system
            tenkm_rule.commit = rules_commit
            self.db.add(tenkm_rule)

        # Save all the changes.
        self.db.commit()
        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return list(errors)

    def run(self, record: Verified, org_group_id: int | None = None):
        """Run rules against record, optionally filter rules by org_group.

        Args:
            record (Verified): The record being tested.
            org_group_id (int): Optional id of org_group from which to select 
            rules.
        Returns
            tuple[bool, list[str]]: of (ok, messages) where ok indicates test 
            success and messages is a list of details. If there are no rules, 
            ok is None.
        """

        # Get the org_groups having rules for the taxon.
        query = (
            select(OrgGroup)
            .select_from(TenkmRule)
            .distinct()
            .join(OrgGroup)
            .join(Taxon)
            .where(Taxon.preferred_tvk == record.preferred_tvk)
            .order_by(OrgGroup.organisation, OrgGroup.group)
        )
        if org_group_id is not None:
            query = query.where(OrgGroup.id == org_group_id)

        # Do we have any rules?
        org_groups = self.db.exec(query).all()
        if len(org_groups) == 0:
            # No we don't.
            return None, []

        # Test the record
        ok, messages = self.test_recorded_10km(record, org_groups)

        if not ok and self.env.tenkm_tolerance > 0:
            # Test the squares in the tolerance band
            ok, messages = self.test_surrounding_10kms(
                record, org_groups
            )

        return ok, messages

    def test_recorded_10km(self, record: Verified, org_groups: list[OrgGroup]):
        """Run rules from org_groups against record.

        Args:
            record (Verified): The record being tested.
            org_groups (int): List of OrgGroup from which to select rules.
        Returns
            tuple[bool, list[str]]: of (ok, messages) where ok indicates test 
            success and messages is a list of details.
        """
        messages = []

        km100 = record.sref.km100
        km10 = record.sref.km10
        tvk = record.preferred_tvk
        # Try the rules from each org_group.
        for org_group in org_groups:
            ok, message = self.test(km100, km10, org_group, tvk)
            if not ok:
                messages.append(message)

        # Any messages returned indicate a failure
        if len(messages) > 0:
            return False, messages
        else:
            return True, []

    def test_surrounding_10kms(
        self, record: Verified,
        org_groups: list[OrgGroup]
    ):
        """Run rules from org_groups against squares around record.

        Args:
            record (Verified): The record being tested.
            org_groups (int): List of OrgGroup from which to select rules.
        Returns
            tuple[bool, list[str]]: of (ok, messages) where ok indicates test 
            success and messages is a list of details.
        """
        messages = []

        utils = GridUtils()
        record_km10 = record.sref.km100 + record.sref.km10
        surrounding_km10s = utils.get_surrounding_km10s(
            record_km10, self.env.tenkm_tolerance
        )
        tvk = record.preferred_tvk

        # Try the rules from each org_group.
        for org_group in org_groups:
            # Try the rules for each surrounding square
            for surrounding_km10 in surrounding_km10s:
                l = len(surrounding_km10)
                km10 = surrounding_km10[l-2: l]
                km100 = surrounding_km10[0: l-2]

                ok, message = self.test(km100, km10, org_group, tvk)
                if ok:
                    # A surrounding square passed a test.
                    messages.append(
                        f"{org_group.organisation}:{org_group.group}:tenkm: "
                        "Record is just outside known area."
                    )
                    # Once a square passes we can move to next org_group.
                    break

            if not ok:
                # No surrounding squares passed
                messages.append(
                    f"{org_group.organisation}:{org_group.group}:tenkm: "
                    "Record is outside known area."
                )

        if len(messages) > 0:
            # Any messages indicate a pass in the tolerance band but this is
            # still a failure (as a first draft anyway).
            return False, messages
        else:
            # No messages indicates outright failure.
            return False, []

    def test(self, km100: str, km10: str, org_group: OrgGroup, tvk: str):
        """Run org_group rules against taxon and location.

        Args:
            km100 (str): The letter(s) indicating 100km square.
            km10 (str): The two digits indicaing 10km square within km100.
            org_group (OrgGroup): The OrgGroup with the rules.
            tvk (str): The taxon version key identifying the taxon.
        Returns:
            tuple[bool, str]: (ok, message) where ok indicates test success
            and message has details details. If there are no rules, ok is
            None."""
        ok = True
        message = ''

        query = (
            select(TenkmRule)
            .join(Taxon)
            .where(Taxon.preferred_tvk == tvk)
            .where(TenkmRule.km100 == km100)
            .where(TenkmRule.org_group_id == org_group.id)
        )
        tenkm_rule = self.db.exec(query).one_or_none()

        if tenkm_rule is None:
            # No matching km100 in the rules.
            ok = False
        else:
            km10s = tenkm_rule.km10.split()
            if (km10 not in km10s):
                # No matching km10 in the rules.
                ok = False

        if not ok:
            message = (
                f"{org_group.organisation}:{org_group.group}:tenkm: "
                "Record is outside known area."
            )

        return ok, message
