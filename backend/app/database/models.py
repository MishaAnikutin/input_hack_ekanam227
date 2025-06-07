from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# К сожалению, связь портфеля тикеров и пользователей Many-to-Many.
# Однако количество пользователей будет небольшим,
# так что не критично
class UserTickerAssociation(Base):
    __tablename__ = "user_ticker_association"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    ticker_id = Column(Integer, ForeignKey("companies.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("UserModel", back_populates="ticker_associations")
    company = relationship("CompanyModel", back_populates="user_associations")


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    name = Column(String)

    ticker_associations = relationship(
        "UserTickerAssociation", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def tickers(self):
        return [assoc.company for assoc in self.ticker_associations]


class CompanyModel(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)

    user_associations = relationship(
        "UserTickerAssociation", back_populates="company", cascade="all, delete-orphan"
    )

    @property
    def users(self):
        return [assoc.user for assoc in self.user_associations]
