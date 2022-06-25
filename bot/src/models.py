import enum

from sqlalchemy import Column, ForeignKey, String, DateTime, Time, Date, BigInteger, Enum, Integer
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from .utils import todict


class GroupType(enum.Enum):
    reading = enum.auto()
    sleeping = enum.auto()


class Base:
    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f"{self.__class__.__name__}({params})"


Base = declarative_base(cls=Base)


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)  # from Telegram

    fullname = Column(String)
    username = Column(String)

    registration_datetime = Column(DateTime, server_default=func.now())


class Group(Base):
    __tablename__ = 'groups'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(32), unique=True)
    group_type = Column(Enum(GroupType), nullable=True)
    invite = Column(BigInteger, index=True, unique=True)

    deposit = Column(Integer)

    start_date = Column(Date)
    creation_datetime = Column(DateTime, server_default=func.now())


class Report(Base):
    __tablename__ = 'reports'

    id = Column(BigInteger, primary_key=True, index=True)

    sender = Column(ForeignKey('users.id'), index=True)
    group = Column(ForeignKey('groups.id'), index=True)

    tg_msg_id = Column(Integer, index=True)

    day = Column(Integer)
    sent_datetime = Column(DateTime, server_default=func.now(), index=True)


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(BigInteger, primary_key=True, index=True)

    fullname = Column(String)
    username = Column(String)

    registration_datetime = Column(DateTime, server_default=func.now())


class Administration(Base):
    __tablename__ = 'administration_relation'

    group_id = Column(ForeignKey('groups.id'), primary_key=True, index=True)
    admin_id = Column(ForeignKey('admins.id'), primary_key=True, index=True)

    admin = relationship("Admin", back_populates="groups")
    group = relationship("Admin", back_populates="admins")


class ParticipationRelation(Base):
    __tablename__ = 'participation_relation'

    user_id = Column(ForeignKey('users.id'), primary_key=True, index=True)
    group_id = Column(ForeignKey('groups.id'), primary_key=True, index=True)
    entered_datetime = Column(DateTime, server_default=func.now())

    attempts_bought = Column(Integer, default=0)
    notification_time = Column(Time, nullable=True)  # Local time

    participant = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="participants")


class KickedRelation(Base):
    __tablename__ = 'kicked_relation'

    user_id = Column(ForeignKey('users.id'), primary_key=True)
    group_id = Column(ForeignKey('groups.id'), primary_key=True)
    kick_datetime = Column(DateTime, server_default=func.now())
    kick_day = Column(Integer)
