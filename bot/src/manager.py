import random
from datetime import date
from typing import Optional, List, Tuple

from sqlalchemy.orm import sessionmaker

from .models import User, Admin, Group, GroupType, Administration, Participation
from .utils import generate_invite


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
            admin = self._get_admin(
                admin_id=admin_id,
                session=session,
            )
            return admin is not None

    def get_admin_groups_names(self, admin_id: int) -> List[str]:
        with self.SessionMaker() as session:
            administrations: List[Administration] = session.query(Administration). \
                filter(Administration.admin_id == admin_id). \
                all()

            return [adm.group.name for adm in administrations]

    def get_user_groups(self, user_id: int) -> List[Group]:
        with self.SessionMaker() as session:
            participations: List[Participation] = session.query(Participation). \
                filter(Participation.admin_id == user_id). \
                all()

            return [p.group for p in participations]

    def is_admin_group(self, admin_id: int, group_name) -> Tuple[bool, Optional[int]]:
        with self.SessionMaker() as session:
            group: Optional[Group] = session.query(Group).filter(Group.name == group_name).first()
            if group is None:
                return False, None

            admins_of_group = [administration.admin_id for administration in group.admins]
            is_admin = admin_id in admins_of_group
            return is_admin, group.id

    def create_group(
            self,
            admin_id: int,
            group_type: GroupType,
            deposit: int,
            rest_day_price_to_bank: int,
            start_date: date,
            cities: List[Tuple[str, str]],
    ) -> Tuple[int, str, int]:
        with self.SessionMaker() as session:
            group_name = generate_new_name(cities, session)
            invite = generate_new_invite(session)

            group = Group(
                name=group_name,
                group_type=group_type,
                invite=invite,
                deposit=deposit,
                rest_day_price_to_bank=rest_day_price_to_bank,
                start_date=start_date,
            )
            session.add(group)
            session.commit()

            administration = Administration(
                admin_id=admin_id,
                group_id=group.id,
            )
            session.add(administration)
            session.commit()

            return group.id, group_name, invite

    def set_channel_id_by_name(
            self,
            channel_id: int,
            group_name: str,
    ) -> bool:
        with self.SessionMaker() as session:
            group: Optional[Group] = session.query(Group).filter(Group.name == group_name).first()

            if group is None:
                return False

            group.channel_id = channel_id
            session.commit()

            return True

    def is_channel_set(self, group_id: int) -> bool:
        with self.SessionMaker() as session:
            group = self._get_group(group_id=group_id, session=session)
            return group.channel_id is not None

    #########

    def _get_user(self, user_id: int, session) -> Optional[User]:
        return session.query(User).get(user_id)

    def _get_admin(self, admin_id: int, session) -> Optional[Admin]:
        return session.query(Admin).get(admin_id)

    def _get_group(self, group_id: int, session) -> Optional[Group]:
        return session.query(Group).get(group_id)


def generate_new_invite(session) -> int:
    for _ in range(20):
        invite = generate_invite()
        group = session.query(Group).filter(Group.invite == invite).first()
        if group is None:
            return invite

    return -1


def generate_new_name(cities: List[Tuple[str, str]], session) -> str:
    flag, city = random.choice(cities)

    n_cities_in_db = session.query(Group).filter(Group.name.contains(city)).count()

    name = f'{city} {flag * (n_cities_in_db + 1)}'
    return name
