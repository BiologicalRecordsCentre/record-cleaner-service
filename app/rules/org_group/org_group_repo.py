from sqlmodel import Session, select


from app.database import engine
from app.sqlmodels import OrgGroup


class OrgGroupRepo:

    @classmethod
    def list(cls, id: int = None):
        with Session(engine) as session:
            if id is None:
                results = session.exec(select(OrgGroup)).all()
            else:
                results = session.get(OrgGroup, id)
            return results

    @classmethod
    def get_or_create(cls, organisation: str, group: str):

        with Session(engine) as session:
            org_group = session.exec(
                select(OrgGroup)
                .where(OrgGroup.organisation == organisation)
                .where(OrgGroup.group == group)
            ).one_or_none()

            if org_group is None:
                # Create if new.
                org_group = OrgGroup(
                    organisation=organisation,
                    group=group
                )
                session.add(org_group)
                session.commit()
                session.refresh(org_group)

        return org_group
