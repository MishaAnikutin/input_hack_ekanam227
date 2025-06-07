from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Базовые модели
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: Optional[str] = None


class TickerBase(BaseModel):
    ticker: str
    name: str


class UserTickerBase(BaseModel):
    user_id: int
    ticker_id: int


# Модели для создания объектов
class UserCreate(UserBase):
    pass


class TickerCreate(TickerBase):
    pass


class UserTickerCreate(UserTickerBase):
    pass


# Модели для чтения/вывода
class TickerOut(TickerBase):
    id: int

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True




class UserWithTickers(UserOut):
    tickers: List[TickerOut] = []


class TickerWithUsers(TickerOut):
    users: List[UserOut] = []


# Модели для операций
class AddTickerToUserRequest(BaseModel):
    telegram_id: int
    ticker_symbol: str


class RemoveTickerFromUserRequest(BaseModel):
    telegram_id: int
    ticker_symbol: str


class CreateTickerRequest(TickerBase):
    pass


class SearchTickersResponse(BaseModel):
    results: List[TickerOut]


class UserTickersResponse(BaseModel):
    user_id: int
    tickers: List[TickerOut]


class AllTickersResponse(BaseModel):
    count: int
    tickers: List[TickerOut]
