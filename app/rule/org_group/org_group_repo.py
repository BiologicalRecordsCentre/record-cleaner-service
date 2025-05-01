import os

from sqlmodel import Session, select

from app.sqlmodels import OrgGroup


class OrgGroupRepo:

    def __init__(self, db: Session):
        self.db = db

    def list(self, id: int = None):
        """List all records or a single record by id."""
        if id is None:
            results = self.db.exec(
                select(OrgGroup)
                .order_by(OrgGroup.organisation, OrgGroup.group)
            ).all()
            return results
        else:
            result = self.db.get(OrgGroup, id)
            return result

    def get(self, organisation: str, group: str):
        """Get record by organisation and group."""
        return self.db.exec(
            select(OrgGroup)
            .where(OrgGroup.organisation == organisation)
            .where(OrgGroup.group == group)
        ).one_or_none()

    def get_or_create(self, organisation: str, group: str):
        """Get existing record or create a new one."""

        org_group = self.get(organisation, group)

        if org_group is None:
            # Create if new.
            org_group = OrgGroup(
                organisation=organisation,
                group=group
            )

        return org_group

    def purge(self, rules_commit):
        """Delete records for org_group not from current commit."""
        org_groups = self.db.exec(
            select(OrgGroup)
            .where(OrgGroup.commit != rules_commit)
        )
        for row in org_groups:
            # Testing indicates that deletion cascades.
            self.db.delete(row)
            self.db.commit()

    def load_dir_structure(self, dir: str, rules_commit: str):
        """Scan the directory structure and save to database."""

        # Top level folder is the organisation.
        organisations = []
        for organisation in os.scandir(dir):
            if organisation.is_dir():
                organisations.append(organisation.name)

        # Second level folder is a group within the organisation.
        for organisation in organisations:
            organisationdir = os.path.join(dir, organisation)

            for group in os.scandir(organisationdir):
                if group.is_dir():
                    # Save the organisation groups in the database.
                    org_group = self.get_or_create(organisation, group.name)
                    org_group.commit = rules_commit
                    self.db.add(org_group)
                    self.db.commit()

        # Delete orphan OrgGroups.
        self.purge(rules_commit)
