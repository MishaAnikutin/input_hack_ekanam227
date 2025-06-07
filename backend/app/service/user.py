from repos import UserRepository
from .schemas import (
    UserCreate,
    UserOut,
    TickerOut,
    UserWithTickers,
)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def get_or_create_user(self, user_data: UserCreate) -> UserOut:
        """Создает или возвращает существующего пользователя"""
        user = await self.repo.get_or_create_user(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            name=user_data.name,
        )
        return UserOut.from_orm(user)

    async def get_user(self, telegram_id: int) -> UserOut:
        """Получает пользователя по telegram_id"""
        user = await self.repo.get_user(telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")
        return UserOut.from_orm(user)

    async def get_user_with_tickers(self, telegram_id: int) -> UserWithTickers:
        """Получает пользователя с его тикерами"""
        user = await self.repo.get_user(telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")

        return UserWithTickers(
            **UserOut.from_orm(user).dict(),
            tickers=[TickerOut.from_orm(t) for t in user.tickers]
        )
