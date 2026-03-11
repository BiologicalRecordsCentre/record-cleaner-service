import datetime

from sqlmodel import Session, select

from app.sqlmodels import Usage


class UsageRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, username: str):
        """Get existing record or create a new one."""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month

        usage = self.db.exec(
            select(Usage)
            .where(Usage.user_name == username)
            .where(Usage.year == year)
            .where(Usage.month == month)
        ).one_or_none()

        if usage is None:
            # Create new.
            usage = Usage(
                user_name=username,
                year=year,
                month=month,
            )

        return usage

    def update_validation_usage(self, username: str, count: int):
        usage = self.get_or_create(username)
        usage.validation_requests += 1
        usage.validation_records += count

        self.db.add(usage)
        self.db.commit()

    def update_verification_usage(self, username: str, count: int):
        usage = self.get_or_create(username)
        usage.verification_requests += 1
        usage.verification_records += count

        self.db.add(usage)
        self.db.commit()
