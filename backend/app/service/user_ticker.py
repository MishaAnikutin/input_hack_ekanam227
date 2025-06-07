from typing import List

from repos import UserTickerRepository, CompanyRepository, UserRepository
from service.schemas import (
    RemoveTickerFromUserRequest,
    UserOut,
    UserTickersResponse,
    TickerOut,
    AddTickerToUserRequest, UserTickerBase,
)


class UserTickerService:
    def __init__(
        self,
        user_ticker_repo: UserTickerRepository,
        company_repo: CompanyRepository,
        user_repo: UserRepository,
    ):
        self.user_ticker_repo = user_ticker_repo
        self.company_repo = company_repo
        self.user_repo = user_repo

    async def add_ticker_to_user(
        self, request: AddTickerToUserRequest
    ) -> UserTickerBase:
        """Добавляет тикер в портфель пользователя"""
        user = await self.user_repo.get_user(request.telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")

        ticker = await self.company_repo.get_ticker_by_symbol(request.ticker_symbol)
        if not ticker:
            raise ValueError("Тикер не найден")

        if await self.user_ticker_repo.user_has_ticker(user.id, ticker.id):
            raise ValueError("Тикер уже в портфеле пользователя")

        association = await self.user_ticker_repo.add_ticker_to_user(user.id, ticker.id)
        return UserTickerBase.from_orm(association)

    async def get_user_tickers(self, telegram_id: int) -> UserTickersResponse:
        """Получает все тикеры пользователя"""
        user = await self.user_repo.get_user(telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")

        tickers = await self.user_ticker_repo.get_user_tickers(user.id)
        return UserTickersResponse(
            user_id=user.id, tickers=[TickerOut.from_orm(t) for t in tickers]
        )

    async def remove_ticker_from_user(
        self, telegram_id: int, ticker: str
    ) -> bool:
        """Удаляет тикер из портфеля пользователя"""
        user = await self.user_repo.get_user(telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")

        ticker = await self.company_repo.get_ticker_by_symbol(ticker)
        if not ticker:
            raise ValueError("Тикер не найден")

        return await self.user_ticker_repo.remove_ticker_from_user(user.id, ticker.id)

    async def get_ticker_subscribers(self, ticker_symbol: str) -> List[UserOut]:
        """Получает всех пользователей, подписанных на тикер"""
        ticker = await self.company_repo.get_ticker_by_symbol(ticker_symbol)
        if not ticker:
            raise ValueError("Тикер не найден")

        users = await self.user_ticker_repo.get_ticker_subscribers(ticker.id)
        return [UserOut.from_orm(u) for u in users]
