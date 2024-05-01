import re
import pandas as pd

from sqlmodel import select

import app.species.cache as cache

from app.sqlmodels import TenkmRule, Taxon, OrgGroup

from ..rule_repo_base import RuleRepoBase


class TenkmRuleRepo(RuleRepoBase):
    default_file = 'tenkm.csv'

    def list_by_org_group(self, org_group_id: int):
        results = self.session.exec(
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
        results = self.session.exec(
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
        tenkm_rule = self.session.exec(
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
        tenkm_rules = self.session.exec(
            select(TenkmRule)
            .where(TenkmRule.org_group_id == org_group_id)
            .where(TenkmRule.commit != rules_commit)
        )
        for row in tenkm_rules:
            self.session.delete(row)
        self.session.commit()

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
            taxon = cache.get_taxon_by_tvk(self.session, row['tvk'].strip())
            if taxon is None:
                errors.add(f"Could not find taxon for {row['tvk']}.")
                continue

            if taxon.tvk != taxon.preferred_tvk:
                taxon = cache.get_taxon_by_tvk(
                    self.session, taxon.preferred_tvk
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

            # Add the rule to the session.
            tenkm_rule = self.get_or_create(org_group_id, taxon.id, km100)
            tenkm_rule.km10 = km10str
            tenkm_rule.coord_system = coord_system
            tenkm_rule.commit = rules_commit
            self.session.add(tenkm_rule)

        # Save all the changes.
        self.session.commit()
        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return list(errors)
