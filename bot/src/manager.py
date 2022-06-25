from typing import Optional

from sqlalchemy.orm import sessionmaker

from .models import User, Admin


class Manager:
    def __init__(self, engine):
        self.engine = engine
        self.SessionMaker = sessionmaker(bind=engine)

    def register_user(self, user_id: int, fullname: str, username: str):
        with self.SessionMaker() as session:
            user = User(id=user_id, fullname=fullname, username=username)

            session.add(user)
            session.commit()

    def is_user_registered(self, user_id: int) -> bool:
        with self.SessionMaker() as session:
            user = self._get_user(user_id, session)
            return user is not None

    def register_admin(self, admin_id: int, fullname: str, username: str):
        with self.SessionMaker() as session:
            admin = Admin(id=admin_id, fullname=fullname, username=username)

            session.add(admin)
            session.commit()

    def is_admin_registered(self, admin_id: int) -> bool:
        with self.SessionMaker() as session:
            admin = session.query(User).get(admin_id)
            return admin is not None

    def _get_user(self, user_id: int, session) -> Optional[User]:
        return session.query(User).get(user_id)
