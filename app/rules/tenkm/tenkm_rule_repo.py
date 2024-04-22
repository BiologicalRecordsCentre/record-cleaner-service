from datetime import date
import pandas as pd

from sqlmodel import Session, select

import app.species.cache as cache

from app.sqlmodels import TenkmRule, Taxon, OrgGroup


class TenkmRuleRepo:

    def __init__(self, session):
        self.session = session

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
            .order_by(OrgGroup.organisation, OrgGroup.group)
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

    def get_or_create(self, org_group_id: int, taxon_id: int):
        """Get existing record or create a new one."""
        tenkm_rule = self.session.exec(
            select(TenkmRule)
            .where(TenkmRule.org_group_id == org_group_id)
            .where(TenkmRule.taxon_id == taxon_id)
        ).one_or_none()

        if tenkm_rule is None:
            # Create new.
            tenkm_rule = TenkmRule(
                org_group_id=org_group_id,
                taxon_id=taxon_id
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
            file: str = 'tenkm.csv'
    ):
        """Read the tenkm file, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        # Read the period file into a dataframe.
        tenkms = pd.read_csv(
            f'{dir}/{file}'
        )

        for row in tenkms.to_dict('records'):
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

            # Save the tenkm rule in the database.
            tenkm_rule = self.get_or_create(org_group_id, taxon.id)
            tenkm_rule.km100 = row['km100'].strip()
            tenkm_rule.km10 = str(row['km10']).strip()
            tenkm_rule.coord_system = row['coord_system'].strip()
            tenkm_rule.commit = rules_commit
            self.session.add(tenkm_rule)
            self.session.commit()

        # Delete orphan PeriodRules.
        self.purge(org_group_id, rules_commit)

        return errors
