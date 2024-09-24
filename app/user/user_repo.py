from sqlmodel import Session, select

from app.auth import hash_password
from app.settings_env import get_env_settings
from app.sqlmodels import User


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, username):
        return self.db.get(User, username)

    def create_user(self, user):
        hash = hash_password(user.password)
        extra_data = {"hash": hash}
        db_user = User.model_validate(user, update=extra_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def create_initial_user(self, env):
        user = self.db.exec(select(User)).first()
        if user is None:
            user = User(
                name=env.initial_user_name,
                email="user@example.com",
                hash=hash_password(env.initial_user_pass),
                is_admin=True
            )
            self.db.add(user)
            self.db.commit()
