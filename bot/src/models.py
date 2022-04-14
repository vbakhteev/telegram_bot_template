from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from .utils import todict


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
