import enum

from sqlalchemy import Column, ForeignKey, String, DateTime, Time, Date, BigInteger, Enum, Integer, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from .utils import todict


class GroupType(enum.Enum):
    reading = enum.auto()
    sleeping = enum.auto()

    def get_name(self):
        return self.name


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

    groups = relationship("ParticipationRelation", back_populates="user")


class Group(Base):
    __tablename__ = 'groups'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(64), unique=True, index=True)
    group_type = Column(Enum(GroupType), nullable=True)
    invite = Column(BigInteger, index=True, unique=True)
    channel_id = Column(BigInteger, nullable=True, unique=True, default=None)

    deposit = Column(Integer)
    rest_day_price_to_bank = Column(Integer)

    start_date = Column(Date)
    creation_datetime = Column(DateTime, server_default=func.now())

    admins = relationship("Administration", back_populates="group")
    participants = relationship("ParticipationRelation", back_populates="group")


class Report(Base):
    __tablename__ = 'reports'

    id = Column(BigInteger, primary_key=True, index=True)

    sender = Column(ForeignKey('users.id'), index=True)
    group = Column(ForeignKey('groups.id'), index=True)

    tg_msg_id = Column(Integer, index=True)
    approved = Column(Boolean, nullable=True, default=None)

    day = Column(Integer)
    sent_datetime = Column(DateTime, server_default=func.now(), index=True)


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(BigInteger, primary_key=True, index=True)

    fullname = Column(String)
    username = Column(String)

    registration_datetime = Column(DateTime, server_default=func.now())

    groups = relationship("Administration", back_populates="admin")


class Administration(Base):
    __tablename__ = 'administration_relation'

    group_id = Column(ForeignKey('groups.id'), primary_key=True, index=True)
    admin_id = Column(ForeignKey('admins.id'), primary_key=True, index=True)

    admin = relationship("Admin", back_populates="groups")
    group = relationship("Group", back_populates="admins")


class ParticipationRelation(Base):
    __tablename__ = 'participation_relation'

    user_id = Column(ForeignKey('users.id'), primary_key=True, index=True)
    group_id = Column(ForeignKey('groups.id'), primary_key=True, index=True)
    entered_datetime = Column(DateTime, server_default=func.now())

    participation_details = Column(Text, nullable=True)
    attempts_bought = Column(Integer, default=0)
    notification_time = Column(Time, nullable=True)  # Local time

    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="participants")


class KickedRelation(Base):
    __tablename__ = 'kicked_relation'

    user_id = Column(ForeignKey('users.id'), primary_key=True)
    group_id = Column(ForeignKey('groups.id'), primary_key=True)
    kick_datetime = Column(DateTime, server_default=func.now())
    kick_day = Column(Integer)
