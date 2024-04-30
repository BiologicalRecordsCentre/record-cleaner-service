from sqlmodel import Session, select

from app.auth import hash_password
from app.settings import settings
from app.sqlmodels import User


class UserRepo:
    def __init__(self, session):
        self.session = session

    def get_user(self, username):
        return self.session.get(User, username)

    def create_user(self, user):
        hash = hash_password(user.password)
        extra_data = {"hash": hash}
        db_user = User.model_validate(user, update=extra_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def create_initial_user(self):
        user = self.session.exec(select(User)).first()
        if user is None:
            user = User(
                name=settings.env.initial_user_name,
                email="user@example.com",
                hash=hash_password(settings.env.initial_user_pass),
                is_admin=True
            )
            self.session.add(user)
            self.session.commit()
